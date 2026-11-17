''' acoplo las especificaciones de google'''

from django.conf import settings
from abc import ABC, abstractmethod

class ServidorGoogleMap(ABC):
  def _init_(self):
    self .api_key = gettr(settings, 'GOOGLE_MAPS_KEY', 'API_KEY_DEFECTO')
    
    
  def generar_url(self) -> dict:
    'hacemos adaptar eol formato'
    return {
      'id': bolsin.id,
      'position':{
        'lat': gblsin.latitud,
        'lng': bolsin.longitud
      },
      'title': str(bolsin.id),
      'info': "Ubicación del envío"
    }

  def getMapa(self) -> dict:
    """
    Obtiene el mapa
    """
    pass