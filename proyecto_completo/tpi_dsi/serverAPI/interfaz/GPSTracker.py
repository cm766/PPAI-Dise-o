from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


# PATRÓN ADAPTER: tipo común de ubicación que reciben los clientes.
# Según el CU 36, para todos los modelos se recupera número de bolsín,
# latitud, longitud y fecha y hora de la última actualización.
@dataclass(frozen=True)
class UbicacionBolsin:
    numero_bolsin: int
    latitud: float
    longitud: float
    ultima_actualizacion: datetime


# PATRÓN ADAPTER: contrato común para indicar que no hay ubicación disponible.
class UbicacionNoDisponibleError(Exception):
    pass


# PATRÓN ADAPTER: Target; define la operación que usan los clientes.
# Reemplaza a la «interfaz» GPSTracker del análisis.
class ServicioBolsinesTracker(ABC):

    @abstractmethod
    def obtener_ubicacion(self, bolsin) -> UbicacionBolsin:
        pass
