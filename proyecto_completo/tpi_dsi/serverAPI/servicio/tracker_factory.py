from ..interfaz.GPSTracker import ServicioBolsinesTracker
from .GeoTrackAdapter import GeoTrackAdapter
from .GeoTrackAdaptee import GeoTrackAdaptee
from .XTR4500LAdapter import XTR4500LAdapter
from .XTR4500LTracker import XTR4500LTracker


# PATRÓN ADAPTER: fábrica que selecciona un Adapter sin exponerlo al cliente.
def crear_servicio_bolsines_tracker(fabricante: str) -> ServicioBolsinesTracker:
    if fabricante == "XTR4500L":
        return XTR4500LAdapter(XTR4500LTracker())
    if fabricante == "GeoTrack":
        return GeoTrackAdapter(GeoTrackAdaptee())
    raise ValueError(f"Fabricante de tracker no soportado: {fabricante}")
