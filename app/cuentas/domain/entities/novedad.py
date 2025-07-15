from dataclasses import dataclass, field
from typing import Optional, List
from datetime import date, datetime

from app.cuentas.domain.value_objects.placa import Placa
from app.cuentas.domain.value_objects.ids.id_novedad import IdentificadorNovedad
from app.cuentas.domain.value_objects.descripcion_novedad import DescripcionNovedad
from app.cuentas.domain.value_objects.observacion import Observacion
from app.cuentas.domain.value_objects.enums.novedades.tipo_novedad import TipoNovedad
from app.cuentas.domain.value_objects.enums.novedades.estado_novedad import EstadoNovedad
from app.cuentas.domain.value_objects.enums.novedades.prioridad_novedad import PrioridadNovedad
from app.cuentas.domain.events.cuenta_events import DomainEvent


@dataclass
class Novedad:
    """
    Entidad Novedad - Representa una irregularidad o inconformidad encontrada 
    durante procesos de traslado o radicación.
    
    Maneja el ciclo completo de una novedad desde su detección hasta su resolución.
    Parte del aggregate Cuenta pero con identidad propia para trazabilidad detallada.
    """
    identificador: IdentificadorNovedad
    placa: Placa
    tipo_novedad: TipoNovedad
    descripcion: DescripcionNovedad
    prioridad: PrioridadNovedad
    funcionario_reporta: str
    fecha_reporte: date
    
    # Contexto del proceso donde se detectó
    tipo_proceso: str  # "traslado" o "radicacion"
    
    # Estado mutable de la novedad
    estado: EstadoNovedad = field(default=EstadoNovedad.PENDIENTE)
    observaciones: Observacion = field(default_factory=Observacion.vacia)
    
    # Resolución
    funcionario_resuelve: Optional[str] = field(default=None)
    fecha_resolucion: Optional[date] = field(default=None)
    descripcion_resolucion: Optional[str] = field(default=None)
    
    # Auditoría
    funcionario_actual: Optional[str] = field(default=None)
    fecha_ultima_actualizacion: Optional[date] = field(default=None)
    
    # Domain Events
    _domain_events: List[DomainEvent] = field(default_factory=list, init=False, repr=False)
    _initialized: bool = field(default=False, init=False, repr=False)

    def __post_init__(self):
        if self._initialized:
            return
            
        self._validar_tipos_value_objects()
        self._validar_funcionario_reporta()
        self._validar_tipo_proceso()
        self._validar_fechas()
        
        # Normalizar funcionarios
        object.__setattr__(self, 'funcionario_reporta', self.funcionario_reporta.strip().upper())
        object.__setattr__(self, 'tipo_proceso', self.tipo_proceso.lower().strip())
        
        # Inicializar campos opcionales
        if self.funcionario_actual is None:
            object.__setattr__(self, 'funcionario_actual', self.funcionario_reporta)
        
        if self.fecha_ultima_actualizacion is None:
            object.__setattr__(self, 'fecha_ultima_actualizacion', date.today())
        
        object.__setattr__(self, '_initialized', True)

    def _validar_tipos_value_objects(self):
        """Valida que los VOs sean del tipo correcto"""
        if not isinstance(self.identificador, IdentificadorNovedad):
            raise ValueError("El identificador debe ser una instancia válida de IdentificadorNovedad")
        
        if not isinstance(self.placa, Placa):
            raise ValueError("La placa debe ser una instancia válida de Placa")
            
        if not isinstance(self.descripcion, DescripcionNovedad):
            raise ValueError("La descripción debe ser una instancia válida de DescripcionNovedad")
            
        if not isinstance(self.observaciones, Observacion):
            raise ValueError("Las observaciones deben ser una instancia válida de Observacion")

    def _validar_funcionario_reporta(self):
        """Valida el funcionario que reporta"""
        if not self.funcionario_reporta or not self.funcionario_reporta.strip():
            raise ValueError("El funcionario que reporta no puede estar vacío")

    def _validar_tipo_proceso(self):
        """Valida el tipo de proceso"""
        if self.tipo_proceso.lower() not in ["traslado", "radicacion"]:
            raise ValueError("El tipo de proceso debe ser 'traslado' o 'radicacion'")

    def _validar_fechas(self):
        """Valida coherencia de fechas"""
        if not isinstance(self.fecha_reporte, date):
            raise ValueError("La fecha de reporte debe ser un objeto date")
        
        if self.fecha_reporte > date.today():
            raise ValueError("La fecha de reporte no puede ser futura")
        
        if self.fecha_resolucion and self.fecha_resolucion < self.fecha_reporte:
            raise ValueError("La fecha de resolución no puede ser anterior al reporte")

    def _add_domain_event(self, event: DomainEvent):
        """Agrega un evento de dominio"""
        self._domain_events.append(event)

    def get_domain_events(self) -> List[DomainEvent]:
        """Retorna y limpia los eventos de dominio pendientes"""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events

    # === MÉTODOS DE CONSULTA ===
    
    def get_codigo_novedad(self) -> str:
        """Retorna el código único de la novedad"""
        return self.identificador.codigo
    
    def get_placa_valor(self) -> str:
        """Retorna el valor de la placa como string"""
        return str(self.placa)
    
    def get_tipo_novedad_descripcion(self) -> str:
        """Retorna descripción legible del tipo de novedad"""
        return self.tipo_novedad.value.replace("_", " ").title()
    
    def get_prioridad_descripcion(self) -> str:
        """Retorna descripción de la prioridad"""
        return self.prioridad.value.upper()
    
    def get_funcionario_responsable(self) -> str:
        """Retorna el funcionario actualmente responsable"""
        if self.esta_resuelta() and self.funcionario_resuelve:
            return self.funcionario_resuelve
        return self.funcionario_actual or self.funcionario_reporta
    
    def get_dias_desde_reporte(self) -> int:
        """Calcula días transcurridos desde el reporte"""
        return (date.today() - self.fecha_reporte).days
    
    def get_dias_desde_ultima_actualizacion(self) -> int:
        """Calcula días desde la última actualización"""
        if self.fecha_ultima_actualizacion:
            return (date.today() - self.fecha_ultima_actualizacion).days
        return self.get_dias_desde_reporte()
    
    def get_tiempo_resolucion_dias(self) -> Optional[int]:
        """Calcula días que tomó resolver la novedad"""
        if self.fecha_resolucion:
            return (self.fecha_resolucion - self.fecha_reporte).days
        return None

    # === VALIDACIONES DE ESTADO ===
    
    def esta_pendiente(self) -> bool:
        """Verifica si está pendiente de atención"""
        return self.estado == EstadoNovedad.PENDIENTE
    
    def esta_en_revision(self) -> bool:
        """Verifica si está en proceso de revisión"""
        return self.estado == EstadoNovedad.EN_REVISION
    
    def esta_resuelta(self) -> bool:
        """Verifica si fue resuelta"""
        return self.estado == EstadoNovedad.RESUELTA
    
    def esta_reabierta(self) -> bool:
        """Verifica si fue reabierta"""
        return self.estado == EstadoNovedad.REABIERTA
    
    def esta_en_estado_final(self) -> bool:
        """Verifica si está en estado final"""
        return self.estado.es_estado_final()
    
    def requiere_atencion_inmediata(self) -> bool:
        """Verifica si requiere atención inmediata"""
        return (self.estado.requiere_accion() and 
                (self.prioridad.es_critica_o_alta() or self.get_dias_desde_reporte() > 3))
    
    def es_novedad_critica(self) -> bool:
        """Verifica si es una novedad crítica"""
        return self.prioridad == PrioridadNovedad.CRITICA
    
    def es_novedad_antigua(self, dias_limite: int = 30) -> bool:
        """Verifica si es una novedad antigua sin resolver"""
        return (not self.esta_resuelta() and 
                self.get_dias_desde_reporte() >= dias_limite)

    # === REGLAS DE NEGOCIO - TRANSICIONES ===
    
    def puede_pasar_a_revision(self) -> bool:
        """Verifica si puede pasar a revisión"""
        return self.estado.puede_transicionar_a(EstadoNovedad.EN_REVISION)
    
    def puede_ser_resuelta(self) -> bool:
        """Verifica si puede ser resuelta"""
        return self.estado.puede_transicionar_a(EstadoNovedad.RESUELTA)
    
    def puede_ser_reabierta(self) -> bool:
        """Verifica si puede ser reabierta"""
        return self.estado.puede_transicionar_a(EstadoNovedad.REABIERTA)
    
    def puede_cambiar_prioridad(self) -> bool:
        """Verifica si se puede cambiar la prioridad"""
        return not self.esta_resuelta()

    # === MÉTODOS DE COMANDO (Cambio de estado) ===
    
    def tomar_en_revision(self, funcionario_id: str) -> None:
        """Toma la novedad en revisión"""
        if not self.puede_pasar_a_revision():
            raise ValueError(f"No se puede pasar a revisión desde estado: {self.estado.value}")
        
        self.estado = EstadoNovedad.EN_REVISION
        object.__setattr__(self, 'funcionario_actual', funcionario_id.strip().upper())
        object.__setattr__(self, 'fecha_ultima_actualizacion', date.today())
        
        # Agregar observación de toma en revisión
        obs_revision = Observacion.crear_con_timestamp(
            f"Novedad tomada en revisión por {funcionario_id}", 
            funcionario_id
        )
        nueva_obs = Observacion.combinar_observaciones([self.observaciones, obs_revision])
        object.__setattr__(self, 'observaciones', nueva_obs)
    
    def resolver_novedad(self, funcionario_id: str, descripcion_resolucion: str) -> None:
        """Resuelve la novedad"""
        if not self.puede_ser_resuelta():
            raise ValueError(f"No se puede resolver desde estado: {self.estado.value}")
        
        if not descripcion_resolucion or not descripcion_resolucion.strip():
            raise ValueError("La descripción de resolución no puede estar vacía")
        
        self.estado = EstadoNovedad.RESUELTA
        object.__setattr__(self, 'funcionario_resuelve', funcionario_id.strip().upper())
        object.__setattr__(self, 'funcionario_actual', funcionario_id.strip().upper())
        object.__setattr__(self, 'fecha_resolucion', date.today())
        object.__setattr__(self, 'fecha_ultima_actualizacion', date.today())
        object.__setattr__(self, 'descripcion_resolucion', descripcion_resolucion.strip())
        
        # Agregar observación de resolución
        obs_resolucion = Observacion.crear_con_timestamp(
            f"NOVEDAD RESUELTA: {descripcion_resolucion}", 
            funcionario_id
        )
        nueva_obs = Observacion.combinar_observaciones([self.observaciones, obs_resolucion])
        object.__setattr__(self, 'observaciones', nueva_obs)
    
    def reabrir_novedad(self, funcionario_id: str, motivo_reapertura: str) -> None:
        """Reabre una novedad previamente resuelta"""
        if not self.puede_ser_reabierta():
            raise ValueError(f"No se puede reabrir desde estado: {self.estado.value}")
        
        if not motivo_reapertura or not motivo_reapertura.strip():
            raise ValueError("El motivo de reapertura no puede estar vacío")
        
        self.estado = EstadoNovedad.REABIERTA
        object.__setattr__(self, 'funcionario_actual', funcionario_id.strip().upper())
        object.__setattr__(self, 'fecha_ultima_actualizacion', date.today())
        
        # Limpiar datos de resolución anterior
        object.__setattr__(self, 'funcionario_resuelve', None)
        object.__setattr__(self, 'fecha_resolucion', None)
        object.__setattr__(self, 'descripcion_resolucion', None)
        
        # Agregar observación de reapertura
        obs_reapertura = Observacion.crear_con_timestamp(
            f"NOVEDAD REABIERTA: {motivo_reapertura}", 
            funcionario_id
        )
        nueva_obs = Observacion.combinar_observaciones([self.observaciones, obs_reapertura])
        object.__setattr__(self, 'observaciones', nueva_obs)
    
    def cambiar_prioridad(self, funcionario_id: str, nueva_prioridad: PrioridadNovedad, 
                         justificacion: str) -> None:
        """Cambia la prioridad de la novedad"""
        if not self.puede_cambiar_prioridad():
            raise ValueError("No se puede cambiar la prioridad de una novedad resuelta")
        
        if nueva_prioridad == self.prioridad:
            raise ValueError("La nueva prioridad debe ser diferente a la actual")
        
        if not justificacion or not justificacion.strip():
            raise ValueError("La justificación del cambio de prioridad no puede estar vacía")
        
        prioridad_anterior = self.prioridad
        object.__setattr__(self, 'prioridad', nueva_prioridad)
        object.__setattr__(self, 'funcionario_actual', funcionario_id.strip().upper())
        object.__setattr__(self, 'fecha_ultima_actualizacion', date.today())
        
        # Agregar observación del cambio
        obs_cambio = Observacion.crear_con_timestamp(
            f"PRIORIDAD CAMBIADA: De {prioridad_anterior.value.upper()} a {nueva_prioridad.value.upper()}. {justificacion}", 
            funcionario_id
        )
        nueva_obs = Observacion.combinar_observaciones([self.observaciones, obs_cambio])
        object.__setattr__(self, 'observaciones', nueva_obs)
    
    def actualizar_observaciones(self, funcionario_id: str, nuevas_observaciones: str) -> None:
        """Actualiza las observaciones de la novedad"""
        if self.esta_resuelta():
            raise ValueError("No se pueden actualizar observaciones de una novedad resuelta")
        
        obs_actualizacion = Observacion.crear_con_timestamp(nuevas_observaciones, funcionario_id)
        nueva_obs = Observacion.combinar_observaciones([self.observaciones, obs_actualizacion])
        object.__setattr__(self, 'observaciones', nueva_obs)
        object.__setattr__(self, 'fecha_ultima_actualizacion', date.today())

    # === MÉTODOS DE ANÁLISIS ===
    
    def es_similar_a(self, otra_novedad: 'Novedad') -> bool:
        """Verifica si es similar a otra novedad"""
        return (self.placa == otra_novedad.placa and
                self.tipo_novedad == otra_novedad.tipo_novedad and
                self.descripcion.es_similar_a(otra_novedad.descripcion))
    
    def get_resumen_ejecutivo(self) -> str:
        """Genera resumen ejecutivo de la novedad"""
        tiempo_texto = f"{self.get_dias_desde_reporte()} días"
        if self.esta_resuelta():
            tiempo_resolucion = self.get_tiempo_resolucion_dias()
            tiempo_texto = f"Resuelta en {tiempo_resolucion} días"
        
        return (f"{self.get_codigo_novedad()} | {self.placa} | "
                f"{self.get_tipo_novedad_descripcion()} | "
                f"{self.prioridad.value.upper()} | {tiempo_texto}")

    # === MÉTODOS DE REPRESENTACIÓN ===
    
    def __str__(self) -> str:
        return f"Novedad({self.identificador.codigo} - {self.placa})"
    
    def __repr__(self) -> str:
        return f"Novedad(codigo='{self.identificador.codigo}', placa='{self.placa}', tipo='{self.tipo_novedad.value}', estado='{self.estado.value}')"

    # === FACTORY METHODS ===
    
    @classmethod
    def crear_nueva(cls, placa: Placa, tipo_novedad: TipoNovedad, 
                   descripcion: DescripcionNovedad, prioridad: PrioridadNovedad,
                   funcionario_reporta: str, tipo_proceso: str,
                   consecutivo_novedad: int,
                   observaciones_iniciales: Optional[str] = None) -> 'Novedad':
        """Factory method para crear una nueva novedad"""
        identificador = IdentificadorNovedad.generar_para_hoy(consecutivo_novedad)
        fecha_reporte = date.today()
        
        observaciones = Observacion.vacia()
        if observaciones_iniciales:
            observaciones = Observacion.crear_con_timestamp(observaciones_iniciales, funcionario_reporta)
        
        return cls(
            identificador=identificador,
            placa=placa,
            tipo_novedad=tipo_novedad,
            descripcion=descripcion,
            prioridad=prioridad,
            funcionario_reporta=funcionario_reporta,
            fecha_reporte=fecha_reporte,
            tipo_proceso=tipo_proceso,
            observaciones=observaciones
        )
    
    @classmethod
    def crear_desde_repositorio(cls, identificador: IdentificadorNovedad, placa: Placa,
                               tipo_novedad: TipoNovedad, descripcion: DescripcionNovedad,
                               prioridad: PrioridadNovedad, funcionario_reporta: str,
                               fecha_reporte: date, tipo_proceso: str, estado: EstadoNovedad,
                               observaciones: Observacion, funcionario_resuelve: Optional[str],
                               fecha_resolucion: Optional[date], descripcion_resolucion: Optional[str],
                               funcionario_actual: Optional[str], 
                               fecha_ultima_actualizacion: Optional[date]) -> 'Novedad':
        """Factory method para recrear novedad desde datos del repositorio"""
        novedad = object.__new__(cls)
        
        object.__setattr__(novedad, 'identificador', identificador)
        object.__setattr__(novedad, 'placa', placa)
        object.__setattr__(novedad, 'tipo_novedad', tipo_novedad)
        object.__setattr__(novedad, 'descripcion', descripcion)
        object.__setattr__(novedad, 'prioridad', prioridad)
        object.__setattr__(novedad, 'funcionario_reporta', funcionario_reporta.strip().upper())
        object.__setattr__(novedad, 'fecha_reporte', fecha_reporte)
        object.__setattr__(novedad, 'tipo_proceso', tipo_proceso.lower().strip())
        object.__setattr__(novedad, 'estado', estado)
        object.__setattr__(novedad, 'observaciones', observaciones)
        object.__setattr__(novedad, 'funcionario_resuelve', funcionario_resuelve)
        object.__setattr__(novedad, 'fecha_resolucion', fecha_resolucion)
        object.__setattr__(novedad, 'descripcion_resolucion', descripcion_resolucion)
        object.__setattr__(novedad, 'funcionario_actual', funcionario_actual)
        object.__setattr__(novedad, 'fecha_ultima_actualizacion', fecha_ultima_actualizacion)
        
        object.__setattr__(novedad, '_domain_events', [])
        object.__setattr__(novedad, '_initialized', True)
        
        novedad._validar_tipos_value_objects()
        novedad._validar_funcionario_reporta()
        novedad._validar_tipo_proceso()
        novedad._validar_fechas()
        
        return novedad