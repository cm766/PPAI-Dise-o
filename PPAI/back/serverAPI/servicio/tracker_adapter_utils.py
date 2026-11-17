import math
from datetime import datetime

from ..interfaz.GPSTracker import UbicacionBolsin


# PATRÓN ADAPTER: normaliza y valida datos antes de crear el formato común.
def crear_ubicacion(numero_bolsin, latitud, longitud, ultima_actualizacion):
    numero_bolsin = int(numero_bolsin)
    latitud = float(latitud)
    longitud = float(longitud)
    if not math.isfinite(latitud) or not -90 <= latitud <= 90:
        raise ValueError("Latitud inválida")
    if not math.isfinite(longitud) or not -180 <= longitud <= 180:
        raise ValueError("Longitud inválida")
    if isinstance(ultima_actualizacion, datetime):
        fecha_hora = ultima_actualizacion
    else:
        fecha_hora = datetime.fromisoformat(ultima_actualizacion)

    return UbicacionBolsin(
        numero_bolsin=numero_bolsin,
        latitud=latitud,
        longitud=longitud,
        ultima_actualizacion=fecha_hora,
    )
