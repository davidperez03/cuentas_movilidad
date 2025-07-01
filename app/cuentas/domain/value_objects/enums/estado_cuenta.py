from enum import Enum


class EstadoCuenta(Enum):
    ACTIVA = 'activa'
    INACTIVA = 'inactiva'
    EN_TRASLADO = 'en_traslado'
    EN_RADICACION = 'en_radicacion'
