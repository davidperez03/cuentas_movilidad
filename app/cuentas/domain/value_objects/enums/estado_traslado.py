from enum import Enum
from typing import List


class EstadoTraslado(Enum):
    """Estados específicos del proceso de traslado"""
    ENVIADO_ORGANISMO_DESTINO = "enviado_organismo_destino"
    REVISADO = "revisado"
    CON_NOVEDADES = "con_novedades"
    TRASLADADO = "trasladado"
    DEVUELTO = "devuelto"
    
    def puede_transicionar_a(self, nuevo_estado: 'EstadoTraslado', es_admin: bool = False) -> bool:
        if es_admin and nuevo_estado == EstadoTraslado.DEVUELTO:
            return True
        
        return nuevo_estado in self._get_transiciones_permitidas()
    
    def _get_transiciones_permitidas(self) -> List['EstadoTraslado']:
        transiciones = {
            EstadoTraslado.ENVIADO_ORGANISMO_DESTINO: [EstadoTraslado.REVISADO],
            EstadoTraslado.REVISADO: [EstadoTraslado.TRASLADADO, EstadoTraslado.CON_NOVEDADES],
            EstadoTraslado.CON_NOVEDADES: [EstadoTraslado.REVISADO],
            EstadoTraslado.TRASLADADO: [], 
            EstadoTraslado.DEVUELTO: []  
        }
        return transiciones.get(self, [])
    
    def es_estado_final(self) -> bool:
        return self in [EstadoTraslado.TRASLADADO, EstadoTraslado.DEVUELTO]