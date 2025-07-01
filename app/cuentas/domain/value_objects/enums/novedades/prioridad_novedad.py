from enum import Enum


class PrioridadNovedad(Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"
    
    def es_mayor_que(self, otra_prioridad: 'PrioridadNovedad') -> bool:
        orden = {
            PrioridadNovedad.BAJA: 1,
            PrioridadNovedad.MEDIA: 2,
            PrioridadNovedad.ALTA: 3,
            PrioridadNovedad.CRITICA: 4
        }
        return orden[self] > orden[otra_prioridad]
    
    def es_critica_o_alta(self) -> bool:
        return self in [PrioridadNovedad.ALTA, PrioridadNovedad.CRITICA]