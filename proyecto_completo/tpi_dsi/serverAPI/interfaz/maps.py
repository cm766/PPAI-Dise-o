from abc import ABC, abstractmethod
from typing import Dict, List, Any

class ServicioMaps(ABC):
  @abstractmethod
  def url_maps(self) -> str:
    '''
    para retornar la url base '''
    
    @abstractmethod
    def mapear_a_marcador(self, bolsin: Any) -> Dict[str, Any]:
      pass
      
      ''' transforma un objeto Bolsín en formato 
      marcador que necesita el proveedor'''
      