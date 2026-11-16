from datetime import datetime
from typing import Dict, Optional


# PATRÓN ADAPTER: Adaptee GeoTrack, entrega las coordenadas como texto y en otro orden.
class GeoTrackAdaptee:
    _coordenadas = {
        1: (-31.4201, -64.1888),
        2: (-32.9468, -60.6393),
        3: (-31.4135, -63.2497),
        4: (-31.5375, -68.5234),
        5: (-32.4833, -58.2278),
        6: (-31.2497, -61.4917),
        65: (-34.6037, -58.3816),
    }

    def leer_coordenadas(self, numero_bolsin: int) -> Optional[str]:
        posicion = self._coordenadas.get(numero_bolsin)
        if posicion is None:
            return ""

        latitud, longitud = posicion
        return f"{datetime.now().isoformat()}|{longitud}|{latitud}"
