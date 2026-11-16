from datetime import datetime
from typing import List

from .coordenadas_simuladas import COORDENADAS_SIMULADAS


# PATRÓN ADAPTER: Adaptee GeoPulse MTR-900, con la operación y el formato propios del fabricante.
# CU 36, Observación 1: fetchCargoPositions() recibe una API Key y el número de bolsín (entero).
# Devuelve una matriz con el número de bolsín, la latitud, la longitud y la fecha y hora
# de la última actualización de posición.
class GeoPulseMTR900Tracker:

    def fetchCargoPositions(self, apiKey: str, nroBolsin: int) -> List[List[str]]:
        posicion = COORDENADAS_SIMULADAS.get(nroBolsin)
        if posicion is None:
            return []

        latitud, longitud = posicion
        return [[str(nroBolsin), str(latitud), str(longitud), datetime.now().isoformat()]]
