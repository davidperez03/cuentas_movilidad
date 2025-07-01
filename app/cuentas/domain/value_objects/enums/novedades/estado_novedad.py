# app/cuentas/domain/enums/novedades/estado_novedad.py
from enum import Enum
from typing import List


class EstadoNovedad(Enum):
    PENDIENTE = "pendiente"
    EN_REVISION = "en_revision"
    RESUELTA = "resuelta"
    REABIERTA = "reabierta"
    
    def _get_transiciones_permitidas(self) -> List['EstadoNovedad']:
        transiciones = {
            EstadoNovedad.PENDIENTE: [EstadoNovedad.EN_REVISION, EstadoNovedad.RESUELTA],
            EstadoNovedad.EN_REVISION: [EstadoNovedad.RESUELTA, EstadoNovedad.PENDIENTE],
            EstadoNovedad.RESUELTA: [EstadoNovedad.REABIERTA],
            EstadoNovedad.REABIERTA: [EstadoNovedad.EN_REVISION, EstadoNovedad.RESUELTA]
        }
        return transiciones.get(self, [])
    
    def puede_transicionar_a(self, nuevo_estado: 'EstadoNovedad') -> bool:
        return nuevo_estado in self._get_transiciones_permitidas()
    
    def es_estado_final(self) -> bool:
        return self == EstadoNovedad.RESUELTA
    
    def requiere_accion(self) -> bool:
        return self in [EstadoNovedad.PENDIENTE, EstadoNovedad.REABIERTA]