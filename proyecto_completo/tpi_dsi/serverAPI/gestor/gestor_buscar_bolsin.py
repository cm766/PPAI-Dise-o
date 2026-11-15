from ..models import Bolsin, Empleado, Sesion
from ..servicio.XTR4500LTracker import XTR4500LTracker
from ..servicio.googleMap import GoogleMap


class GestorBuscarBolsin:

    def __init__(self, usuario_autenticado):
        self.usuario_autenticado = usuario_autenticado
        self.cm_origen = None
        self.bolsines_enviados = []
        self.ubicaciones = {}      # {numeroBolsin: datos_gps}
        self.mapa = None

    def nuevaBusquedaBolsin(self):
        self.cm_origen = self.buscarCMUsuarioLog()
        self.bolsines_enviados = self.buscarBolsinesEnviados()
        self.obtenerUbicaciones()
        self.mapa = GoogleMap().getMapa()

    def buscarCMUsuarioLog(self):
        sesion = Sesion.objects.filter(
            usuario__user=self.usuario_autenticado
        ).latest('id')
        return sesion.usuario.obtenerEmpleado().getCM().getNombre()

    def buscarBolsinesEnviados(self):
        return [
            b for b in Bolsin.objects.all()
            if b.sosEnviado() and b.esTuCMOrigen(self.cm_origen)
        ]

    def obtenerUbicaciones(self):
        tracker = XTR4500LTracker("KEY_XTR_123")
        for b in self.bolsines_enviados:
            try:
                self.ubicaciones[b.getNumeroBolsin()] = tracker.obtener_ubicacion(
                    b.getNumeroBolsin()
                )
            except Exception as e:
                print(f"Error al obtener GPS: {e}")

    def buscarEmailGCM(self, numero_bolsin):
        bolsin = Bolsin.objects.filter(numeroBolsin=numero_bolsin).first()
        if bolsin is None:
            return None
        cm_destino = bolsin.getCMDestino()
        emails = [
            e.getEmail()
            for e in Empleado.objects.filter(asignadoA=cm_destino)
            if e.sosGerenteCM()
        ]
        return emails[0] if emails else 'sin@email.com'

    def notificarUbicacionDelBolsin(self, numero_bolsin, lat, lng, fecha):
        """
        Busca el bolsín, resuelve el email del gerente de la CM destino
        y arma la respuesta de notificación. Devuelve None si el bolsín
        no existe, para que la vista decida el 404.
        """
        bolsin = Bolsin.objects.filter(numeroBolsin=numero_bolsin).first()
        if bolsin is None:
            return None

        email_final = self.buscarEmailGCM(numero_bolsin)

        return {
            'status': 'success',
            'message': 'Notificación enviada correctamente',
            'emailGcm': email_final,
            'numeroBolsin': numero_bolsin,
            'coordenadas': {'lat': float(lat), 'lng': float(lng)},
            'fechaHora': fecha,
        }