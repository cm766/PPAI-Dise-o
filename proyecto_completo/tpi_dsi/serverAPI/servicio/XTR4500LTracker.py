#PATRÓN GRASP APLICADO: Bajo acoplamiento
from typing import Any, Dict
from datetime import datetime


# PATRÓN ADAPTER: Adaptee XTR4500L, con formato y operación propios del fabricante.
class XTR4500LTracker:
    _coordenadas = {
        1: {"lat": -31.4201, "lng": -64.1888},
        2: {"lat": -32.9468, "lng": -60.6393},
        3: {"lat": -31.4135, "lng": -63.2497},
        4: {"lat": -31.5375, "lng": -68.5234},
        5: {"lat": -32.4833, "lng": -58.2278},
        6: {"lat": -31.2497, "lng": -61.4917},
        65: {"lat": -34.6037, "lng": -58.3816},
    }

    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    def consultar_posicion(self, numero_bolsin: int) -> Dict[str, Any]:
        pos = self._coordenadas.get(numero_bolsin)
        if pos is None:
            raise TimeoutError(
                f"GPS Tracker XTR-4500L agotó el tiempo de espera para el bolsín #{numero_bolsin}"
            )

        return {
            "latitude_deg": pos["lat"],
            "longitude_deg": pos["lng"],
            "recorded_at": datetime.now().isoformat(),
        }

    def obtener_ubicacion(self, numero_bolsin: int) -> Dict[str, Any]:
        # Compatibilidad temporal con views.py hasta que Bloque 1 migre al Target.
        posicion = self.consultar_posicion(numero_bolsin)
        return {
            "numero_bolsin": numero_bolsin,
            "latitud": float(posicion["latitude_deg"]),
            "longitud": float(posicion["longitude_deg"]),
            "ultima_actualizacion": posicion["recorded_at"],
        }
