from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ServicioBolsinesTracker(ABC):
    
    @abstractmethod
    def obtener_ubicacion(self, numero_bolsin: int, **kwargs) -> Dict[str, Any]:
        """
        Debe retornar:
        {
            "numero_bolsin": int,
            "latitud": float,
            "longitud": float,
            "ultima_actualizacion": str
        }
        """
        pass