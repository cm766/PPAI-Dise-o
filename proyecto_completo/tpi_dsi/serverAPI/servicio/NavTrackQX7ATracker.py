from datetime import datetime

from .coordenadas_simuladas import COORDENADAS_SIMULADAS


# PATRÓN ADAPTER: Adaptee NavTrack QX-7A, con la operación y el formato propios del fabricante.
# CU 36, Observación 1: retrieveTrackingData() recibe una API Key, el número de bolsín (entero)
# y el código de la CM destino (String). Devuelve un único String con sus ítems separados
# por comas: número de bolsín, latitud, longitud y fecha y hora del último reporte.
class NavTrackQX7ATracker:

    def retrieveTrackingData(self, apiKey: str, nroBolsin: int, codigoCMDestino: str) -> str:
        posicion = COORDENADAS_SIMULADAS.get(nroBolsin)
        if posicion is None:
            return ""

        latitud, longitud = posicion
        return f"{nroBolsin},{latitud},{longitud},{datetime.now().isoformat()}"


# Servicio externo del fabricante: ya existe, el sistema no lo crea.
# Los adaptadores solo guardan una referencia (puntero) a este objeto para hacerle peticiones.
servicio_navtrack_qx7a = NavTrackQX7ATracker()
