from ..models import Bolsin, Empleado, Sesion
from ..interfaz.GPSTracker import ServicioBolsinesTracker, UbicacionNoDisponibleError
from ..servicio.XTR4500LAdapter import XTR4500LAdapter
from ..servicio.NavTrackQX7AAdapter import NavTrackQX7AAdapter
from ..servicio.GeoPulseMTR900Adapter import GeoPulseMTR900Adapter
from ..servicio.googleMap import GoogleMap

# API Keys identificatorias de cada servicio de GPS Tracker (simuladas)
API_KEY_XTR4500L = "KEY_XTR_123"
API_KEY_NAVTRACK = "KEY_NAVTRACK_456"
API_KEY_GEOPULSE = "KEY_GEOPULSE_789"


# PATRÓN ADAPTER: GestorBuscarBolsin cumple el rol de Cliente.
# Crea el Adapter que corresponde al modelo de GPS Tracker de cada bolsín (crearAdaptador)
# y después pide la ubicación siempre a través de la interfaz común (Target),
# sin saber qué adaptador concreto le tocó.
class GestorBuscarBolsin:

    def __init__(self, usuario_autenticado):
        self.usuario_autenticado = usuario_autenticado
        self.cm_origen = None
        self.bolsines_enviados = []
        self.ubicaciones = {}              # {numeroBolsin: UbicacionBolsin}
        self.bolsines_sin_ubicacion = []   # A3: números de bolsín sin ubicación
        self.mapa = None
        self.bolsin_seleccionado = None
        self.confirmacion_envio_correo = False

    def nuevaBusquedaBolsin(self):
        self.cm_origen = self.buscarCMUsuarioLog()
        self.bolsines_enviados = self.buscarBolsinesEnviados()
        # A1: si no hay bolsines enviados, no se consulta ningún GPS Tracker
        if self.bolsines_enviados:
            self.obtenerUbicaciones()
        self.mapa = GoogleMap().getMapa()

    def buscarCMUsuarioLog(self):
        sesion = Sesion.objects.filter(
            usuario__user=self.usuario_autenticado
        ).latest('id')
        return sesion.buscarUsuarioLog().obtenerEmpleado().getCM().getNombre()

    def buscarBolsinesEnviados(self):
        return [
            b for b in Bolsin.objects.all()
            if b.sosEnviado() and b.esTuCMOrigen(self.cm_origen)
        ]

    def obtenerUbicaciones(self):
        for bolsin in self.bolsines_enviados:
            numero = bolsin.getNumeroBolsin()
            try:
                modelo_tracker = bolsin.getModeloTracker()
                servicio_tracker = self.crearAdaptador(modelo_tracker)
                # Llamada polimórfica: el gestor siempre usa la misma operación del Target
                self.ubicaciones[numero] = servicio_tracker.obtener_ubicacion(bolsin)
            except UbicacionNoDisponibleError:
                # A3: el GPS Tracker no pudo informar la ubicación del bolsín
                self.bolsines_sin_ubicacion.append(numero)
            except ValueError as error:
                # Modelo de GPS Tracker sin Adapter implementado
                print(f"Error al obtener GPS: {error}")
                self.bolsines_sin_ubicacion.append(numero)

    def crearAdaptador(self, modelo_tracker: str) -> ServicioBolsinesTracker:
        # Según el modelo de GPS Tracker del bolsín, se crea el Adapter concreto.
        # El resto del gestor lo usa como ServicioBolsinesTracker.
        if modelo_tracker == "XTR4500L":
            return XTR4500LAdapter(API_KEY_XTR4500L)
        if modelo_tracker == "NavTrackQX7A":
            return NavTrackQX7AAdapter(API_KEY_NAVTRACK)
        if modelo_tracker == "GeoPulseMTR900":
            return GeoPulseMTR900Adapter(API_KEY_GEOPULSE)
        raise ValueError(f"Modelo de GPS Tracker no soportado: {modelo_tracker}")

    def tomarSeleccionBolsin(self, numero_bolsin):
        self.bolsin_seleccionado = Bolsin.objects.filter(numeroBolsin=numero_bolsin).first()
        return self.bolsin_seleccionado

    def tomarConfEnvioCorreo(self, confirmacion, lat, lng, fecha):
        self.confirmacion_envio_correo = confirmacion
        # A5: el EB no confirma el envío del correo
        if not confirmacion or self.bolsin_seleccionado is None:
            self.finCU()
            return None

        email_gcm = self.buscarEmailGCM()
        resultado = self.llamarCUNotificarUbicacionDeBolsin(email_gcm, lat, lng, fecha)
        self.finCU()
        return resultado

    def buscarEmailGCM(self):
        cm_destino = self.bolsin_seleccionado.getCMDestino()
        emails = [
            e.getEmail()
            for e in Empleado.objects.filter(asignadoA=cm_destino)
            if e.sosGerenteCM()
        ]
        return emails[0] if emails else 'sin@email.com'

    def llamarCUNotificarUbicacionDeBolsin(self, email_gcm, lat, lng, fecha):
        # <<include>> CU 31 Notificar ubicación de bolsín
        return {
            'status': 'success',
            'message': 'Notificación enviada correctamente',
            'emailGcm': email_gcm,
            'numeroBolsin': self.bolsin_seleccionado.getNumeroBolsin(),
            'coordenadas': {'lat': float(lat), 'lng': float(lng)},
            'fechaHora': fecha,
        }

    def finCU(self):
        self.bolsin_seleccionado = None
        self.confirmacion_envio_correo = False
