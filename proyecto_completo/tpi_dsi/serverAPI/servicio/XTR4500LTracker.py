#PATRÓN GRASP APLICADO: Bajo acoplamiento
import json
from datetime import datetime

from .coordenadas_simuladas import COORDENADAS_SIMULADAS


# PATRÓN ADAPTER: Adaptee XTR-4500L, con la operación y el formato propios del fabricante.
# CU 36, Observación 1: getBolsinLocation() recibe una API Key, el número de bolsín (entero)
# y el código de la CM origen (String). Devuelve un JSON en formato cadena de caracteres
# con el número de bolsín, la latitud, la longitud y la fecha y hora de la última actualización.
class XTR4500LTracker:

    def getBolsinLocation(self, apiKey: str, nroBolsin: int, codigoCMOrigen: str) -> str:
        posicion = COORDENADAS_SIMULADAS.get(nroBolsin)
        if posicion is None:
            raise TimeoutError(
                f"GPS Tracker XTR-4500L agotó el tiempo de espera para el bolsín #{nroBolsin}"
            )

        latitud, longitud = posicion
        return json.dumps([{
            "bolsin": nroBolsin,
            "lat": latitud,
            "lng": longitud,
            "lastUpdate": datetime.now().isoformat(),
        }])


# Servicio externo del fabricante: ya existe, el sistema no lo crea.
# Los adaptadores solo guardan una referencia (puntero) a este objeto para hacerle peticiones.
servicio_xtr4500l = XTR4500LTracker()
