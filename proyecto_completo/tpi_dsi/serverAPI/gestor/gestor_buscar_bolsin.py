from ..models import Bolsin, Empleado, Sesion
from ..interfaz.GPSTracker import UbicacionNoDisponibleError
from ..servicio.tracker_factory import crear_servicio_bolsines_tracker
from ..servicio.googleMap import GoogleMap


# PATRÓN ADAPTER: GestorBuscarBolsin cumple el rol de Cliente.
# Pide la ubicación de cada bolsín a través de la interfaz común (Target),
# sin conocer qué modelo de GPS Tracker hay detrás.
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
                # La fábrica devuelve el Adapter que corresponde al modelo de GPS del bolsín
                servicio_tracker = crear_servicio_bolsines_tracker(bolsin.getModeloTracker())
                # Llamada polimórfica: el gestor siempre usa la misma operación del Target
                self.ubicaciones[numero] = servicio_tracker.obtener_ubicacion(bolsin)
            except UbicacionNoDisponibleError:
                # A3: el GPS Tracker no pudo informar la ubicación del bolsín
                self.bolsines_sin_ubicacion.append(numero)
            except ValueError as error:
                # Modelo de GPS Tracker sin Adapter implementado
                print(f"Error al obtener GPS: {error}")
                self.bolsines_sin_ubicacion.append(numero)

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
