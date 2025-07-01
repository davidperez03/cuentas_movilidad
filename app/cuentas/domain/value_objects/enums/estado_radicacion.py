from enum import Enum
from typing import List


class EstadoRadicacion(Enum):
    PENDIENTE_RADICAR = "pendiente_radicar"
    RECIBIDO = "recibido"
    REVISADO = "revisado"
    CON_NOVEDADES = "con_novedades" 
    RADICADO = "radicado"
    DEVUELTO = "devuelto"
    
    def puede_transicionar_a(self, nuevo_estado: 'EstadoRadicacion', es_admin: bool = False) -> bool:
        # Admin puede hacer devoluciones desde cualquier estado
        if es_admin and nuevo_estado == EstadoRadicacion.DEVUELTO:
            return True
        
        return nuevo_estado in self._get_transiciones_permitidas()
    
    def _get_transiciones_permitidas(self) -> List['EstadoRadicacion']:
        transiciones = {
            EstadoRadicacion.PENDIENTE_RADICAR: [EstadoRadicacion.RECIBIDO],
            EstadoRadicacion.RECIBIDO: [EstadoRadicacion.REVISADO],
            EstadoRadicacion.REVISADO: [EstadoRadicacion.RADICADO, EstadoRadicacion.CON_NOVEDADES],
            EstadoRadicacion.CON_NOVEDADES: [EstadoRadicacion.REVISADO],
            EstadoRadicacion.RADICADO: [], 
            EstadoRadicacion.DEVUELTO: [] 
        }
        return transiciones.get(self, [])
    
    def es_estado_final(self) -> bool:
        return self in [EstadoRadicacion.RADICADO, EstadoRadicacion.DEVUELTO]