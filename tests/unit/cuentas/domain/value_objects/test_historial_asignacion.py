import pytest
from datetime import date, timedelta
from app.cuentas.domain.value_objects.historial_asignacion import HistorialAsignacion, TipoAsignacion


class TestTipoAsignacion:
    """Tests para el enum TipoAsignacion"""
    
    def test_valores_enum_correctos(self):
        """Verificar que los valores del enum son correctos"""
        assert TipoAsignacion.CREACION.value == "creacion"
        assert TipoAsignacion.REASIGNACION.value == "reasignacion"
        assert TipoAsignacion.INICIO_PROCESO.value == "inicio_proceso"
        assert TipoAsignacion.COMPLETAR_PROCESO.value == "completar_proceso"
        assert TipoAsignacion.DEVOLVER_PROCESO.value == "devolver_proceso"
        assert TipoAsignacion.INACTIVACION.value == "inactivacion"
        assert TipoAsignacion.REACTIVACION.value == "reactivacion"
    
    def test_enum_es_inmutable(self):
        """Verificar que los valores del enum no se pueden cambiar"""
        with pytest.raises(AttributeError):
            TipoAsignacion.CREACION.value = "nuevo_valor"
    
    def test_todos_los_tipos_disponibles(self):
        """Verificar que tenemos todos los tipos necesarios"""
        tipos_esperados = [
            "creacion", "reasignacion", "inicio_proceso", 
            "completar_proceso", "devolver_proceso", 
            "inactivacion", "reactivacion"
        ]
        tipos_reales = [tipo.value for tipo in TipoAsignacion]
        assert len(tipos_reales) == 7
        for tipo in tipos_esperados:
            assert tipo in tipos_reales


class TestHistorialAsignacionCreacion:
    """Tests para creación de historial de asignación"""
    
    def test_crear_historial_basico(self):
        """Test crear historial básico válido"""
        hoy = date.today()
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=hoy,
            motivo="Asignación inicial"
        )
        assert historial.funcionario_id == "FUNC001"
        assert historial.fecha_asignacion == hoy
        assert historial.motivo == "Asignación inicial"
        assert historial.funcionario_asigna is None
        assert historial.observaciones is None
    
    def test_crear_historial_completo(self):
        """Test crear historial con todos los campos"""
        hoy = date.today()
        historial = HistorialAsignacion(
            funcionario_id="func002",
            fecha_asignacion=hoy,
            motivo="Reasignación por carga de trabajo",
            funcionario_asigna="SUPERVISOR01",
            tipo_asignacion=TipoAsignacion.REASIGNACION,
            observaciones="Funcionario anterior de vacaciones"
        )
        assert historial.funcionario_id == "FUNC002"  # Normalizado
        assert historial.funcionario_asigna == "SUPERVISOR01"
        assert historial.tipo_asignacion == TipoAsignacion.REASIGNACION
        assert historial.observaciones == "Funcionario anterior de vacaciones"
    
    def test_normalizacion_funcionario_id(self):
        """Test normalización de funcionario_id"""
        historial = HistorialAsignacion(
            funcionario_id="  func003  ",
            fecha_asignacion=date.today(),
            motivo="test"
        )
        assert historial.funcionario_id == "FUNC003"
    
    def test_normalizacion_motivo(self):
        """Test normalización de motivo"""
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=date.today(),
            motivo="  Motivo con espacios  "
        )
        assert historial.motivo == "Motivo con espacios"
    
    def test_normalizacion_funcionario_asigna(self):
        """Test normalización de funcionario_asigna"""
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=date.today(),
            motivo="test",
            funcionario_asigna="  supervisor01  "
        )
        assert historial.funcionario_asigna == "SUPERVISOR01"
    
    def test_normalizacion_observaciones(self):
        """Test normalización de observaciones"""
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=date.today(),
            motivo="test",
            observaciones="  Observación con espacios  "
        )
        assert historial.observaciones == "Observación con espacios"


class TestHistorialAsignacionValidaciones:
    """Tests para validaciones de entrada"""
    
    def test_funcionario_id_vacio_error(self):
        """Test que funcionario_id vacío genera error"""
        with pytest.raises(ValueError, match="ID del funcionario no puede estar vacío"):
            HistorialAsignacion(
                funcionario_id="",
                fecha_asignacion=date.today(),
                motivo="test"
            )
    
    def test_funcionario_id_solo_espacios_error(self):
        """Test que funcionario_id con solo espacios genera error"""
        with pytest.raises(ValueError, match="ID del funcionario no puede estar vacío"):
            HistorialAsignacion(
                funcionario_id="   ",
                fecha_asignacion=date.today(),
                motivo="test"
            )
    
    def test_fecha_asignacion_tipo_invalido_error(self):
        """Test que fecha de tipo inválido genera error"""
        with pytest.raises(ValueError, match="debe ser un objeto date"):
            HistorialAsignacion(
                funcionario_id="FUNC001",
                fecha_asignacion="2024-12-04",
                motivo="test"
            )
    
    def test_fecha_asignacion_none_error(self):
        """Test que fecha None genera error"""
        with pytest.raises(ValueError, match="debe ser un objeto date"):
            HistorialAsignacion(
                funcionario_id="FUNC001",
                fecha_asignacion=None,
                motivo="test"
            )
    
    def test_motivo_vacio_error(self):
        """Test que motivo vacío genera error"""
        with pytest.raises(ValueError, match="motivo de asignación no puede estar vacío"):
            HistorialAsignacion(
                funcionario_id="FUNC001",
                fecha_asignacion=date.today(),
                motivo=""
            )
    
    def test_motivo_solo_espacios_error(self):
        """Test que motivo con solo espacios genera error"""
        with pytest.raises(ValueError, match="motivo de asignación no puede estar vacío"):
            HistorialAsignacion(
                funcionario_id="FUNC001",
                fecha_asignacion=date.today(),
                motivo="   "
            )
    
    def test_motivo_muy_largo_error(self):
        """Test que motivo muy largo genera error"""
        motivo_largo = "a" * 501
        with pytest.raises(ValueError, match="motivo no puede exceder 500 caracteres"):
            HistorialAsignacion(
                funcionario_id="FUNC001",
                fecha_asignacion=date.today(),
                motivo=motivo_largo
            )
    
    def test_observaciones_muy_largas_error(self):
        """Test que observaciones muy largas generan error"""
        observaciones_largas = "a" * 1001
        with pytest.raises(ValueError, match="observaciones no pueden exceder 1000 caracteres"):
            HistorialAsignacion(
                funcionario_id="FUNC001",
                fecha_asignacion=date.today(),
                motivo="test",
                observaciones=observaciones_largas
            )
    
    def test_fecha_futura_error(self):
        """Test que fecha futura genera error"""
        mañana = date.today() + timedelta(days=1)
        with pytest.raises(ValueError, match="fecha de asignación no puede ser futura"):
            HistorialAsignacion(
                funcionario_id="FUNC001",
                fecha_asignacion=mañana,
                motivo="test"
            )
    
    def test_motivo_limite_exacto_valido(self):
        """Test que motivo de 500 caracteres exactos es válido"""
        motivo_limite = "a" * 500
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=date.today(),
            motivo=motivo_limite
        )
        assert len(historial.motivo) == 500
    
    def test_observaciones_limite_exacto_validas(self):
        """Test que observaciones de 1000 caracteres exactos son válidas"""
        observaciones_limite = "a" * 1000
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=date.today(),
            motivo="test",
            observaciones=observaciones_limite
        )
        assert len(historial.observaciones) == 1000


class TestDeteccionTipoAsignacion:
    """Tests para detección automática de tipo de asignación"""
    
    def test_detectar_creacion(self):
        """Test detección automática de tipo CREACION"""
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=date.today(),
            motivo="creacion"
        )
        assert historial.tipo_asignacion == TipoAsignacion.CREACION
    
    def test_detectar_reasignacion(self):
        """Test detección automática de tipo REASIGNACION"""
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=date.today(),
            motivo="reasignacion"
        )
        assert historial.tipo_asignacion == TipoAsignacion.REASIGNACION
    
    def test_detectar_inicio_proceso(self):
        """Test detección automática de tipo INICIO_PROCESO"""
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=date.today(),
            motivo="inicio traslado"
        )
        assert historial.tipo_asignacion == TipoAsignacion.INICIO_PROCESO
    
    def test_detectar_completar_proceso(self):
        """Test detección automática de tipo COMPLETAR_PROCESO"""
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=date.today(),
            motivo="completar radicación"
        )
        assert historial.tipo_asignacion == TipoAsignacion.COMPLETAR_PROCESO
    
    def test_detectar_devolver_proceso(self):
        """Test detección automática de tipo DEVOLVER_PROCESO"""
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=date.today(),
            motivo="devolver por documentos incorrectos"
        )
        assert historial.tipo_asignacion == TipoAsignacion.DEVOLVER_PROCESO
    
    def test_detectar_inactivacion(self):
        """Test detección automática de tipo INACTIVACION"""
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=date.today(),
            motivo="inactivar cuenta duplicada"
        )
        assert historial.tipo_asignacion == TipoAsignacion.INACTIVACION
    
    def test_detectar_reactivacion(self):
        """Test detección automática de tipo REACTIVACION"""
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=date.today(),
            motivo="reactivar"
        )
        assert historial.tipo_asignacion == TipoAsignacion.REACTIVACION
    
    def test_detectar_reasignacion_por_defecto(self):
        """Test que motivos desconocidos se clasifican como REASIGNACION"""
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=date.today(),
            motivo="motivo desconocido"
        )
        assert historial.tipo_asignacion == TipoAsignacion.REASIGNACION
    
    def test_tipo_explicito_prevalece(self):
        """Test que tipo explícito prevalece sobre detección automática"""
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=date.today(),
            motivo="creacion",  # Esto sugeriría CREACION
            tipo_asignacion=TipoAsignacion.REASIGNACION  # Pero especificamos REASIGNACION
        )
        assert historial.tipo_asignacion == TipoAsignacion.REASIGNACION


class TestHistorialAsignacionMetodos:
    """Tests para métodos de negocio"""
    
    def test_es_asignacion_inicial_verdadero(self):
        """Test es_asignacion_inicial para tipo CREACION"""
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=date.today(),
            motivo="creacion",
            tipo_asignacion=TipoAsignacion.CREACION
        )
        assert historial.es_asignacion_inicial() == True
    
    def test_es_asignacion_inicial_falso(self):
        """Test es_asignacion_inicial para otros tipos"""
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=date.today(),
            motivo="reasignacion",
            tipo_asignacion=TipoAsignacion.REASIGNACION
        )
        assert historial.es_asignacion_inicial() == False
    
    def test_es_reasignacion_manual_verdadero(self):
        """Test es_reasignacion_manual para tipo REASIGNACION"""
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=date.today(),
            motivo="reasignacion",
            tipo_asignacion=TipoAsignacion.REASIGNACION
        )
        assert historial.es_reasignacion_manual() == True
    
    def test_es_reasignacion_manual_falso(self):
        """Test es_reasignacion_manual para otros tipos"""
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=date.today(),
            motivo="creacion",
            tipo_asignacion=TipoAsignacion.CREACION
        )
        assert historial.es_reasignacion_manual() == False
    
    def test_es_cambio_por_proceso_verdadero(self):
        """Test es_cambio_por_proceso para tipos de proceso"""
        tipos_proceso = [
            TipoAsignacion.INICIO_PROCESO,
            TipoAsignacion.COMPLETAR_PROCESO,
            TipoAsignacion.DEVOLVER_PROCESO
        ]
        
        for tipo in tipos_proceso:
            historial = HistorialAsignacion(
                funcionario_id="FUNC001",
                fecha_asignacion=date.today(),
                motivo="test",
                tipo_asignacion=tipo
            )
            assert historial.es_cambio_por_proceso() == True
    
    def test_es_cambio_por_proceso_falso(self):
        """Test es_cambio_por_proceso para tipos no de proceso"""
        tipos_no_proceso = [
            TipoAsignacion.CREACION,
            TipoAsignacion.REASIGNACION,
            TipoAsignacion.INACTIVACION,
            TipoAsignacion.REACTIVACION
        ]
        
        for tipo in tipos_no_proceso:
            historial = HistorialAsignacion(
                funcionario_id="FUNC001",
                fecha_asignacion=date.today(),
                motivo="test",
                tipo_asignacion=tipo
            )
            assert historial.es_cambio_por_proceso() == False
    
    def test_fue_asignado_por_supervisor_verdadero(self):
        """Test fue_asignado_por_supervisor con funcionario_asigna"""
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=date.today(),
            motivo="test",
            funcionario_asigna="SUPERVISOR01"
        )
        assert historial.fue_asignado_por_supervisor() == True
    
    def test_fue_asignado_por_supervisor_falso(self):
        """Test fue_asignado_por_supervisor sin funcionario_asigna"""
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=date.today(),
            motivo="test"
        )
        assert historial.fue_asignado_por_supervisor() == False
    
    def test_get_dias_desde_asignacion_hoy(self):
        """Test días desde asignación para hoy"""
        hoy = date.today()
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=hoy,
            motivo="test"
        )
        assert historial.get_dias_desde_asignacion() == 0
    
    def test_get_dias_desde_asignacion_ayer(self):
        """Test días desde asignación para ayer"""
        ayer = date.today() - timedelta(days=1)
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=ayer,
            motivo="test"
        )
        assert historial.get_dias_desde_asignacion() == 1
    
    def test_get_dias_desde_asignacion_semana_pasada(self):
        """Test días desde asignación para hace una semana"""
        hace_semana = date.today() - timedelta(days=7)
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=hace_semana,
            motivo="test"
        )
        assert historial.get_dias_desde_asignacion() == 7
    
    def test_es_asignacion_reciente_verdadero_defecto(self):
        """Test es_asignacion_reciente con límite por defecto (7 días)"""
        hace_5_dias = date.today() - timedelta(days=5)
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=hace_5_dias,
            motivo="test"
        )
        assert historial.es_asignacion_reciente() == True
    
    def test_es_asignacion_reciente_falso_defecto(self):
        """Test es_asignacion_reciente fuera del límite por defecto"""
        hace_10_dias = date.today() - timedelta(days=10)
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=hace_10_dias,
            motivo="test"
        )
        assert historial.es_asignacion_reciente() == False
    
    def test_es_asignacion_reciente_personalizado(self):
        """Test es_asignacion_reciente con límite personalizado"""
        hace_5_dias = date.today() - timedelta(days=5)
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=hace_5_dias,
            motivo="test"
        )
        assert historial.es_asignacion_reciente(3) == False  # 5 > 3
        assert historial.es_asignacion_reciente(10) == True  # 5 <= 10


class TestHistorialAsignacionFormatos:
    """Tests para métodos de formato y representación"""
    
    def test_get_motivo_detallado_sin_observaciones(self):
        """Test motivo detallado sin observaciones"""
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=date.today(),
            motivo="Asignación inicial"
        )
        assert historial.get_motivo_detallado() == "Asignación inicial"
    
    def test_get_motivo_detallado_con_observaciones(self):
        """Test motivo detallado con observaciones"""
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=date.today(),
            motivo="Reasignación",
            observaciones="Por carga de trabajo"
        )
        assert historial.get_motivo_detallado() == "Reasignación - Por carga de trabajo"
    
    def test_get_info_asignador_automatico(self):
        """Test info asignador para asignación automática"""
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=date.today(),
            motivo="test"
        )
        assert historial.get_info_asignador() == "Asignación automática"
    
    def test_get_info_asignador_manual(self):
        """Test info asignador para asignación manual"""
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=date.today(),
            motivo="test",
            funcionario_asigna="SUPERVISOR01"
        )
        assert historial.get_info_asignador() == "Asignado por: SUPERVISOR01"
    
    def test_get_resumen_completo_basico(self):
        """Test resumen completo básico"""
        fecha_test = date(2024, 12, 4)
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=fecha_test,
            motivo="creacion",
            tipo_asignacion=TipoAsignacion.CREACION
        )
        resumen = historial.get_resumen_completo()
        expected = "04/12/2024 | Creacion | FUNC001 | creacion"
        assert resumen == expected
    
    def test_get_resumen_completo_con_asignador(self):
        """Test resumen completo con asignador"""
        fecha_test = date(2024, 12, 4)
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=fecha_test,
            motivo="reasignacion",
            funcionario_asigna="SUPERVISOR01",
            tipo_asignacion=TipoAsignacion.REASIGNACION
        )
        resumen = historial.get_resumen_completo()
        expected = "04/12/2024 | Reasignacion | FUNC001 | reasignacion | Por: SUPERVISOR01"
        assert resumen == expected
    
    def test_str_representation(self):
        """Test representación string"""
        fecha_test = date(2024, 12, 4)
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=fecha_test,
            motivo="Asignación inicial"
        )
        expected = "2024-12-04 - FUNC001: Asignación inicial"
        assert str(historial) == expected
    
    def test_repr_representation(self):
        """Test representación repr"""
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=date.today(),
            motivo="creacion",
            tipo_asignacion=TipoAsignacion.CREACION
        )
        expected = "HistorialAsignacion(funcionario='FUNC001', fecha=" + str(date.today()) + ", tipo='creacion')"
        assert repr(historial) == expected


class TestHistorialAsignacionFactoryMethods:
    """Tests para factory methods"""
    
    def test_crear_asignacion_inicial(self):
        """Test factory method crear_asignacion_inicial"""
        fecha_test = date(2024, 12, 4)
        historial = HistorialAsignacion.crear_asignacion_inicial("FUNC001", fecha_test)
        
        assert historial.funcionario_id == "FUNC001"
        assert historial.fecha_asignacion == fecha_test
        assert historial.motivo == "creacion"
        assert historial.tipo_asignacion == TipoAsignacion.CREACION
        assert historial.funcionario_asigna is None
        assert historial.observaciones is None
    
    def test_crear_reasignacion_manual_basico(self):
        """Test factory method crear_reasignacion_manual básico"""
        historial = HistorialAsignacion.crear_reasignacion_manual(
            "FUNC002", 
            "SUPERVISOR01"
        )
        
        assert historial.funcionario_id == "FUNC002"
        assert historial.fecha_asignacion == date.today()
        assert historial.motivo == "reasignacion"
        assert historial.funcionario_asigna == "SUPERVISOR01"
        assert historial.tipo_asignacion == TipoAsignacion.REASIGNACION
        assert historial.observaciones is None
    
    def test_crear_reasignacion_manual_completo(self):
        """Test factory method crear_reasignacion_manual completo"""
        historial = HistorialAsignacion.crear_reasignacion_manual(
            "FUNC002",
            "SUPERVISOR01", 
            motivo="Reasignación por especialización",
            observaciones="Funcionario especialista en casos complejos"
        )
        
        assert historial.funcionario_id == "FUNC002"
        assert historial.motivo == "Reasignación por especialización"
        assert historial.funcionario_asigna == "SUPERVISOR01"
        assert historial.observaciones == "Funcionario especialista en casos complejos"
        assert historial.tipo_asignacion == TipoAsignacion.REASIGNACION
    
    def test_crear_cambio_proceso_inicio_traslado(self):
        """Test factory method crear_cambio_proceso para inicio de traslado"""
        historial = HistorialAsignacion.crear_cambio_proceso(
            "FUNC003",
            "traslado",
            "inicio"
        )
        
        assert historial.funcionario_id == "FUNC003"
        assert historial.fecha_asignacion == date.today()
        assert historial.motivo == "inicio_traslado"
        assert historial.tipo_asignacion == TipoAsignacion.INICIO_PROCESO
        assert historial.observaciones is None
    
    def test_crear_cambio_proceso_completar_radicacion(self):
        """Test factory method crear_cambio_proceso para completar radicación"""
        historial = HistorialAsignacion.crear_cambio_proceso(
            "FUNC003",
            "radicacion",
            "completar"
        )
        
        assert historial.funcionario_id == "FUNC003"
        assert historial.motivo == "completar_radicacion"
        assert historial.tipo_asignacion == TipoAsignacion.COMPLETAR_PROCESO
    
    def test_crear_cambio_proceso_devolver_con_motivo(self):
        """Test factory method crear_cambio_proceso para devolución con motivo"""
        historial = HistorialAsignacion.crear_cambio_proceso(
            "FUNC003",
            "traslado",
            "devolver",
            "Documentos incompletos"
        )
        
        assert historial.funcionario_id == "FUNC003"
        assert historial.motivo == "devolver_traslado: Documentos incompletos"
        assert historial.tipo_asignacion == TipoAsignacion.DEVOLVER_PROCESO
        assert historial.observaciones == "Documentos incompletos"
    
    def test_crear_cambio_proceso_accion_invalida(self):
        """Test factory method crear_cambio_proceso con acción inválida"""
        historial = HistorialAsignacion.crear_cambio_proceso(
            "FUNC003",
            "traslado",
            "accion_invalida"
        )
        
        # Debe caer en el caso por defecto (REASIGNACION)
        assert historial.tipo_asignacion == TipoAsignacion.REASIGNACION
        assert historial.motivo == "accion_invalida_traslado"
    
    def test_crear_inactivacion(self):
        """Test factory method crear_inactivacion"""
        historial = HistorialAsignacion.crear_inactivacion(
            "FUNC004",
            "Cuenta duplicada"
        )
        
        assert historial.funcionario_id == "FUNC004"
        assert historial.fecha_asignacion == date.today()
        assert historial.motivo == "inactivar: Cuenta duplicada"
        assert historial.tipo_asignacion == TipoAsignacion.INACTIVACION
        assert historial.observaciones == "Cuenta duplicada"
    
    def test_crear_reactivacion(self):
        """Test factory method crear_reactivacion"""
        historial = HistorialAsignacion.crear_reactivacion("FUNC005")
        
        assert historial.funcionario_id == "FUNC005"
        assert historial.fecha_asignacion == date.today()
        assert historial.motivo == "reactivar"
        assert historial.tipo_asignacion == TipoAsignacion.REACTIVACION
        assert historial.funcionario_asigna is None
        assert historial.observaciones is None


class TestHistorialAsignacionInmutabilidad:
    """Tests para inmutabilidad del value object"""
    
    def test_historial_es_inmutable(self):
        """Test que historial no se puede modificar"""
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=date.today(),
            motivo="test"
        )
        
        with pytest.raises(AttributeError):
            historial.funcionario_id = "FUNC002"
        
        with pytest.raises(AttributeError):
            historial.motivo = "nuevo motivo"
        
        with pytest.raises(AttributeError):
            historial.tipo_asignacion = TipoAsignacion.REASIGNACION
    
    def test_historial_hasheable(self):
        """Test que historial es hasheable"""
        historial = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=date.today(),
            motivo="test"
        )
        conjunto = {historial}
        assert len(conjunto) == 1
        assert historial in conjunto
    
    def test_igualdad_historiales(self):
        """Test igualdad entre historiales"""
        fecha_test = date.today()
        historial1 = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=fecha_test,
            motivo="test"
        )
        historial2 = HistorialAsignacion(
            funcionario_id="FUNC001",
            fecha_asignacion=fecha_test,
            motivo="test"
        )
        assert historial1 == historial2


class TestHistorialAsignacionCasosReales:
    """Tests con casos de uso reales del sistema"""
    
    def test_flujo_completo_creacion_cuenta(self):
        """Test flujo completo: creación de cuenta"""
        historial = HistorialAsignacion.crear_asignacion_inicial(
            "FUNC001", 
            date.today()
        )
        
        assert historial.es_asignacion_inicial() == True
        assert historial.fue_asignado_por_supervisor() == False
        assert historial.es_cambio_por_proceso() == False
        assert historial.es_asignacion_reciente() == True
        assert historial.get_dias_desde_asignacion() == 0
    
    def test_flujo_completo_reasignacion_supervisor(self):
        """Test flujo completo: reasignación por supervisor"""
        historial = HistorialAsignacion.crear_reasignacion_manual(
            "FUNC002",
            "SUPERVISOR01",
            motivo="Cambio por especialización",
            observaciones="Caso requiere experiencia específica"
        )
        
        assert historial.es_reasignacion_manual() == True
        assert historial.fue_asignado_por_supervisor() == True
        assert historial.es_cambio_por_proceso() == False
        assert "Cambio por especialización - Caso requiere experiencia específica" == historial.get_motivo_detallado()
        assert "Asignado por: SUPERVISOR01" == historial.get_info_asignador()
    
    def test_flujo_completo_proceso_traslado(self):
        """Test flujo completo: proceso de traslado"""
        # Inicio de traslado
        inicio = HistorialAsignacion.crear_cambio_proceso(
            "FUNC003",
            "traslado", 
            "inicio"
        )
        
        # Devolución por problemas
        devolucion = HistorialAsignacion.crear_cambio_proceso(
            "FUNC003",
            "traslado",
            "devolver",
            "Documentos faltantes"
        )
        
        # Completar después de correcciones
        completar = HistorialAsignacion.crear_cambio_proceso(
            "FUNC003",
            "traslado",
            "completar"
        )
        
        # Verificar tipos
        assert inicio.es_cambio_por_proceso() == True
        assert devolucion.es_cambio_por_proceso() == True
        assert completar.es_cambio_por_proceso() == True
        
        # Verificar motivos
        assert inicio.motivo == "inicio_traslado"
        assert devolucion.motivo == "devolver_traslado: Documentos faltantes"
        assert completar.motivo == "completar_traslado"
    
    def test_flujo_completo_inactivacion_reactivacion(self):
        """Test flujo completo: inactivación y reactivación"""
        # Inactivación
        inactivacion = HistorialAsignacion.crear_inactivacion(
            "FUNC004",
            "Cuenta creada por error"
        )
        
        # Reactivación posterior
        reactivacion = HistorialAsignacion.crear_reactivacion("FUNC005")
        
        assert inactivacion.tipo_asignacion == TipoAsignacion.INACTIVACION
        assert reactivacion.tipo_asignacion == TipoAsignacion.REACTIVACION
        assert inactivacion.motivo == "inactivar: Cuenta creada por error"
        assert reactivacion.motivo == "reactivar"
    
    def test_historial_completo_cuenta(self):
        """Test historial completo de una cuenta"""
        # Simular historial completo de asignaciones
        historial_completo = [
            HistorialAsignacion.crear_asignacion_inicial("FUNC001", date.today() - timedelta(days=30)),
            HistorialAsignacion.crear_cambio_proceso("FUNC001", "traslado", "inicio"),
            HistorialAsignacion.crear_cambio_proceso("FUNC001", "traslado", "devolver", "Revisar datos propietario"),
            HistorialAsignacion.crear_reasignacion_manual("FUNC002", "SUPERVISOR01", observaciones="Especialista en casos complejos"),
            HistorialAsignacion.crear_cambio_proceso("FUNC002", "traslado", "completar")
        ]
        
        # Verificar secuencia lógica
        assert historial_completo[0].es_asignacion_inicial() == True
        assert historial_completo[1].tipo_asignacion == TipoAsignacion.INICIO_PROCESO
        assert historial_completo[2].tipo_asignacion == TipoAsignacion.DEVOLVER_PROCESO
        assert historial_completo[3].es_reasignacion_manual() == True
        assert historial_completo[4].tipo_asignacion == TipoAsignacion.COMPLETAR_PROCESO
        
        # Verificar trazabilidad
        assert historial_completo[3].fue_asignado_por_supervisor() == True
        assert "FUNC002" == historial_completo[4].funcionario_id
    
    def test_deteccion_casos_edge_motivos(self):
        """Test detección de tipos en casos edge de motivos"""
        casos_edge = [
            ("INICIO traslado", TipoAsignacion.INICIO_PROCESO),
            ("proceso de INICIO", TipoAsignacion.INICIO_PROCESO),
            ("COMPLETAR proceso", TipoAsignacion.COMPLETAR_PROCESO),
            ("DEVOLVER cuenta", TipoAsignacion.DEVOLVER_PROCESO),
            ("INACTIVAR por duplicado", TipoAsignacion.INACTIVACION),
            ("REACTIVAR", TipoAsignacion.REACTIVACION),
            ("REASIGNACION", TipoAsignacion.REASIGNACION),
            ("CREACION", TipoAsignacion.CREACION),
            ("Creación de cuenta nueva", TipoAsignacion.CREACION),  # Ahora debería funcionar
            ("Reasignación por carga de trabajo", TipoAsignacion.REASIGNACION),  # Ahora debería funcionar
            ("motivo sin palabras clave", TipoAsignacion.REASIGNACION)
        ]
        
        for motivo, tipo_esperado in casos_edge:
            historial = HistorialAsignacion(
                funcionario_id="FUNC001",
                fecha_asignacion=date.today(),
                motivo=motivo
            )
            assert historial.tipo_asignacion == tipo_esperado, f"Motivo '{motivo}' debería dar tipo {tipo_esperado}"