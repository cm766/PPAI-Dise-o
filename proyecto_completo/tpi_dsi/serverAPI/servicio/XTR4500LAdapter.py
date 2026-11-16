from ..interfaz.GPSTracker import (
    ServicioBolsinesTracker,
    UbicacionBolsin,
    UbicacionNoDisponibleError,
)
from .XTR4500LTracker import XTR4500LTracker
from .tracker_adapter_utils import crear_ubicacion


# PATRÓN ADAPTER: Adapter que traduce el formato XTR4500L al Target común.
class XTR4500LAdapter(ServicioBolsinesTracker):
    def __init__(self, adaptee: XTR4500LTracker):
        self.adaptee = adaptee

    def obtener_ubicacion(self, numero_bolsin: int) -> UbicacionBolsin:
        try:
            datos = self.adaptee.consultar_posicion(numero_bolsin)
            return crear_ubicacion(
                datos["latitude_deg"],
                datos["longitude_deg"],
                datos["recorded_at"],
            )
        except (KeyError, TypeError, ValueError, OverflowError, TimeoutError) as error:
            raise UbicacionNoDisponibleError(
                f"No hay ubicación disponible para el bolsín #{numero_bolsin}"
            ) from error
