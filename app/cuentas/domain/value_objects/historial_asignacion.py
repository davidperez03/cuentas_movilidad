from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional
from enum import Enum


class TipoAsignacion(Enum):
    """Tipos de asignación para mejor categorización"""
    CREACION = "creacion"
    REASIGNACION = "reasignacion"
    INICIO_PROCESO = "inicio_proceso"
    COMPLETAR_PROCESO = "completar_proceso"
    DEVOLVER_PROCESO = "devolver_proceso"
    INACTIVACION = "inactivacion"
    REACTIVACION = "reactivacion"


@dataclass(frozen=True)
class HistorialAsignacion:
    """
    Value Object para trazabilidad de asignaciones de funcionarios.
    
    Registra quién, cuándo y por qué se asignó un funcionario a una cuenta.
    Inmutable para garantizar integridad del historial.
    """
    funcionario_id: str
    fecha_asignacion: date
    motivo: str
    funcionario_asigna: Optional[str] = None
    tipo_asignacion: Optional[TipoAsignacion] = None
    observaciones: Optional[str] = None

    def __post_init__(self):
        # PASO 1: Normalizar valores (manejar None y espacios)
        funcionario_normalizado = self.funcionario_id.strip().upper() if self.funcionario_id else ""
        motivo_normalizado = self.motivo.strip() if self.motivo else ""
        funcionario_asigna_normalizado = self.funcionario_asigna.strip().upper() if self.funcionario_asigna else None
        observaciones_normalizadas = self.observaciones.strip() if self.observaciones else None
        
        # PASO 2: Validar valores normalizados
        if not funcionario_normalizado:
            raise ValueError("El ID del funcionario no puede estar vacío")
        
        if not isinstance(self.fecha_asignacion, date):
            raise ValueError("La fecha de asignación debe ser un objeto date")
        
        if not motivo_normalizado:
            raise ValueError("El motivo de asignación no puede estar vacío")
        
        if len(motivo_normalizado) > 500:
            raise ValueError("El motivo no puede exceder 500 caracteres")
        
        if observaciones_normalizadas and len(observaciones_normalizadas) > 1000:
            raise ValueError("Las observaciones no pueden exceder 1000 caracteres")
        
        if self.fecha_asignacion > date.today():
            raise ValueError("La fecha de asignación no puede ser futura")
        
        # PASO 3: Asignar valores normalizados
        object.__setattr__(self, 'funcionario_id', funcionario_normalizado)
        object.__setattr__(self, 'motivo', motivo_normalizado)
        object.__setattr__(self, 'funcionario_asigna', funcionario_asigna_normalizado)
        object.__setattr__(self, 'observaciones', observaciones_normalizadas)
        
        # PASO 4: Detectar tipo automáticamente si no se especificó
        if self.tipo_asignacion is None:
            tipo_detectado = self._detectar_tipo_asignacion()
            object.__setattr__(self, 'tipo_asignacion', tipo_detectado)

    def _detectar_tipo_asignacion(self) -> TipoAsignacion:
            motivo_lower = self.motivo.lower()
    
            motivo_lower = motivo_lower.replace('á', 'a')
            motivo_lower = motivo_lower.replace('é', 'e') 
            motivo_lower = motivo_lower.replace('í', 'i')
            motivo_lower = motivo_lower.replace('ó', 'o')
            motivo_lower = motivo_lower.replace('ú', 'u')
            motivo_lower = motivo_lower.replace('ñ', 'n')

            if "creacion" in motivo_lower:
                return TipoAsignacion.CREACION
            elif "reasignacion" in motivo_lower:
                return TipoAsignacion.REASIGNACION
            elif "inicio" in motivo_lower:
                return TipoAsignacion.INICIO_PROCESO
            elif "completar" in motivo_lower:
                return TipoAsignacion.COMPLETAR_PROCESO
            elif "devolver" in motivo_lower:
                return TipoAsignacion.DEVOLVER_PROCESO
            elif "inactivar" in motivo_lower:
                return TipoAsignacion.INACTIVACION
            elif "reactivar" in motivo_lower:
                return TipoAsignacion.REACTIVACION
            else:
                return TipoAsignacion.REASIGNACION 

    def es_asignacion_inicial(self) -> bool:
        """Verifica si es la asignación inicial (creación de cuenta)"""
        return self.tipo_asignacion == TipoAsignacion.CREACION

    def es_reasignacion_manual(self) -> bool:
        """Verifica si es una reasignación manual (no automática por proceso)"""
        return self.tipo_asignacion == TipoAsignacion.REASIGNACION

    def es_cambio_por_proceso(self) -> bool:
        """Verifica si el cambio fue debido a un proceso (traslado/radicación)"""
        return self.tipo_asignacion in [
            TipoAsignacion.INICIO_PROCESO,
            TipoAsignacion.COMPLETAR_PROCESO,
            TipoAsignacion.DEVOLVER_PROCESO
        ]

    def fue_asignado_por_supervisor(self) -> bool:
        """Verifica si fue asignado por otro funcionario (supervisor)"""
        return self.funcionario_asigna is not None

    def get_dias_desde_asignacion(self) -> int:
        """Calcula días transcurridos desde la asignación"""
        return (date.today() - self.fecha_asignacion).days

    def es_asignacion_reciente(self, dias_limite: int = 7) -> bool:
        """Verifica si la asignación es reciente (últimos N días)"""
        return self.get_dias_desde_asignacion() <= dias_limite

    def get_motivo_detallado(self) -> str:
        """Retorna motivo con observaciones si las hay"""
        if self.observaciones:
            return f"{self.motivo} - {self.observaciones}"
        return self.motivo

    def get_info_asignador(self) -> str:
        """Retorna información del funcionario que asigna"""
        if self.funcionario_asigna:
            return f"Asignado por: {self.funcionario_asigna}"
        return "Asignación automática"

    def get_resumen_completo(self) -> str:
        """Retorna resumen completo de la asignación"""
        fecha_str = self.fecha_asignacion.strftime("%d/%m/%Y")
        tipo_str = self.tipo_asignacion.value.replace("_", " ").title()
        
        resumen = f"{fecha_str} | {tipo_str} | {self.funcionario_id} | {self.motivo}"
        
        if self.funcionario_asigna:
            resumen += f" | Por: {self.funcionario_asigna}"
        
        return resumen

    def __str__(self) -> str:
        return f"{self.fecha_asignacion} - {self.funcionario_id}: {self.motivo}"

    def __repr__(self) -> str:
        return f"HistorialAsignacion(funcionario='{self.funcionario_id}', fecha={self.fecha_asignacion}, tipo='{self.tipo_asignacion.value}')"

    @classmethod
    def crear_asignacion_inicial(cls, funcionario_id: str, fecha: date) -> 'HistorialAsignacion':
        """Factory method para asignación inicial (creación de cuenta)"""
        return cls(
            funcionario_id=funcionario_id,
            fecha_asignacion=fecha,
            motivo="creacion",
            tipo_asignacion=TipoAsignacion.CREACION
        )

    @classmethod
    def crear_reasignacion_manual(cls, funcionario_id: str, funcionario_asigna: str, 
                                 motivo: str = "reasignacion", observaciones: Optional[str] = None) -> 'HistorialAsignacion':
        """Factory method para reasignación manual"""
        return cls(
            funcionario_id=funcionario_id,
            fecha_asignacion=date.today(),
            motivo=motivo,
            funcionario_asigna=funcionario_asigna,
            tipo_asignacion=TipoAsignacion.REASIGNACION,
            observaciones=observaciones
        )

    @classmethod
    def crear_cambio_proceso(cls, funcionario_id: str, tipo_proceso: str, 
                           accion: str, motivo_adicional: Optional[str] = None) -> 'HistorialAsignacion':
        """
        Factory method para cambios por procesos
        
        Args:
            funcionario_id: ID del funcionario
            tipo_proceso: "traslado" o "radicacion"
            accion: "inicio", "completar", "devolver"
            motivo_adicional: Motivo adicional (ej: para devoluciones)
        """
        motivo_base = f"{accion}_{tipo_proceso}"
        
        if motivo_adicional:
            motivo = f"{motivo_base}: {motivo_adicional}"
        else:
            motivo = motivo_base
    
        # Mapear acción a tipo específico
        tipo_mapping = {
            "inicio": TipoAsignacion.INICIO_PROCESO,
            "completar": TipoAsignacion.COMPLETAR_PROCESO,
            "devolver": TipoAsignacion.DEVOLVER_PROCESO
        }
        
        tipo_asignacion = tipo_mapping.get(accion, TipoAsignacion.REASIGNACION)
        
        return cls(
            funcionario_id=funcionario_id,
            fecha_asignacion=date.today(),
            motivo=motivo,
            tipo_asignacion=tipo_asignacion,
            observaciones=motivo_adicional
        )

    @classmethod
    def crear_inactivacion(cls, funcionario_id: str, motivo: str) -> 'HistorialAsignacion':
        """Factory method para inactivación de cuenta"""
        return cls(
            funcionario_id=funcionario_id,
            fecha_asignacion=date.today(),
            motivo=f"inactivar: {motivo}",
            tipo_asignacion=TipoAsignacion.INACTIVACION,
            observaciones=motivo
        )

    @classmethod
    def crear_reactivacion(cls, funcionario_id: str) -> 'HistorialAsignacion':
        """Factory method para reactivación de cuenta"""
        return cls(
            funcionario_id=funcionario_id,
            fecha_asignacion=date.today(),
            motivo="reactivar",
            tipo_asignacion=TipoAsignacion.REACTIVACION
        )