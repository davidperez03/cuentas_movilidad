from dataclasses import dataclass, field
from typing import Optional, List
from datetime import date

from app.cuentas.domain.value_objects.placa import Placa
from app.cuentas.domain.value_objects.fecha_tramite import FechaTramite
from app.cuentas.domain.value_objects.fecha_vencimiento import FechaVencimiento
from app.cuentas.domain.value_objects.ubicacion import Ubicacion
from app.cuentas.domain.value_objects.observacion import Observacion
from app.cuentas.domain.value_objects.enums.estado_radicacion import EstadoRadicacion
from app.cuentas.domain.events.cuenta_events import DomainEvent


@dataclass
class Radicacion:
    """
    Entidad Radicación - Proceso de recepción de cuenta desde otro organismo.
    
    Maneja el flujo completo desde recepción hasta radicación final o devolución.
    Parte del aggregate Cuenta pero con su propia identidad y ciclo de vida.
    """
    placa: Placa
    organismo_origen: Ubicacion
    fecha_tramite: FechaTramite
    fecha_vencimiento: FechaVencimiento
    funcionario_recibe: str
    
    # Estado mutable del proceso
    estado: EstadoRadicacion = field(default=EstadoRadicacion.PENDIENTE_RADICAR)
    observaciones: Observacion = field(default_factory=Observacion.vacia)
    
    # Auditoría de transiciones
    funcionario_actual: Optional[str] = field(default=None)
    fecha_ultima_actualizacion: Optional[date] = field(default=None)
    
    # Domain Events
    _domain_events: List[DomainEvent] = field(default_factory=list, init=False, repr=False)
    _initialized: bool = field(default=False, init=False, repr=False)
    _fue_recibida: bool = field(default=False, init=False, repr=False)

    def __post_init__(self):
        if self._initialized:
            return
            
        self._validar_tipos_value_objects()
        self._validar_funcionario_recibe()
        self._validar_fechas()
        
        # Normalizar funcionario
        object.__setattr__(self, 'funcionario_recibe', self.funcionario_recibe.strip().upper())
        
        # Inicializar campos opcionales
        if self.funcionario_actual is None:
            object.__setattr__(self, 'funcionario_actual', self.funcionario_recibe)
        
        if self.fecha_ultima_actualizacion is None:
            object.__setattr__(self, 'fecha_ultima_actualizacion', date.today())
        
        object.__setattr__(self, '_initialized', True)

    def _validar_tipos_value_objects(self):
        """Valida que los VOs sean del tipo correcto"""
        if not isinstance(self.placa, Placa):
            raise ValueError("La placa debe ser una instancia válida de Placa")
        
        if not isinstance(self.organismo_origen, Ubicacion):
            raise ValueError("El organismo origen debe ser una instancia válida de Ubicacion")
            
        if not isinstance(self.fecha_tramite, FechaTramite):
            raise ValueError("La fecha de trámite debe ser una instancia válida de FechaTramite")
            
        if not isinstance(self.fecha_vencimiento, FechaVencimiento):
            raise ValueError("La fecha de vencimiento debe ser una instancia válida de FechaVencimiento")
            
        if not isinstance(self.observaciones, Observacion):
            raise ValueError("Las observaciones deben ser una instancia válida de Observacion")

    def _validar_funcionario_recibe(self):
        """Valida el funcionario que recibe"""
        if not self.funcionario_recibe or not self.funcionario_recibe.strip():
            raise ValueError("El funcionario que recibe no puede estar vacío")

    def _validar_fechas(self):
        """Valida coherencia de fechas"""
        if self.fecha_vencimiento.fecha <= self.fecha_tramite.fecha:
            raise ValueError("La fecha de vencimiento debe ser posterior a la fecha de trámite")

    def _add_domain_event(self, event: DomainEvent):
        """Agrega un evento de dominio"""
        self._domain_events.append(event)

    def get_domain_events(self) -> List[DomainEvent]:
        """Retorna y limpia los eventos de dominio pendientes"""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events

    # === MÉTODOS DE CONSULTA ===
    
    def get_placa_valor(self) -> str:
        """Retorna el valor de la placa como string"""
        return str(self.placa)
    
    def get_codigo_organismo_origen(self) -> str:
        """Retorna el código del organismo origen"""
        return self.organismo_origen.codigo
    
    def get_nombre_organismo_origen(self) -> str:
        """Retorna el nombre del organismo origen"""
        return self.organismo_origen.get_nombre_corto()
    
    def get_ubicacion_completa_origen(self) -> str:
        """Retorna la ubicación completa del origen"""
        return self.organismo_origen.get_ubicacion_display()
    
    def get_dias_restantes_vencimiento(self) -> int:
        """Retorna días restantes hasta el vencimiento"""
        return self.fecha_vencimiento.dias_restantes()
    
    def get_nivel_urgencia(self) -> str:
        """Retorna el nivel de urgencia basado en vencimiento"""
        return self.fecha_vencimiento.nivel_urgencia()
    
    def get_funcionario_responsable(self) -> str:
        """Retorna el funcionario actualmente responsable"""
        return self.funcionario_actual or self.funcionario_recibe
    
    def get_dias_en_proceso(self) -> int:
        """Calcula días transcurridos desde la recepción"""
        return self.fecha_tramite.dias_desde_hoy() * -1 if self.fecha_tramite.es_futuro() else self.fecha_tramite.dias_desde_hoy()

    # === VALIDACIONES DE ESTADO ===
    
    def esta_vencida(self) -> bool:
        """Verifica si la radicación está vencida"""
        return self.fecha_vencimiento.esta_vencida()
    
    def esta_por_vencer(self, dias_alerta: int = 7) -> bool:
        """Verifica si está por vencer"""
        return self.fecha_vencimiento.esta_por_vencer(dias_alerta)
    
    def es_critica(self) -> bool:
        """Verifica si está en estado crítico"""
        return self.fecha_vencimiento.es_critica()
    
    def esta_pendiente(self) -> bool:
        """Verifica si está pendiente de recibir"""
        return self.estado == EstadoRadicacion.PENDIENTE_RADICAR
    
    def fue_recibida(self) -> bool:
        """Verifica si ya fue recibida"""
        return self._fue_recibida
    
    def esta_en_revision(self) -> bool:
        """Verifica si está en proceso de revisión"""
        return self.estado == EstadoRadicacion.REVISADO
    
    def tiene_novedades(self) -> bool:
        """Verifica si tiene novedades pendientes"""
        return self.estado == EstadoRadicacion.CON_NOVEDADES
    
    def esta_completada(self) -> bool:
        """Verifica si la radicación fue completada exitosamente"""
        return self.estado == EstadoRadicacion.RADICADO
    
    def fue_devuelta(self) -> bool:
        """Verifica si fue devuelta"""
        return self.estado == EstadoRadicacion.DEVUELTO
    
    def esta_en_estado_final(self) -> bool:
        """Verifica si está en estado final (radicada o devuelta)"""
        return self.estado.es_estado_final()

    # === REGLAS DE NEGOCIO - TRANSICIONES ===
    
    def puede_ser_recibida(self) -> bool:
        """Verifica si puede ser recibida"""
        return self.estado == EstadoRadicacion.PENDIENTE_RADICAR
    
    def puede_pasar_a_revision(self) -> bool:
        """Verifica si puede pasar a revisión"""
        return self.estado == EstadoRadicacion.RECIBIDO
    
    def puede_completar_radicacion(self) -> bool:
        """Verifica si puede completar la radicación"""
        return self.estado == EstadoRadicacion.REVISADO
    
    def puede_reportar_novedad(self) -> bool:
        """Verifica si puede reportar novedad"""
        return self.estado == EstadoRadicacion.REVISADO
    
    def puede_resolver_novedad(self) -> bool:
        """Verifica si puede resolver novedad"""
        return self.estado == EstadoRadicacion.CON_NOVEDADES
    
    def puede_ser_devuelta(self, es_admin: bool = False) -> bool:
        """Verifica si puede ser devuelta (admin puede desde cualquier estado)"""
        if es_admin:
            return not self.esta_en_estado_final()
        return self.estado.puede_transicionar_a(EstadoRadicacion.DEVUELTO, es_admin)

    # === MÉTODOS DE COMANDO (Cambio de estado) ===
    
    def marcar_como_recibida(self, funcionario_id: str) -> None:
        """Marca la radicación como recibida"""
        if not self.puede_ser_recibida():
            raise ValueError(f"No se puede recibir desde estado: {self.estado.value}")
        
        self.estado = EstadoRadicacion.RECIBIDO
        object.__setattr__(self, 'funcionario_actual', funcionario_id.strip().upper())
        object.__setattr__(self, 'fecha_ultima_actualizacion', date.today())
        object.__setattr__(self, '_fue_recibida', True)
        
        # Agregar observación de recepción
        obs_recepcion = Observacion.crear_con_timestamp(
            f"Radicación recibida del {self.organismo_origen.get_nombre_corto()}", 
            funcionario_id
        )
        nueva_obs = Observacion.combinar_observaciones([self.observaciones, obs_recepcion])
        object.__setattr__(self, 'observaciones', nueva_obs)
    
    def marcar_como_revisada(self, funcionario_id: str) -> None:
        """Marca la radicación como revisada"""
        if not self.puede_pasar_a_revision():
            raise ValueError(f"No se puede pasar a revisión desde estado: {self.estado.value}")
        
        self.estado = EstadoRadicacion.REVISADO
        object.__setattr__(self, 'funcionario_actual', funcionario_id.strip().upper())
        object.__setattr__(self, 'fecha_ultima_actualizacion', date.today())
    
    def completar_radicacion(self, funcionario_id: str, observaciones_finales: Optional[str] = None) -> None:
        """Completa la radicación exitosamente"""
        if not self.puede_completar_radicacion():
            raise ValueError(f"No se puede completar radicación desde estado: {self.estado.value}")
        
        self.estado = EstadoRadicacion.RADICADO
        object.__setattr__(self, 'funcionario_actual', funcionario_id.strip().upper())
        object.__setattr__(self, 'fecha_ultima_actualizacion', date.today())
        
        if observaciones_finales:
            obs_con_timestamp = self.observaciones.agregar_timestamp_automatico(funcionario_id)
            nueva_obs = Observacion.crear_desde_texto(f"{obs_con_timestamp.valor}\nCOMPLETADA: {observaciones_finales}")
            object.__setattr__(self, 'observaciones', nueva_obs)
    
    def reportar_novedad(self, funcionario_id: str, descripcion_novedad: str) -> None:
        """Reporta una novedad en la radicación"""
        if not self.puede_reportar_novedad():
            raise ValueError(f"No se puede reportar novedad desde estado: {self.estado.value}")
        
        self.estado = EstadoRadicacion.CON_NOVEDADES
        object.__setattr__(self, 'funcionario_actual', funcionario_id.strip().upper())
        object.__setattr__(self, 'fecha_ultima_actualizacion', date.today())
        
        # Agregar novedad a observaciones
        obs_con_novedad = Observacion.crear_con_timestamp(
            f"NOVEDAD REPORTADA: {descripcion_novedad}", 
            funcionario_id
        )
        nueva_obs = Observacion.combinar_observaciones([self.observaciones, obs_con_novedad])
        object.__setattr__(self, 'observaciones', nueva_obs)
    
    def resolver_novedad(self, funcionario_id: str, descripcion_resolucion: str) -> None:
        """Resuelve las novedades y vuelve a revisión"""
        if not self.puede_resolver_novedad():
            raise ValueError(f"No se puede resolver novedad desde estado: {self.estado.value}")
        
        self.estado = EstadoRadicacion.REVISADO
        object.__setattr__(self, 'funcionario_actual', funcionario_id.strip().upper())
        object.__setattr__(self, 'fecha_ultima_actualizacion', date.today())
        
        # Agregar resolución a observaciones
        obs_resolucion = Observacion.crear_con_timestamp(
            f"NOVEDAD RESUELTA: {descripcion_resolucion}", 
            funcionario_id
        )
        nueva_obs = Observacion.combinar_observaciones([self.observaciones, obs_resolucion])
        object.__setattr__(self, 'observaciones', nueva_obs)
    
    def devolver_radicacion(self, funcionario_id: str, motivo_devolucion: str, es_admin: bool = False) -> None:
        """Devuelve la radicación al organismo de origen"""
        if not self.puede_ser_devuelta(es_admin):
            raise ValueError(f"No se puede devolver radicación desde estado: {self.estado.value}")
        
        self.estado = EstadoRadicacion.DEVUELTO
        object.__setattr__(self, 'funcionario_actual', funcionario_id.strip().upper())
        object.__setattr__(self, 'fecha_ultima_actualizacion', date.today())
        
        # Agregar motivo de devolución
        obs_devolucion = Observacion.crear_con_timestamp(
            f"RADICACIÓN DEVUELTA: {motivo_devolucion}", 
            funcionario_id
        )
        nueva_obs = Observacion.combinar_observaciones([self.observaciones, obs_devolucion])
        object.__setattr__(self, 'observaciones', nueva_obs)
    
    def actualizar_observaciones(self, funcionario_id: str, nuevas_observaciones: str) -> None:
        """Actualiza las observaciones de la radicación"""
        if self.esta_en_estado_final():
            raise ValueError("No se pueden actualizar observaciones en estado final")
        
        obs_actualizacion = Observacion.crear_con_timestamp(nuevas_observaciones, funcionario_id)
        nueva_obs = Observacion.combinar_observaciones([self.observaciones, obs_actualizacion])
        object.__setattr__(self, 'observaciones', nueva_obs)
        object.__setattr__(self, 'fecha_ultima_actualizacion', date.today())

    # === MÉTODOS DE REPRESENTACIÓN ===
    
    def __str__(self) -> str:
        return f"Radicacion({self.placa} ← {self.organismo_origen.get_nombre_corto()})"
    
    def __repr__(self) -> str:
        return f"Radicacion(placa='{self.placa}', origen='{self.organismo_origen.codigo}', estado='{self.estado.value}')"

    # === FACTORY METHODS ===
    
    @classmethod
    def crear_nueva(cls, placa: Placa, organismo_origen: Ubicacion, 
                   fecha_tramite: FechaTramite, funcionario_recibe: str,
                   observaciones_iniciales: Optional[str] = None) -> 'Radicacion':
        """Factory method para crear una nueva radicación"""
        fecha_vencimiento = FechaVencimiento.calcular_desde_tramite(fecha_tramite)
        
        observaciones = Observacion.vacia()
        if observaciones_iniciales:
            observaciones = Observacion.crear_con_timestamp(observaciones_iniciales, funcionario_recibe)
        
        return cls(
            placa=placa,
            organismo_origen=organismo_origen,
            fecha_tramite=fecha_tramite,
            fecha_vencimiento=fecha_vencimiento,
            funcionario_recibe=funcionario_recibe,
            observaciones=observaciones
        )
    
    @classmethod
    def crear_desde_repositorio(cls, placa: Placa, organismo_origen: Ubicacion,
                               fecha_tramite: FechaTramite, fecha_vencimiento: FechaVencimiento,
                               funcionario_recibe: str, estado: EstadoRadicacion,
                               observaciones: Observacion, funcionario_actual: Optional[str],
                               fecha_ultima_actualizacion: Optional[date]) -> 'Radicacion':
        """Factory method para recrear radicación desde datos del repositorio"""
        radicacion = object.__new__(cls)
        
        object.__setattr__(radicacion, 'placa', placa)
        object.__setattr__(radicacion, 'organismo_origen', organismo_origen)
        object.__setattr__(radicacion, 'fecha_tramite', fecha_tramite)
        object.__setattr__(radicacion, 'fecha_vencimiento', fecha_vencimiento)
        object.__setattr__(radicacion, 'funcionario_recibe', funcionario_recibe.strip().upper())
        object.__setattr__(radicacion, 'estado', estado)
        object.__setattr__(radicacion, 'observaciones', observaciones)
        object.__setattr__(radicacion, 'funcionario_actual', funcionario_actual)
        object.__setattr__(radicacion, 'fecha_ultima_actualizacion', fecha_ultima_actualizacion)
        
        object.__setattr__(radicacion, '_domain_events', [])
        object.__setattr__(radicacion, '_initialized', True)
        
        radicacion._validar_tipos_value_objects()
        radicacion._validar_funcionario_recibe()
        radicacion._validar_fechas()
        
        return radicacion