from dataclasses import dataclass, field
from typing import Optional, List
from datetime import date

from app.cuentas.domain.value_objects.placa import Placa
from app.cuentas.domain.value_objects.numero_cuenta import NumeroCuenta
from app.cuentas.domain.value_objects.fecha_creacion import FechaCreacion
from app.cuentas.domain.value_objects.funcionario import Funcionario
from app.cuentas.domain.value_objects.historial_asignacion import HistorialAsignacion
from app.cuentas.domain.value_objects.enums.tipo_servicio import TipoServicio
from app.cuentas.domain.value_objects.enums.estado_cuenta import EstadoCuenta
from app.cuentas.domain.value_objects.enums.tipo_proceso_anterior import TipoProcesoAnterior
from app.cuentas.domain.events.cuenta_events import (
    CuentaCreadaEvent, ProcesoIniciadoEvent, ProcesoCompletadoEvent,
    CuentaReasignadaEvent, CuentaInactivadaEvent, CuentaReactivadaEvent
)


@dataclass
class Cuenta:
    """
    Entidad Cuenta - Aggregate Root del bounded context.
    
    Representa una cuenta de vehículo que puede tener procesos de
    traslado (envío) o radicación (recepción), pero nunca ambos simultáneamente.
    
    Reglas de negocio críticas:
    - Placa como identidad única
    - Un solo proceso activo (traslado XOR radicación)
    - Lógica origen/destino basada en historial
    - Trazabilidad completa de funcionarios (AUDITORÍA COMPLETA)
    - Inmutabilidad de estado interno
    """
    placa: Placa
    numero_cuenta: NumeroCuenta
    tipo_servicio: TipoServicio
    fecha_creacion: FechaCreacion
    funcionario_creador: str

    """Campos mutables controlados"""
    estado: EstadoCuenta = field(default=EstadoCuenta.ACTIVA)
    historial_asignaciones: List[HistorialAsignacion] = field(default_factory=list)

    """Domain Events (para notificar a otros bounded contexts)"""
    _domain_events: List = field(default_factory=list, init=False, repr=False)
    
    """Estado interno privado (inmutable después de inicialización)"""
    _tipo_proceso_anterior: TipoProcesoAnterior = field(default=None, init=False, repr=False)
    _proceso_traslado_activo: bool = field(default=False, init=False, repr=False)
    _proceso_radicacion_activo: bool = field(default=False, init=False, repr=False)
    _initialized: bool = field(default=False, init=False, repr=False)

    def __post_init__(self):
        if self._initialized:
            return 
              
        self._validar_tipos_value_objects()
        self._validar_funcionario_creador()

        object.__setattr__(self, 'funcionario_creador', self.funcionario_creador.strip().upper())
        
        if self._tipo_proceso_anterior is None:
            object.__setattr__(self, '_tipo_proceso_anterior', TipoProcesoAnterior.NINGUNO)
        
        self._crear_asignacion_inicial_si_necesaria()
        
        self._validar_coherencia_estado()
        
        object.__setattr__(self, '_initialized', True)
        
        if len(self.historial_asignaciones) == 1 and self.historial_asignaciones[0].es_asignacion_inicial():
            self._add_domain_event(CuentaCreadaEvent.create(
                placa=str(self.placa),
                numero_cuenta=str(self.numero_cuenta),
                tipo_servicio=self.tipo_servicio.value,
                funcionario_creador=self.funcionario_creador
            ))

    def _validar_tipos_value_objects(self):
        """Valida que los VOs sean del tipo correcto"""
        if not isinstance(self.placa, Placa):
            raise ValueError("La placa debe ser una instancia válida de Placa")
        
        if not isinstance(self.numero_cuenta, NumeroCuenta):
            raise ValueError("El número de cuenta debe ser una instancia válida de NumeroCuenta")
        
        if not isinstance(self.fecha_creacion, FechaCreacion):
            raise ValueError("La fecha de creación debe ser una instancia válida de FechaCreacion")

    def _validar_funcionario_creador(self):
        """Valida el funcionario creador"""
        if not self.funcionario_creador or not self.funcionario_creador.strip():
            raise ValueError("El funcionario creador no puede estar vacío")

    def _crear_asignacion_inicial_si_necesaria(self):
        """Crea la asignación inicial si no existe"""
        if not self.historial_asignaciones:
            asignacion_inicial = HistorialAsignacion.crear_asignacion_inicial(
                funcionario_id=self.funcionario_creador,
                fecha=self.fecha_creacion.fecha
            )
            self.historial_asignaciones.append(asignacion_inicial)

    def _validar_coherencia_estado(self):
        """Valida que el estado sea coherente con los procesos activos"""
        if self.estado == EstadoCuenta.EN_TRASLADO and not self._proceso_traslado_activo:
            raise ValueError("Estado EN_TRASLADO requiere proceso de traslado activo")
        
        if self.estado == EstadoCuenta.EN_RADICACION and not self._proceso_radicacion_activo:
            raise ValueError("Estado EN_RADICACION requiere proceso de radicación activo")
        
        if self._proceso_traslado_activo and self._proceso_radicacion_activo:
            raise ValueError("No puede tener ambos procesos activos simultáneamente")
        
        if (self.estado in [EstadoCuenta.ACTIVA, EstadoCuenta.INACTIVA] and 
            (self._proceso_traslado_activo or self._proceso_radicacion_activo)):
            raise ValueError("Estado ACTIVA/INACTIVA no debe tener procesos activos")

    def _add_domain_event(self, event):
        """Agrega un evento de dominio"""
        self._domain_events.append(event)

    def get_domain_events(self) -> List:
        """Retorna y limpia los eventos de dominio pendientes"""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events

    """PROPIEDADES PARA ACCESO CONTROLADO AL ESTADO INTERNO"""

    @property
    def tipo_proceso_anterior(self) -> TipoProcesoAnterior:
        """Tipo de proceso anterior (solo lectura)"""
        return self._tipo_proceso_anterior

    @property
    def proceso_traslado_activo(self) -> bool:
        """Estado del proceso de traslado (solo lectura)"""
        return self._proceso_traslado_activo

    @property 
    def proceso_radicacion_activo(self) -> bool:
        """Estado del proceso de radicación (solo lectura)"""
        return self._proceso_radicacion_activo

    """MÉTODOS DE CONSULTA (Getters)"""

    def get_placa_valor(self) -> str:
        """Retorna el valor de la placa como string"""
        return str(self.placa)

    def get_numero_cuenta_valor(self) -> str:
        """Retorna el número de cuenta como string"""
        return str(self.numero_cuenta)

    def get_funcionario_actual(self) -> str:
        """Retorna el ID del funcionario actualmente asignado"""
        if not self.historial_asignaciones:
            return self.funcionario_creador
        return self.historial_asignaciones[-1].funcionario_id

    def get_fecha_ultima_asignacion(self) -> date:
        """Retorna la fecha de la última asignación"""
        if not self.historial_asignaciones:
            return self.fecha_creacion.fecha
        return self.historial_asignaciones[-1].fecha_asignacion

    def get_tipo_vehiculo(self) -> str:
        """Retorna el tipo de vehículo basado en la placa"""
        return self.placa.get_tipo_vehiculo()

    def get_edad_cuenta_dias(self) -> int:
        """Retorna la edad de la cuenta en días"""
        return self.fecha_creacion.dias_desde_creacion()

    def tiene_proceso_activo(self) -> bool:
        """Verifica si tiene algún proceso activo"""
        return self._proceso_traslado_activo or self._proceso_radicacion_activo

    def tiene_traslado_activo(self) -> bool:
        """Verifica si tiene traslado activo"""
        return self._proceso_traslado_activo

    def tiene_radicacion_activa(self) -> bool:
        """Verifica si tiene radicación activa"""
        return self._proceso_radicacion_activo

    def esta_activa(self) -> bool:
        """Verifica si la cuenta está en estado activo"""
        return self.estado == EstadoCuenta.ACTIVA

    def esta_inactiva(self) -> bool:
        """Verifica si la cuenta está inactiva"""
        return self.estado == EstadoCuenta.INACTIVA

    def get_descripcion_proceso_anterior(self) -> str:
        """Retorna descripción del proceso anterior"""
        return self._tipo_proceso_anterior.get_descripcion()

    def get_numero_asignaciones(self) -> int:
        """Retorna el número total de asignaciones"""
        return len(self.historial_asignaciones)

    def get_asignaciones_por_tipo(self, tipo: str) -> List[HistorialAsignacion]:
        """Retorna asignaciones filtradas por tipo"""
        from app.cuentas.domain.value_objects.historial_asignacion import TipoAsignacion
        
        try:
            tipo_enum = TipoAsignacion(tipo.lower())
            return [h for h in self.historial_asignaciones if h.tipo_asignacion == tipo_enum]
        except ValueError:
            return []
        
    """REGLAS DE NEGOCIO - LÓGICA ORIGEN/DESTINO"""

    def puede_iniciar_traslado(self) -> bool:
        """
        Verifica si puede iniciar un proceso de traslado.
        
        Usa el enum TipoProcesoAnterior para determinar permisos.
        """
        if self.tiene_proceso_activo() or self.esta_inactiva():
            return False
        
        return self._tipo_proceso_anterior.permite_traslado()

    def puede_iniciar_radicacion(self) -> bool:
        """
        Verifica si puede iniciar un proceso de radicación.
        
        Usa el enum TipoProcesoAnterior para determinar permisos.
        """
        if self.tiene_proceso_activo() or self.esta_inactiva():
            return False
        
        return self._tipo_proceso_anterior.permite_radicacion()

    def get_razon_no_puede_trasladar(self) -> Optional[str]:
        """Retorna la razón específica por la cual no puede iniciar traslado"""
        if self.puede_iniciar_traslado():
            return None
        
        if self.tiene_proceso_activo():
            if self.tiene_traslado_activo():
                return "Ya tiene un proceso de traslado activo"
            else:
                return "Ya tiene un proceso de radicación activo"
        
        if self.esta_inactiva():
            return "La cuenta está inactiva"
        
        if not self._tipo_proceso_anterior.permite_traslado():
            if self._tipo_proceso_anterior == TipoProcesoAnterior.TRASLADO_COMPLETADO:
                return "Esta placa ya fue enviada a otro organismo, solo puede recibir radicaciones"
            else:
                return f"Proceso anterior ({self._tipo_proceso_anterior.get_descripcion()}) no permite traslados"
        
        return "No se puede determinar la razón"

    def get_razon_no_puede_radicar(self) -> Optional[str]:
        """Retorna la razón específica por la cual no puede iniciar radicación"""
        if self.puede_iniciar_radicacion():
            return None
        
        if self.tiene_proceso_activo():
            if self.tiene_radicacion_activa():
                return "Ya tiene un proceso de radicación activo"
            else:
                return "Ya tiene un proceso de traslado activo"
        
        if self.esta_inactiva():
            return "La cuenta está inactiva"
        
        if not self._tipo_proceso_anterior.permite_radicacion():
            if self._tipo_proceso_anterior == TipoProcesoAnterior.RADICACION_COMPLETADA:
                return "Esta placa ya llegó de otro organismo, solo puede enviar traslados"
            else:
                return f"Proceso anterior ({self._tipo_proceso_anterior.get_descripcion()}) no permite radicaciones"
        
        return "No se puede determinar la razón"

    def get_procesos_permitidos(self) -> List[str]:
        """Retorna lista de procesos permitidos actualmente"""
        procesos = []
        if self.puede_iniciar_traslado():
            procesos.append("traslado")
        if self.puede_iniciar_radicacion():
            procesos.append("radicacion")
        return procesos

    """MÉTODOS DE COMANDO (Cambio de estado) - CON AUDITORÍA COMPLETA"""

    def iniciar_proceso_traslado(self, funcionario_id: str) -> None:
        """Inicia un proceso de traslado"""
        if not self.puede_iniciar_traslado():
            razon = self.get_razon_no_puede_trasladar()
            raise ValueError(f"No se puede iniciar traslado: {razon}")
        
        object.__setattr__(self, '_proceso_traslado_activo', True)
        self.estado = EstadoCuenta.EN_TRASLADO
        
        # 🔥 AUDITORÍA COMPLETA: SIEMPRE registrar operación de inicio
        asignacion = HistorialAsignacion.crear_cambio_proceso(
            funcionario_id, "traslado", "inicio"
        )
        self.historial_asignaciones.append(asignacion)
        
        self._add_domain_event(ProcesoIniciadoEvent.create(
            placa=str(self.placa),
            tipo_proceso="traslado",
            funcionario=funcionario_id,
            numero_cuenta=str(self.numero_cuenta)
        ))

    def iniciar_proceso_radicacion(self, funcionario_id: str) -> None:
        """Inicia un proceso de radicación"""
        if not self.puede_iniciar_radicacion():
            razon = self.get_razon_no_puede_radicar()
            raise ValueError(f"No se puede iniciar radicación: {razon}")
        
        object.__setattr__(self, '_proceso_radicacion_activo', True)
        self.estado = EstadoCuenta.EN_RADICACION
        
        # 🔥 AUDITORÍA COMPLETA: SIEMPRE registrar operación de inicio
        asignacion = HistorialAsignacion.crear_cambio_proceso(
            funcionario_id, "radicacion", "inicio"
        )
        self.historial_asignaciones.append(asignacion)
        
        self._add_domain_event(ProcesoIniciadoEvent.create(
            placa=str(self.placa),
            tipo_proceso="radicacion",
            funcionario=funcionario_id,
            numero_cuenta=str(self.numero_cuenta)
        ))

    def completar_proceso_traslado(self, funcionario_id: str) -> None:
        """Completa un proceso de traslado exitosamente"""
        if not self.tiene_traslado_activo():
            raise ValueError("No hay proceso de traslado activo para completar")
        
        object.__setattr__(self, '_proceso_traslado_activo', False)
        object.__setattr__(self, '_tipo_proceso_anterior', TipoProcesoAnterior.TRASLADO_COMPLETADO)
        self.estado = EstadoCuenta.ACTIVA
        
        # 🔥 AUDITORÍA COMPLETA: SIEMPRE registrar operación de completar
        asignacion = HistorialAsignacion.crear_cambio_proceso(
            funcionario_id, "traslado", "completar"
        )
        self.historial_asignaciones.append(asignacion)

        self._add_domain_event(ProcesoCompletadoEvent.create(
            placa=str(self.placa),
            tipo_proceso="traslado",
            funcionario=funcionario_id,
            numero_cuenta=str(self.numero_cuenta),
            resultado="completado"
        ))

    def completar_proceso_radicacion(self, funcionario_id: str) -> None:
        """Completa un proceso de radicación exitosamente"""
        if not self.tiene_radicacion_activa():
            raise ValueError("No hay proceso de radicación activo para completar")
        
        object.__setattr__(self, '_proceso_radicacion_activo', False)
        object.__setattr__(self, '_tipo_proceso_anterior', TipoProcesoAnterior.RADICACION_COMPLETADA)
        self.estado = EstadoCuenta.ACTIVA

        # 🔥 AUDITORÍA COMPLETA: SIEMPRE registrar operación de completar
        asignacion = HistorialAsignacion.crear_cambio_proceso(
            funcionario_id, "radicacion", "completar"
        )
        self.historial_asignaciones.append(asignacion)
        
        self._add_domain_event(ProcesoCompletadoEvent.create(
            placa=str(self.placa),
            tipo_proceso="radicacion",
            funcionario=funcionario_id,
            numero_cuenta=str(self.numero_cuenta),
            resultado="completado"
        ))

    def devolver_proceso_traslado(self, funcionario_id: str, motivo: str) -> None:
        """Devuelve un proceso de traslado (cancelación administrativa)"""
        if not self.tiene_traslado_activo():
            raise ValueError("No hay proceso de traslado activo para devolver")
        
        object.__setattr__(self, '_proceso_traslado_activo', False)
        object.__setattr__(self, '_tipo_proceso_anterior', TipoProcesoAnterior.TRASLADO_DEVUELTO)
        self.estado = EstadoCuenta.ACTIVA
        
        # ✅ Ya registra siempre (sin cambios)
        asignacion = HistorialAsignacion.crear_cambio_proceso(
            funcionario_id, "traslado", "devolver", motivo
        )
        self.historial_asignaciones.append(asignacion)
        
        self._add_domain_event(ProcesoCompletadoEvent.create(
            placa=str(self.placa),
            tipo_proceso="traslado",
            funcionario=funcionario_id,
            numero_cuenta=str(self.numero_cuenta),
            resultado="devuelto",
            motivo_devolucion=motivo
        ))

    def devolver_proceso_radicacion(self, funcionario_id: str, motivo: str) -> None:
        """Devuelve un proceso de radicación (cancelación administrativa)"""
        if not self.tiene_radicacion_activa():
            raise ValueError("No hay proceso de radicación activo para devolver")
        
        object.__setattr__(self, '_proceso_radicacion_activo', False)
        object.__setattr__(self, '_tipo_proceso_anterior', TipoProcesoAnterior.RADICACION_DEVUELTA)
        self.estado = EstadoCuenta.ACTIVA
        
        # ✅ Ya registra siempre (sin cambios)
        asignacion = HistorialAsignacion.crear_cambio_proceso(
            funcionario_id, "radicacion", "devolver", motivo
        )
        self.historial_asignaciones.append(asignacion)
        
        self._add_domain_event(ProcesoCompletadoEvent.create(
            placa=str(self.placa),
            tipo_proceso="radicacion",
            funcionario=funcionario_id,
            numero_cuenta=str(self.numero_cuenta),
            resultado="devuelto",
            motivo_devolucion=motivo
        ))

    def inactivar_cuenta(self, funcionario_id: str, motivo: str) -> None:
        """Inactiva la cuenta (solo si no tiene procesos activos)"""
        if self.tiene_proceso_activo():
            raise ValueError("No se puede inactivar una cuenta con procesos activos")
        
        self.estado = EstadoCuenta.INACTIVA
        
        # ✅ Ya registra siempre (sin cambios)
        asignacion = HistorialAsignacion.crear_inactivacion(funcionario_id, motivo)
        self.historial_asignaciones.append(asignacion)
        
        self._add_domain_event(CuentaInactivadaEvent.create(
            placa=str(self.placa),
            funcionario=funcionario_id,
            motivo=motivo
        ))

    def reactivar_cuenta(self, funcionario_id: str) -> None:
        """Reactiva una cuenta inactiva"""
        if self.estado != EstadoCuenta.INACTIVA:
            raise ValueError("Solo se pueden reactivar cuentas inactivas")
        
        self.estado = EstadoCuenta.ACTIVA
        
        # ✅ Ya registra siempre (sin cambios)
        asignacion = HistorialAsignacion.crear_reactivacion(funcionario_id)
        self.historial_asignaciones.append(asignacion)
        
        self._add_domain_event(CuentaReactivadaEvent.create(
            placa=str(self.placa),
            funcionario=funcionario_id
        ))

    def reasignar_funcionario(self, nuevo_funcionario_id: str, funcionario_autoriza: str, 
                            motivo: str = "reasignacion", observaciones: Optional[str] = None) -> None:
        """Reasigna la cuenta a otro funcionario"""
        funcionario_anterior = self.get_funcionario_actual()
        
        if nuevo_funcionario_id.upper() == funcionario_anterior:
            raise ValueError("El funcionario ya está asignado a esta cuenta")
        
        # ✅ Mantiene lógica original (solo para cambios reales de funcionario)
        asignacion = HistorialAsignacion.crear_reasignacion_manual(
            funcionario_id=nuevo_funcionario_id,
            funcionario_asigna=funcionario_autoriza,
            motivo=motivo,
            observaciones=observaciones
        )
        self.historial_asignaciones.append(asignacion)
        
        self._add_domain_event(CuentaReasignadaEvent.create(
            placa=str(self.placa),
            funcionario_anterior=funcionario_anterior,
            funcionario_nuevo=nuevo_funcionario_id,
            funcionario_autoriza=funcionario_autoriza,
            motivo=motivo
        ))

    """MÉTODOS DE REPRESENTACIÓN"""

    def __str__(self) -> str:
        return f"Cuenta({self.placa} - {self.numero_cuenta})"

    def __repr__(self) -> str:
        estado_proceso = "sin_proceso"
        if self.tiene_traslado_activo():
            estado_proceso = "traslado_activo"
        elif self.tiene_radicacion_activa():
            estado_proceso = "radicacion_activa"
        
        return f"Cuenta(placa='{self.placa}', numero='{self.numero_cuenta}', estado='{self.estado.value}', proceso='{estado_proceso}')"

    """FACTORY METHODS"""
    @classmethod
    def crear_nueva_cuenta(cls, placa: Placa, tipo_servicio: TipoServicio, 
                          funcionario_creador: str, 
                          consecutivo_cuenta: Optional[int] = None) -> 'Cuenta':
        """Factory method para crear una nueva cuenta"""
        if consecutivo_cuenta is not None:
            numero_cuenta = NumeroCuenta.generar_para_hoy(consecutivo_cuenta)
        else:
            numero_cuenta = NumeroCuenta.generar_para_hoy(1)
        
        fecha_creacion = FechaCreacion.crear_hoy()
        
        return cls(
            placa=placa,
            numero_cuenta=numero_cuenta,
            tipo_servicio=tipo_servicio,
            fecha_creacion=fecha_creacion,
            funcionario_creador=funcionario_creador,
            estado=EstadoCuenta.ACTIVA
        )

    @classmethod
    def crear_desde_repositorio(cls, placa: Placa, numero_cuenta: NumeroCuenta,
                               tipo_servicio: TipoServicio, estado: EstadoCuenta,
                               fecha_creacion: FechaCreacion, funcionario_creador: str,
                               historial: List[HistorialAsignacion],
                               tipo_proceso_anterior: TipoProcesoAnterior = TipoProcesoAnterior.NINGUNO,
                               proceso_traslado_activo: bool = False,
                               proceso_radicacion_activo: bool = False) -> 'Cuenta':
        
        """Factory method para recrear cuenta desde datos del repositorio"""
        cuenta = object.__new__(cls)
        
        object.__setattr__(cuenta, 'placa', placa)
        object.__setattr__(cuenta, 'numero_cuenta', numero_cuenta)
        object.__setattr__(cuenta, 'tipo_servicio', tipo_servicio)
        object.__setattr__(cuenta, 'fecha_creacion', fecha_creacion)
        object.__setattr__(cuenta, 'funcionario_creador', funcionario_creador.strip().upper())
        object.__setattr__(cuenta, 'estado', estado)
        object.__setattr__(cuenta, 'historial_asignaciones', historial.copy())
        
        object.__setattr__(cuenta, '_domain_events', [])
        object.__setattr__(cuenta, '_tipo_proceso_anterior', tipo_proceso_anterior)
        object.__setattr__(cuenta, '_proceso_traslado_activo', proceso_traslado_activo)
        object.__setattr__(cuenta, '_proceso_radicacion_activo', proceso_radicacion_activo)
        object.__setattr__(cuenta, '_initialized', True)
        
        cuenta._validar_tipos_value_objects()
        cuenta._validar_funcionario_creador()
        
        cuenta._validar_coherencia_estado()
        
        return cuenta