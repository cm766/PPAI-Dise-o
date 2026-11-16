from ..interfaz.GPSTracker import (
    ServicioBolsinesTracker,
    UbicacionBolsin,
    UbicacionNoDisponibleError,
)
from .GeoTrackAdaptee import GeoTrackAdaptee
from .tracker_adapter_utils import crear_ubicacion


# PATRÓN ADAPTER: Adapter que traduce el formato GeoTrack al Target común.
class GeoTrackAdapter(ServicioBolsinesTracker):
    def __init__(self, adaptee: GeoTrackAdaptee):
        self.adaptee = adaptee

    def obtener_ubicacion(self, numero_bolsin: int) -> UbicacionBolsin:
        try:
            datos = self.adaptee.leer_coordenadas(numero_bolsin)
            if not datos:
                raise ValueError("GeoTrack devolvió una respuesta vacía")

            fecha_hora, longitud, latitud = datos.split("|")
            return crear_ubicacion(latitud, longitud, fecha_hora)
        except (TypeError, ValueError, OverflowError) as error:
            raise UbicacionNoDisponibleError(
                f"No hay ubicación disponible para el bolsín #{numero_bolsin}"
            ) from error
