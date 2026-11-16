from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


# PATRÓN ADAPTER: tipo común de ubicación que reciben los clientes.
@dataclass(frozen=True)
class UbicacionBolsin:
    latitud: float
    longitud: float
    ultima_actualizacion: datetime


# PATRÓN ADAPTER: contrato común para indicar que no hay ubicación disponible.
class UbicacionNoDisponibleError(Exception):
    pass


# PATRÓN ADAPTER: Target; define la operación que usan los clientes.
class ServicioBolsinesTracker(ABC):

    @abstractmethod
    def obtener_ubicacion(self, numero_bolsin: int) -> UbicacionBolsin:
        pass