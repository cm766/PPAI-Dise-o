from ..interfaz.GPSTracker import ServicioBolsinesTracker
from .XTR4500LAdapter import XTR4500LAdapter
from .XTR4500LTracker import XTR4500LTracker
from .NavTrackQX7AAdapter import NavTrackQX7AAdapter
from .NavTrackQX7ATracker import NavTrackQX7ATracker
from .GeoPulseMTR900Adapter import GeoPulseMTR900Adapter
from .GeoPulseMTR900Tracker import GeoPulseMTR900Tracker

# API Keys identificatorias de cada servicio (simuladas)
API_KEY_XTR4500L = "KEY_XTR_123"
API_KEY_NAVTRACK = "KEY_NAVTRACK_456"
API_KEY_GEOPULSE = "KEY_GEOPULSE_789"


# PATRÓN ADAPTER: fábrica que selecciona un Adapter sin exponerlo al cliente.
def crear_servicio_bolsines_tracker(fabricante: str) -> ServicioBolsinesTracker:
    if fabricante == "XTR4500L":
        return XTR4500LAdapter(XTR4500LTracker(), API_KEY_XTR4500L)
    if fabricante == "NavTrackQX7A":
        return NavTrackQX7AAdapter(NavTrackQX7ATracker(), API_KEY_NAVTRACK)
    if fabricante == "GeoPulseMTR900":
        return GeoPulseMTR900Adapter(GeoPulseMTR900Tracker(), API_KEY_GEOPULSE)
    raise ValueError(f"Fabricante de tracker no soportado: {fabricante}")
