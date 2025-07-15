from dataclasses import dataclass, field
from typing import Optional, List
from datetime import date

from app.cuentas.domain.value_objects.placa import Placa
from app.cuentas.domain.value_objects.fecha_tramite import FechaTramite
from app.cuentas.domain.value_objects.fecha_vencimiento import FechaVencimiento
from app.cuentas.domain.value_objects.ubicacion import Ubicacion
from app.cuentas.domain.value_objects.observacion import Observacion
from app.cuentas.domain.value_objects.enums.estado_traslado import EstadoTraslado
from app.cuentas.domain.events.cuenta_events import DomainEvent


@dataclass
class Traslado:
    """
    Entidad Traslado - Proceso de envío de cuenta a otro organismo.
    
    Maneja el flujo completo desde envío hasta traslado final o devolución.
    Parte del aggregate Cuenta pero con su propia identidad y ciclo de vida.
    """
    placa: Placa
    organismo_destino: Ubicacion
    fecha_tramite: FechaTramite
    fecha_vencimiento: FechaVencimiento
    funcionario_envia: str
    
    # Estado mutable del proceso
    estado: EstadoTraslado = field(default=EstadoTraslado.ENVIADO_ORGANISMO_DESTINO)
    observaciones: Observacion = field(default_factory=Observacion.vacia)
    
    # Auditoría de transiciones
    funcionario_actual: Optional[str] = field(default=None)
    fecha_ultima_actualizacion: Optional[date] = field(default=None)
    
    # Domain Events
    _domain_events: List[DomainEvent] = field(default_factory=list, init=False, repr=False)
    _initialized: bool = field(default=False, init=False, repr=False)

    def __post_init__(self):
        if self._initialized:
            return
            
        self._validar_tipos_value_objects()
        self._validar_funcionario_envia()
        self._validar_fechas()
        
        # Normalizar funcionario
        object.__setattr__(self, 'funcionario_envia', self.funcionario_envia.strip().upper())
        
        # Inicializar campos opcionales
        if self.funcionario_actual is None:
            object.__setattr__(self, 'funcionario_actual', self.funcionario_envia)
        
        if self.fecha_ultima_actualizacion is None:
            object.__setattr__(self, 'fecha_ultima_actualizacion', date.today())
        
        object.__setattr__(self, '_initialized', True)

    def _validar_tipos_value_objects(self):
        """Valida que los VOs sean del tipo correcto"""
        if not isinstance(self.placa, Placa):
            raise ValueError("La placa debe ser una instancia válida de Placa")
        
        if not isinstance(self.organismo_destino, Ubicacion):
            raise ValueError("El organismo destino debe ser una instancia válida de Ubicacion")
            
        if not isinstance(self.fecha_tramite, FechaTramite):
            raise ValueError("La fecha de trámite debe ser una instancia válida de FechaTramite")
            
        if not isinstance(self.fecha_vencimiento, FechaVencimiento):
            raise ValueError("La fecha de vencimiento debe ser una instancia válida de FechaVencimiento")
            
        if not isinstance(self.observaciones, Observacion):
            raise ValueError("Las observaciones deben ser una instancia válida de Observacion")

    def _validar_funcionario_envia(self):
        """Valida el funcionario que envía"""
        if not self.funcionario_envia or not self.funcionario_envia.strip():
            raise ValueError("El funcionario que envía no puede estar vacío")

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
    
    def get_codigo_organismo_destino(self) -> str:
        """Retorna el código del organismo destino"""
        return self.organismo_destino.codigo
    
    def get_nombre_organismo_destino(self) -> str:
        """Retorna el nombre del organismo destino"""
        return self.organismo_destino.get_nombre_corto()
    
    def get_ubicacion_completa_destino(self) -> str:
        """Retorna la ubicación completa del destino"""
        return self.organismo_destino.get_ubicacion_display()
    
    def get_dias_restantes_vencimiento(self) -> int:
        """Retorna días restantes hasta el vencimiento"""
        return self.fecha_vencimiento.dias_restantes()
    
    def get_nivel_urgencia(self) -> str:
        """Retorna el nivel de urgencia basado en vencimiento"""
        return self.fecha_vencimiento.nivel_urgencia()
    
    def get_funcionario_responsable(self) -> str:
        """Retorna el funcionario actualmente responsable"""
        return self.funcionario_actual or self.funcionario_envia
    
    def get_dias_en_proceso(self) -> int:
        """Calcula días transcurridos desde el envío"""
        return self.fecha_tramite.dias_desde_hoy() * -1 if self.fecha_tramite.es_futuro() else self.fecha_tramite.dias_desde_hoy()

    # === VALIDACIONES DE ESTADO ===
    
    def esta_vencido(self) -> bool:
        """Verifica si el traslado está vencido"""
        return self.fecha_vencimiento.esta_vencida()
    
    def esta_por_vencer(self, dias_alerta: int = 7) -> bool:
        """Verifica si está por vencer"""
        return self.fecha_vencimiento.esta_por_vencer(dias_alerta)
    
    def es_critico(self) -> bool:
        """Verifica si está en estado crítico"""
        return self.fecha_vencimiento.es_critica()
    
    def esta_en_revision(self) -> bool:
        """Verifica si está en proceso de revisión"""
        return self.estado == EstadoTraslado.REVISADO
    
    def tiene_novedades(self) -> bool:
        """Verifica si tiene novedades pendientes"""
        return self.estado == EstadoTraslado.CON_NOVEDADES
    
    def esta_completado(self) -> bool:
        """Verifica si el traslado fue completado exitosamente"""
        return self.estado == EstadoTraslado.TRASLADADO
    
    def fue_devuelto(self) -> bool:
        """Verifica si fue devuelto"""
        return self.estado == EstadoTraslado.DEVUELTO
    
    def esta_en_estado_final(self) -> bool:
        """Verifica si está en estado final (completado o devuelto)"""
        return self.estado.es_estado_final()

    # === REGLAS DE NEGOCIO - TRANSICIONES ===
    
    def puede_pasar_a_revision(self) -> bool:
        """Verifica si puede pasar a revisión"""
        return self.estado == EstadoTraslado.ENVIADO_ORGANISMO_DESTINO
    
    def puede_completar_traslado(self) -> bool:
        """Verifica si puede completar el traslado"""
        return self.estado == EstadoTraslado.REVISADO
    
    def puede_reportar_novedad(self) -> bool:
        """Verifica si puede reportar novedad"""
        return self.estado == EstadoTraslado.REVISADO
    
    def puede_resolver_novedad(self) -> bool:
        """Verifica si puede resolver novedad"""
        return self.estado == EstadoTraslado.CON_NOVEDADES
    
    def puede_ser_devuelto(self, es_admin: bool = False) -> bool:
        """Verifica si puede ser devuelto (admin puede desde cualquier estado)"""
        if es_admin:
            return not self.esta_en_estado_final()
        return self.estado.puede_transicionar_a(EstadoTraslado.DEVUELTO, es_admin)

    # === MÉTODOS DE COMANDO (Cambio de estado) ===
    
    def marcar_como_revisado(self, funcionario_id: str) -> None:
        """Marca el traslado como revisado"""
        if not self.puede_pasar_a_revision():
            raise ValueError(f"No se puede pasar a revisión desde estado: {self.estado.value}")
        
        self.estado = EstadoTraslado.REVISADO
        object.__setattr__(self, 'funcionario_actual', funcionario_id.strip().upper())
        object.__setattr__(self, 'fecha_ultima_actualizacion', date.today())
    
    def completar_traslado(self, funcionario_id: str, observaciones_finales: Optional[str] = None) -> None:
        """Completa el traslado exitosamente"""
        if not self.puede_completar_traslado():
            raise ValueError(f"No se puede completar traslado desde estado: {self.estado.value}")
        
        self.estado = EstadoTraslado.TRASLADADO
        object.__setattr__(self, 'funcionario_actual', funcionario_id.strip().upper())
        object.__setattr__(self, 'fecha_ultima_actualizacion', date.today())
        
        if observaciones_finales:
            obs_con_timestamp = self.observaciones.agregar_timestamp_automatico(funcionario_id)
            nueva_obs = Observacion.crear_desde_texto(f"{obs_con_timestamp.valor}\nCOMPLETADO: {observaciones_finales}")
            object.__setattr__(self, 'observaciones', nueva_obs)
    
    def reportar_novedad(self, funcionario_id: str, descripcion_novedad: str) -> None:
        """Reporta una novedad en el traslado"""
        if not self.puede_reportar_novedad():
            raise ValueError(f"No se puede reportar novedad desde estado: {self.estado.value}")
        
        self.estado = EstadoTraslado.CON_NOVEDADES
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
        
        self.estado = EstadoTraslado.REVISADO
        object.__setattr__(self, 'funcionario_actual', funcionario_id.strip().upper())
        object.__setattr__(self, 'fecha_ultima_actualizacion', date.today())
        
        # Agregar resolución a observaciones
        obs_resolucion = Observacion.crear_con_timestamp(
            f"NOVEDAD RESUELTA: {descripcion_resolucion}", 
            funcionario_id
        )
        nueva_obs = Observacion.combinar_observaciones([self.observaciones, obs_resolucion])
        object.__setattr__(self, 'observaciones', nueva_obs)
    
    def devolver_traslado(self, funcionario_id: str, motivo_devolucion: str, es_admin: bool = False) -> None:
        """Devuelve el traslado al organismo de origen"""
        if not self.puede_ser_devuelto(es_admin):
            raise ValueError(f"No se puede devolver traslado desde estado: {self.estado.value}")
        
        self.estado = EstadoTraslado.DEVUELTO
        object.__setattr__(self, 'funcionario_actual', funcionario_id.strip().upper())
        object.__setattr__(self, 'fecha_ultima_actualizacion', date.today())
        
        # Agregar motivo de devolución
        obs_devolucion = Observacion.crear_con_timestamp(
            f"TRASLADO DEVUELTO: {motivo_devolucion}", 
            funcionario_id
        )
        nueva_obs = Observacion.combinar_observaciones([self.observaciones, obs_devolucion])
        object.__setattr__(self, 'observaciones', nueva_obs)
    
    def actualizar_observaciones(self, funcionario_id: str, nuevas_observaciones: str) -> None:
        """Actualiza las observaciones del traslado"""
        if self.esta_en_estado_final():
            raise ValueError("No se pueden actualizar observaciones en estado final")
        
        obs_actualizacion = Observacion.crear_con_timestamp(nuevas_observaciones, funcionario_id)
        nueva_obs = Observacion.combinar_observaciones([self.observaciones, obs_actualizacion])
        object.__setattr__(self, 'observaciones', nueva_obs)
        object.__setattr__(self, 'fecha_ultima_actualizacion', date.today())

    # === MÉTODOS DE REPRESENTACIÓN ===
    
    def __str__(self) -> str:
        return f"Traslado({self.placa} → {self.organismo_destino.get_nombre_corto()})"
    
    def __repr__(self) -> str:
        return f"Traslado(placa='{self.placa}', destino='{self.organismo_destino.codigo}', estado='{self.estado.value}')"

    # === FACTORY METHODS ===
    
    @classmethod
    def crear_nuevo(cls, placa: Placa, organismo_destino: Ubicacion, 
                   fecha_tramite: FechaTramite, funcionario_envia: str,
                   observaciones_iniciales: Optional[str] = None) -> 'Traslado':
        """Factory method para crear un nuevo traslado"""
        fecha_vencimiento = FechaVencimiento.calcular_desde_tramite(fecha_tramite)
        
        observaciones = Observacion.vacia()
        if observaciones_iniciales:
            observaciones = Observacion.crear_con_timestamp(observaciones_iniciales, funcionario_envia)
        
        return cls(
            placa=placa,
            organismo_destino=organismo_destino,
            fecha_tramite=fecha_tramite,
            fecha_vencimiento=fecha_vencimiento,
            funcionario_envia=funcionario_envia,
            observaciones=observaciones
        )
    
    @classmethod
    def crear_desde_repositorio(cls, placa: Placa, organismo_destino: Ubicacion,
                               fecha_tramite: FechaTramite, fecha_vencimiento: FechaVencimiento,
                               funcionario_envia: str, estado: EstadoTraslado,
                               observaciones: Observacion, funcionario_actual: Optional[str],
                               fecha_ultima_actualizacion: Optional[date]) -> 'Traslado':
        """Factory method para recrear traslado desde datos del repositorio"""
        traslado = object.__new__(cls)
        
        object.__setattr__(traslado, 'placa', placa)
        object.__setattr__(traslado, 'organismo_destino', organismo_destino)
        object.__setattr__(traslado, 'fecha_tramite', fecha_tramite)
        object.__setattr__(traslado, 'fecha_vencimiento', fecha_vencimiento)
        object.__setattr__(traslado, 'funcionario_envia', funcionario_envia.strip().upper())
        object.__setattr__(traslado, 'estado', estado)
        object.__setattr__(traslado, 'observaciones', observaciones)
        object.__setattr__(traslado, 'funcionario_actual', funcionario_actual)
        object.__setattr__(traslado, 'fecha_ultima_actualizacion', fecha_ultima_actualizacion)
        
        object.__setattr__(traslado, '_domain_events', [])
        object.__setattr__(traslado, '_initialized', True)
        
        traslado._validar_tipos_value_objects()
        traslado._validar_funcionario_envia()
        traslado._validar_fechas()
        
        return traslado