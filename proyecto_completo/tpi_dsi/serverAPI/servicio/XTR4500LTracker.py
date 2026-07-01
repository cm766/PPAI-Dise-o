#PATRÓN GRASP APLICADO: Bajo acoplamiento
from ..interfaz.GPSTracker import ServicioBolsinesTracker
import json
from datetime import datetime

class XTR4500LTracker(ServicioBolsinesTracker):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def obtener_ubicacion(self, numero_bolsin: int, **kwargs) -> dict:
        # Simulamos datos basados en el número de bolsín
        coordenadas = {
            1: {"lat": -31.4201, "lng": -64.1888},  # Córdoba
            2: {"lat": -32.9468, "lng": -60.6393},  # Rosario
            3: {"lat": -31.4135, "lng": -63.2497},  # Villa María
            4: {"lat": -31.5375, "lng": -68.5234},  # San Juan
            5: {"lat": -32.4833, "lng": -58.2278},  # Concepción del Uruguay
            6: {"lat": -31.2497, "lng": -61.4917},  # Rafaela
            65: {"lat": -34.6037, "lng": -58.3816}  # Buenos Aires
        }
        pos = coordenadas.get(numero_bolsin)
        if pos is None:
            raise Exception(f"GPS Tracker XTR-4500L no pudo localizar el bolsín #{numero_bolsin}")
        
        # Fecha dinámica simulada
        fecha_actual = datetime.now().isoformat()
        
        return {
            "numero_bolsin": numero_bolsin,
            "latitud": float(pos["lat"]),
            "longitud": float(pos["lng"]),
            "ultima_actualizacion": fecha_actual
        }
