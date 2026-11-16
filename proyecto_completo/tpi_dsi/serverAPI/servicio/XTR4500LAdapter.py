import json

from ..interfaz.GPSTracker import (
    ServicioBolsinesTracker,
    UbicacionBolsin,
    UbicacionNoDisponibleError,
)
from .XTR4500LTracker import XTR4500LTracker
from .tracker_adapter_utils import crear_ubicacion


# PATRÓN ADAPTER: Adapter que traduce el formato XTR-4500L (JSON en String) al Target común.
class XTR4500LAdapter(ServicioBolsinesTracker):
    def __init__(self, adaptee: XTR4500LTracker, api_key: str):
        self.adaptee = adaptee
        self.api_key = api_key

    def obtener_ubicacion(self, bolsin) -> UbicacionBolsin:
        numero_bolsin = bolsin.getNumeroBolsin()
        try:
            codigo_cm_origen = bolsin.getCMOrigen().getCodigo()
            respuesta = self.adaptee.getBolsinLocation(
                self.api_key, numero_bolsin, codigo_cm_origen
            )
            item = json.loads(respuesta)[0]
            return crear_ubicacion(
                item["bolsin"],
                item["lat"],
                item["lng"],
                item["lastUpdate"],
            )
        except (KeyError, IndexError, TypeError, ValueError, OverflowError, TimeoutError) as error:
            raise UbicacionNoDisponibleError(
                f"No hay ubicación disponible para el bolsín #{numero_bolsin}"
            ) from error
