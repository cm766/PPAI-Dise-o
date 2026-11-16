from ..interfaz.GPSTracker import (
    ServicioBolsinesTracker,
    UbicacionBolsin,
    UbicacionNoDisponibleError,
)
from .GeoPulseMTR900Tracker import GeoPulseMTR900Tracker
from .tracker_adapter_utils import crear_ubicacion


# PATRÓN ADAPTER: Adapter que traduce el formato GeoPulse MTR-900 (matriz) al Target común.
class GeoPulseMTR900Adapter(ServicioBolsinesTracker):
    def __init__(self, adaptee: GeoPulseMTR900Tracker, api_key: str):
        self.adaptee = adaptee
        self.api_key = api_key

    def obtener_ubicacion(self, bolsin) -> UbicacionBolsin:
        numero_bolsin = bolsin.getNumeroBolsin()
        try:
            matriz = self.adaptee.fetchCargoPositions(self.api_key, numero_bolsin)
            if not matriz:
                raise ValueError("GeoPulse MTR-900 devolvió una matriz vacía")

            numero, latitud, longitud, fecha_hora = matriz[0]
            return crear_ubicacion(numero, latitud, longitud, fecha_hora)
        except (IndexError, TypeError, ValueError, OverflowError) as error:
            raise UbicacionNoDisponibleError(
                f"No hay ubicación disponible para el bolsín #{numero_bolsin}"
            ) from error
