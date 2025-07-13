from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    """Clase base para eventos de dominio"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    aggregate_id: str
    version: int = field(default=1)


@dataclass(frozen=True)
class CuentaCreadaEvent(DomainEvent):
    """Evento: Nueva cuenta creada"""
    placa: str
    numero_cuenta: str
    tipo_servicio: str
    funcionario_creador: str

    @classmethod
    def create(cls, placa: str, numero_cuenta: str, tipo_servicio: str, funcionario_creador: str) -> 'CuentaCreadaEvent':
        return cls(
            aggregate_id=placa,
            placa=placa,
            numero_cuenta=numero_cuenta,
            tipo_servicio=tipo_servicio,
            funcionario_creador=funcionario_creador
        )


@dataclass(frozen=True)
class ProcesoIniciadoEvent(DomainEvent):
    """Evento: Proceso de traslado o radicación iniciado"""
    placa: str
    tipo_proceso: str 
    funcionario: str
    numero_cuenta: str

    @classmethod
    def create(cls, placa: str, tipo_proceso: str, funcionario: str, numero_cuenta: str) -> 'ProcesoIniciadoEvent':
        return cls(
            aggregate_id=placa,
            placa=placa,
            tipo_proceso=tipo_proceso,
            funcionario=funcionario,
            numero_cuenta=numero_cuenta
        )


@dataclass(frozen=True)
class ProcesoCompletadoEvent(DomainEvent):
    """Evento: Proceso completado exitosamente"""
    placa: str
    tipo_proceso: str
    funcionario: str
    numero_cuenta: str
    resultado: str  
    motivo_devolucion: Optional[str] = None

    @classmethod
    def create(cls, placa: str, tipo_proceso: str, funcionario: str, numero_cuenta: str,
               resultado: str, motivo_devolucion: Optional[str] = None) -> 'ProcesoCompletadoEvent':
        return cls(
            aggregate_id=placa,
            placa=placa,
            tipo_proceso=tipo_proceso,
            funcionario=funcionario,
            numero_cuenta=numero_cuenta,
            resultado=resultado,
            motivo_devolucion=motivo_devolucion
        )


@dataclass(frozen=True)
class CuentaReasignadaEvent(DomainEvent):
    """Evento: Cuenta reasignada a otro funcionario"""
    placa: str
    funcionario_anterior: str
    funcionario_nuevo: str
    funcionario_autoriza: Optional[str]
    motivo: str

    @classmethod
    def create(cls, placa: str, funcionario_anterior: str, funcionario_nuevo: str,
               funcionario_autoriza: Optional[str], motivo: str) -> 'CuentaReasignadaEvent':
        return cls(
            aggregate_id=placa,
            placa=placa,
            funcionario_anterior=funcionario_anterior,
            funcionario_nuevo=funcionario_nuevo,
            funcionario_autoriza=funcionario_autoriza,
            motivo=motivo
        )


@dataclass(frozen=True)
class CuentaInactivadaEvent(DomainEvent):
    """Evento: Cuenta inactivada"""
    placa: str
    funcionario: str
    motivo: str

    @classmethod
    def create(cls, placa: str, funcionario: str, motivo: str) -> 'CuentaInactivadaEvent':
        return cls(
            aggregate_id=placa,
            placa=placa,
            funcionario=funcionario,
            motivo=motivo
        )


@dataclass(frozen=True)
class CuentaReactivadaEvent(DomainEvent):
    """Evento: Cuenta reactivada"""
    placa: str
    funcionario: str

    @classmethod
    def create(cls, placa: str, funcionario: str) -> 'CuentaReactivadaEvent':
        return cls(
            aggregate_id=placa,
            placa=placa,
            funcionario=funcionario
        )
