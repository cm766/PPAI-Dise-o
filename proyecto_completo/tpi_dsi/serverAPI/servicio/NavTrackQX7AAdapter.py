from ..interfaz.GPSTracker import (
    ServicioBolsinesTracker,
    UbicacionBolsin,
    UbicacionNoDisponibleError,
)
from .NavTrackQX7ATracker import NavTrackQX7ATracker
from .tracker_adapter_utils import crear_ubicacion


# PATRÓN ADAPTER: Adapter que traduce el formato NavTrack QX-7A (String separado por comas)
# al Target común.
class NavTrackQX7AAdapter(ServicioBolsinesTracker):
    def __init__(self, adaptee: NavTrackQX7ATracker, api_key: str):
        self.adaptee = adaptee
        self.api_key = api_key

    def obtener_ubicacion(self, bolsin) -> UbicacionBolsin:
        numero_bolsin = bolsin.getNumeroBolsin()
        try:
            codigo_cm_destino = bolsin.getCMDestino().getCodigo()
            datos = self.adaptee.retrieveTrackingData(
                self.api_key, numero_bolsin, codigo_cm_destino
            )
            if not datos:
                raise ValueError("NavTrack QX-7A devolvió una respuesta vacía")

            numero, latitud, longitud, fecha_hora = datos.split(",")
            return crear_ubicacion(numero, latitud, longitud, fecha_hora)
        except (TypeError, ValueError, OverflowError) as error:
            raise UbicacionNoDisponibleError(
                f"No hay ubicación disponible para el bolsín #{numero_bolsin}"
            ) from error
