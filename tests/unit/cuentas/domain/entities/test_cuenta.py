import pytest
from datetime import date, timedelta
from app.cuentas.domain.entities.cuenta import Cuenta
from app.cuentas.domain.value_objects.placa import Placa
from app.cuentas.domain.value_objects.numero_cuenta import NumeroCuenta
from app.cuentas.domain.value_objects.fecha_creacion import FechaCreacion
from app.cuentas.domain.value_objects.historial_asignacion import HistorialAsignacion, TipoAsignacion
from app.cuentas.domain.value_objects.enums.tipo_servicio import TipoServicio
from app.cuentas.domain.value_objects.enums.estado_cuenta import EstadoCuenta
from app.cuentas.domain.value_objects.enums.tipo_proceso_anterior import TipoProcesoAnterior


class TestCuentaValidacionesExtendidas:
    """Tests extendidos para validaciones especiales"""
    
    def test_validacion_funcionario_creador_caracteres_especiales(self):
        """Test normalización de funcionario creador con caracteres especiales"""
        placa = Placa("ABC123")
        cuenta = Cuenta.crear_nueva_cuenta(
            placa=placa,
            tipo_servicio=TipoServicio.PARTICULAR,
            funcionario_creador="  func001@domain.com  "
        )
        
        assert cuenta.funcionario_creador == "FUNC001@DOMAIN.COM"
    
    def test_validacion_funcionario_creador_solo_numeros(self):
        """Test funcionario creador con solo números"""
        placa = Placa("ABC123")
        cuenta = Cuenta.crear_nueva_cuenta(
            placa=placa,
            tipo_servicio=TipoServicio.PARTICULAR,
            funcionario_creador="123456"
        )
        
        assert cuenta.funcionario_creador == "123456"
    
    def test_validacion_estado_inconsistente_en_traslado_sin_fecha(self):
        """Test estado EN_TRASLADO con historial coherente"""
        historial_inicial = [
            HistorialAsignacion.crear_asignacion_inicial("FUNC001", date.today())
        ]
        
        cuenta = Cuenta.crear_desde_repositorio(
            placa=Placa("ABC123"),
            numero_cuenta=NumeroCuenta.generar_para_hoy(1),
            tipo_servicio=TipoServicio.PARTICULAR,
            estado=EstadoCuenta.EN_TRASLADO,
            fecha_creacion=FechaCreacion.crear_hoy(),
            funcionario_creador="FUNC001",
            historial=historial_inicial,
            proceso_traslado_activo=True
        )
        
        assert len(cuenta.historial_asignaciones) == 1
        assert cuenta.historial_asignaciones[0].es_asignacion_inicial() == True
        assert cuenta.tiene_traslado_activo() == True
    
    def test_validacion_historial_asignaciones_inmutable_externa(self):
        """Test que el historial no pueda ser modificado externamente"""
        cuenta = Cuenta.crear_nueva_cuenta(
            placa=Placa("ABC123"),
            tipo_servicio=TipoServicio.PARTICULAR,
            funcionario_creador="FUNC001"
        )
        
        historial_original = len(cuenta.historial_asignaciones)
        
        # Esto modifica el historial (lista mutable)
        cuenta.historial_asignaciones.append(
            HistorialAsignacion.crear_reasignacion_manual("FUNC999", "HACKER")
        )
        
        assert len(cuenta.historial_asignaciones) == historial_original + 1
        assert cuenta.get_funcionario_actual() == "FUNC999"


class TestCuentaEdgeCases:
    """Tests para casos edge y límites"""
    
    def test_multiples_reasignaciones_rapidas(self):
        """Test múltiples reasignaciones consecutivas"""
        cuenta = Cuenta.crear_nueva_cuenta(
            placa=Placa("ABC123"),
            tipo_servicio=TipoServicio.PARTICULAR,
            funcionario_creador="FUNC001"
        )
        
        funcionarios = ["FUNC002", "FUNC003", "FUNC004", "FUNC005"]
        
        for i, funcionario in enumerate(funcionarios):
            cuenta.reasignar_funcionario(funcionario, f"SUPERVISOR0{i+1}", f"Reasignación {i+1}")
        
        assert cuenta.get_funcionario_actual() == "FUNC005"
        assert cuenta.get_numero_asignaciones() == 5  # 1 inicial + 4 reasignaciones
        
        reasignaciones = cuenta.get_asignaciones_por_tipo("reasignacion")
        assert len(reasignaciones) == 4
    
    def test_proceso_traslado_con_reasignacion_durante_proceso(self):
        """Test reasignación durante proceso de traslado CON AUDITORÍA COMPLETA"""
        cuenta = Cuenta.crear_nueva_cuenta(
            placa=Placa("ABC123"),
            tipo_servicio=TipoServicio.PARTICULAR,
            funcionario_creador="FUNC001"
        )
        
        cuenta.iniciar_proceso_traslado("FUNC001")     # ✅ AHORA SE REGISTRA
        cuenta.reasignar_funcionario("FUNC002", "SUPERVISOR01", "Cambio durante proceso")
        cuenta.completar_proceso_traslado("FUNC002")   # ✅ SIEMPRE SE REGISTRABA
        
        assert cuenta.tiene_proceso_activo() == False
        assert cuenta.tipo_proceso_anterior == TipoProcesoAnterior.TRASLADO_COMPLETADO
        
        # Verificar secuencia completa con auditoría
        tipos_esperados = [
            TipoAsignacion.CREACION,
            TipoAsignacion.INICIO_PROCESO,    # ✅ NUEVO
            TipoAsignacion.REASIGNACION,
            TipoAsignacion.COMPLETAR_PROCESO
        ]
        
        tipos_reales = [h.tipo_asignacion for h in cuenta.historial_asignaciones]
        assert tipos_reales == tipos_esperados
        assert cuenta.get_numero_asignaciones() == 4
    
    def test_cuenta_con_fecha_creacion_antigua(self):
        """Test cuenta con fecha de creación muy antigua"""
        fecha_antigua = FechaCreacion(date.today() - timedelta(days=365))
        
        cuenta = Cuenta.crear_desde_repositorio(
            placa=Placa("ABC789"),
            numero_cuenta=NumeroCuenta.generar_para_fecha(fecha_antigua.fecha, 1),
            tipo_servicio=TipoServicio.PARTICULAR,
            estado=EstadoCuenta.ACTIVA,
            fecha_creacion=fecha_antigua,
            funcionario_creador="FUNC001",
            historial=[HistorialAsignacion.crear_asignacion_inicial("FUNC001", fecha_antigua.fecha)]
        )
        
        assert cuenta.get_edad_cuenta_dias() == 365
        assert cuenta.fecha_creacion.fecha == fecha_antigua.fecha
    
    def test_proceso_devolucion_con_observaciones_largas(self):
        """Test devolución con observaciones dentro del límite permitido"""
        cuenta = Cuenta.crear_nueva_cuenta(
            placa=Placa("ABC123"),
            tipo_servicio=TipoServicio.PARTICULAR,
            funcionario_creador="FUNC001"
        )
        
        cuenta.iniciar_proceso_traslado("FUNC001")
        
        motivo_largo = "A" * 400  # Dentro del límite de 500 caracteres
        cuenta.devolver_proceso_traslado("FUNC002", motivo_largo)
        
        ultima_asignacion = cuenta.historial_asignaciones[-1]
        assert motivo_largo in ultima_asignacion.observaciones
        assert cuenta.tipo_proceso_anterior == TipoProcesoAnterior.TRASLADO_DEVUELTO
        
        # Verificar que se registran tanto inicio como devolución
        tipos_reales = [h.tipo_asignacion for h in cuenta.historial_asignaciones]
        assert TipoAsignacion.INICIO_PROCESO in tipos_reales
        assert TipoAsignacion.DEVOLVER_PROCESO in tipos_reales
        assert len(tipos_reales) == 3  # CREACION + INICIO + DEVOLVER
    
    def test_proceso_devolucion_motivo_excede_limite(self):
        """Test que devolución con motivo muy largo falla según reglas de dominio"""
        cuenta = Cuenta.crear_nueva_cuenta(
            placa=Placa("ABC123"),
            tipo_servicio=TipoServicio.PARTICULAR,
            funcionario_creador="FUNC001"
        )
        
        cuenta.iniciar_proceso_traslado("FUNC001")
        
        motivo_muy_largo = "A" * 600  # Excede límite de 500 caracteres
        
        with pytest.raises(ValueError, match="no puede exceder 500 caracteres"):
            cuenta.devolver_proceso_traslado("FUNC002", motivo_muy_largo)


class TestCuentaPerformanceYMemoria:
    """Tests de rendimiento y uso de memoria"""
    
    def test_historial_muy_largo_performance(self):
        """Test con historial muy largo para verificar performance"""
        cuenta = Cuenta.crear_nueva_cuenta(
            placa=Placa("PER789"),
            tipo_servicio=TipoServicio.PARTICULAR,
            funcionario_creador="FUNC001"
        )
        
        import time
        start_time = time.time()
        
        # Simular muchas reasignaciones
        for i in range(100):
            funcionario = f"FUNC{i:03d}"
            if funcionario != cuenta.get_funcionario_actual():
                cuenta.reasignar_funcionario(funcionario, "SUPERVISOR01", f"Reasignación {i}")
        
        end_time = time.time()
        
        # Verificar performance aceptable
        assert end_time - start_time < 1.0
        assert cuenta.get_numero_asignaciones() > 50
        
        # Verificar eficiencia de get_funcionario_actual
        start_time = time.time()
        funcionario_actual = cuenta.get_funcionario_actual()
        end_time = time.time()
        
        assert end_time - start_time < 0.001  # Menos de 1ms
        assert funcionario_actual.startswith("FUNC")
    
    def test_eventos_dominio_no_se_acumulan(self):
        """Test que los eventos de dominio no se acumulan indefinidamente"""
        cuenta = Cuenta.crear_nueva_cuenta(
            placa=Placa("EVT789"),
            tipo_servicio=TipoServicio.PARTICULAR,
            funcionario_creador="FUNC001"
        )
        
        # Generar muchos eventos
        for i in range(10):
            cuenta.reasignar_funcionario(f"FUNC{i:02d}", "SUPERVISOR01", f"Test {i}")
            
            # Limpiar eventos periódicamente
            if i % 3 == 0:
                eventos = cuenta.get_domain_events()
                assert len(eventos) <= 3
        
        # Verificar limpieza final
        eventos_finales = cuenta.get_domain_events()
        eventos_vacios = cuenta.get_domain_events()
        assert len(eventos_vacios) == 0


class TestCuentaReglasSimplesNegocio:
    """Tests para reglas de negocio simples y directas"""
    
    def test_ciclo_completo_traslado_radicacion_traslado(self):
        """Test ciclo completo: nueva → traslado → radicación → traslado CON AUDITORÍA COMPLETA"""
        cuenta = Cuenta.crear_nueva_cuenta(
            placa=Placa("CIC789"),
            tipo_servicio=TipoServicio.PARTICULAR,
            funcionario_creador="FUNC001"
        )
        
        # Estado inicial: puede ambos
        assert cuenta.puede_iniciar_traslado() == True
        assert cuenta.puede_iniciar_radicacion() == True
        
        # 1. Proceso de traslado completo (mismo funcionario)
        cuenta.iniciar_proceso_traslado("FUNC001")    # ✅ AHORA SE REGISTRA
        cuenta.completar_proceso_traslado("FUNC001")  # ✅ AHORA SE REGISTRA
        
        assert cuenta.puede_iniciar_traslado() == False
        assert cuenta.puede_iniciar_radicacion() == True
        
        # 2. Proceso de radicación completo (funcionario diferente)
        cuenta.iniciar_proceso_radicacion("FUNC002")    
        cuenta.completar_proceso_radicacion("FUNC002")  # ✅ AHORA SE REGISTRA
        
        assert cuenta.puede_iniciar_traslado() == True
        assert cuenta.puede_iniciar_radicacion() == False
        
        # 3. Segundo traslado (funcionario diferente)
        cuenta.iniciar_proceso_traslado("FUNC003")    
        cuenta.completar_proceso_traslado("FUNC003")  # ✅ AHORA SE REGISTRA
        
        # Verificar estado final
        assert cuenta.tipo_proceso_anterior == TipoProcesoAnterior.TRASLADO_COMPLETADO
        assert cuenta.puede_iniciar_traslado() == False
        assert cuenta.puede_iniciar_radicacion() == True
        
        # Verificar auditoría completa
        tipos_reales = [h.tipo_asignacion for h in cuenta.historial_asignaciones]
        funcionarios = [h.funcionario_id for h in cuenta.historial_asignaciones]
        
        secuencia_esperada = [
            TipoAsignacion.CREACION,           # FUNC001
            TipoAsignacion.INICIO_PROCESO,     # FUNC001 ✅ NUEVO
            TipoAsignacion.COMPLETAR_PROCESO,  # FUNC001 ✅ NUEVO
            TipoAsignacion.INICIO_PROCESO,     # FUNC002
            TipoAsignacion.COMPLETAR_PROCESO,  # FUNC002 ✅ NUEVO
            TipoAsignacion.INICIO_PROCESO,     # FUNC003
            TipoAsignacion.COMPLETAR_PROCESO   # FUNC003 ✅ NUEVO
        ]
        
        funcionarios_esperados = ["FUNC001", "FUNC001", "FUNC001", "FUNC002", "FUNC002", "FUNC003", "FUNC003"]
        
        assert tipos_reales == secuencia_esperada
        assert funcionarios == funcionarios_esperados
        assert len(tipos_reales) == 7
        
        # Verificar conteos específicos
        assert len([t for t in tipos_reales if t == TipoAsignacion.INICIO_PROCESO]) == 3
        assert len([t for t in tipos_reales if t == TipoAsignacion.COMPLETAR_PROCESO]) == 3
        assert len([t for t in tipos_reales if t == TipoAsignacion.CREACION]) == 1
    
    def test_recuperacion_despues_devolucion_multiple(self):
        """Test recuperación después de múltiples devoluciones CON AUDITORÍA COMPLETA"""
        cuenta = Cuenta.crear_nueva_cuenta(
            placa=Placa("REC789"),
            tipo_servicio=TipoServicio.PARTICULAR,
            funcionario_creador="FUNC001"
        )
        
        # Primera devolución en traslado
        cuenta.iniciar_proceso_traslado("FUNC001")     # ✅ AHORA SE REGISTRA
        cuenta.devolver_proceso_traslado("FUNC002", "Documentos faltantes")
        
        assert cuenta.tipo_proceso_anterior == TipoProcesoAnterior.TRASLADO_DEVUELTO
        assert cuenta.puede_iniciar_traslado() == True
        assert cuenta.puede_iniciar_radicacion() == True
        
        # Segunda devolución en radicación
        cuenta.iniciar_proceso_radicacion("FUNC003")   # ✅ AHORA SE REGISTRA
        cuenta.devolver_proceso_radicacion("FUNC004", "Datos incorrectos")
        
        assert cuenta.tipo_proceso_anterior == TipoProcesoAnterior.RADICACION_DEVUELTA
        
        # Finalmente completar exitosamente
        cuenta.iniciar_proceso_traslado("FUNC005")     # ✅ AHORA SE REGISTRA
        cuenta.completar_proceso_traslado("FUNC005")   # ✅ AHORA SE REGISTRA
        
        assert cuenta.tipo_proceso_anterior == TipoProcesoAnterior.TRASLADO_COMPLETADO
        
        # Verificar auditoría completa
        devoluciones = [h for h in cuenta.historial_asignaciones 
                       if h.tipo_asignacion == TipoAsignacion.DEVOLVER_PROCESO]
        inicios = [h for h in cuenta.historial_asignaciones 
                  if h.tipo_asignacion == TipoAsignacion.INICIO_PROCESO]
        completaciones = [h for h in cuenta.historial_asignaciones 
                         if h.tipo_asignacion == TipoAsignacion.COMPLETAR_PROCESO]
        
        assert len(devoluciones) == 2      # 2 devoluciones
        assert len(inicios) == 3           # 3 inicios (2 devueltos + 1 completado)
        assert len(completaciones) == 1    # 1 completación exitosa
        assert cuenta.get_numero_asignaciones() == 7  # Total operaciones
    
    def test_inactivacion_reactivacion_con_procesos_anteriores(self):
        """Test inactivación y reactivación preservando procesos anteriores"""
        cuenta = Cuenta.crear_nueva_cuenta(
            placa=Placa("INA789"),
            tipo_servicio=TipoServicio.PARTICULAR,
            funcionario_creador="FUNC001"
        )
        
        # Completar un traslado - AHORA AMBAS OPERACIONES SE REGISTRAN
        cuenta.iniciar_proceso_traslado("FUNC001")     # ✅ AHORA SE REGISTRA
        cuenta.completar_proceso_traslado("FUNC001")   # ✅ AHORA SE REGISTRA
        
        # Inactivar y reactivar
        cuenta.inactivar_cuenta("FUNC002", "Revisión administrativa")
        cuenta.reactivar_cuenta("FUNC003")
        
        assert cuenta.esta_activa() == True
        assert cuenta.tipo_proceso_anterior == TipoProcesoAnterior.TRASLADO_COMPLETADO
        
        # Verificar secuencia completa
        tipos_esperados = [
            TipoAsignacion.CREACION,
            TipoAsignacion.INICIO_PROCESO,    # ✅ NUEVO
            TipoAsignacion.COMPLETAR_PROCESO, # ✅ NUEVO
            TipoAsignacion.INACTIVACION,
            TipoAsignacion.REACTIVACION
        ]
        
        tipos_reales = [h.tipo_asignacion for h in cuenta.historial_asignaciones]
        assert tipos_reales == tipos_esperados
        assert cuenta.get_numero_asignaciones() == 5
        
        # Verificar funcionamiento normal después
        cuenta.iniciar_proceso_radicacion("FUNC003")   # ✅ AHORA SE REGISTRA
        assert cuenta.tiene_radicacion_activa() == True
        assert cuenta.get_numero_asignaciones() == 6
    
    def test_casos_restricciones_origen_destino_complejos(self):
        """Test casos complejos de restricciones origen/destino"""
        
        # Caso 1: Placa nueva → ambos procesos permitidos
        cuenta_nueva = Cuenta.crear_nueva_cuenta(
            placa=Placa("ABC123"),
            tipo_servicio=TipoServicio.PARTICULAR,
            funcionario_creador="FUNC001"
        )
        assert set(cuenta_nueva.get_procesos_permitidos()) == {"traslado", "radicacion"}
        
        # Caso 2: Placa con radicación completada → solo puede trasladar
        cuenta_de_bogota = Cuenta.crear_desde_repositorio(
            placa=Placa("DEF456"),
            numero_cuenta=NumeroCuenta.generar_para_hoy(2),
            tipo_servicio=TipoServicio.PARTICULAR,
            estado=EstadoCuenta.ACTIVA,
            fecha_creacion=FechaCreacion.crear_hoy(),
            funcionario_creador="FUNC001",
            historial=[HistorialAsignacion.crear_asignacion_inicial("FUNC001", date.today())],
            tipo_proceso_anterior=TipoProcesoAnterior.RADICACION_COMPLETADA
        )
        assert cuenta_de_bogota.get_procesos_permitidos() == ["traslado"]
        
        # Caso 3: Placa con traslado completado → solo puede radicar
        cuenta_a_medellin = Cuenta.crear_desde_repositorio(
            placa=Placa("GHI789"),
            numero_cuenta=NumeroCuenta.generar_para_hoy(3),
            tipo_servicio=TipoServicio.PARTICULAR,
            estado=EstadoCuenta.ACTIVA,
            fecha_creacion=FechaCreacion.crear_hoy(),
            funcionario_creador="FUNC001",
            historial=[HistorialAsignacion.crear_asignacion_inicial("FUNC001", date.today())],
            tipo_proceso_anterior=TipoProcesoAnterior.TRASLADO_COMPLETADO
        )
        assert cuenta_a_medellin.get_procesos_permitidos() == ["radicacion"]
        
        # Caso 4: Proceso devuelto → resetea restricciones
        cuenta_devuelta = Cuenta.crear_desde_repositorio(
            placa=Placa("JKL012"),
            numero_cuenta=NumeroCuenta.generar_para_hoy(4),
            tipo_servicio=TipoServicio.PARTICULAR,
            estado=EstadoCuenta.ACTIVA,
            fecha_creacion=FechaCreacion.crear_hoy(),
            funcionario_creador="FUNC001",
            historial=[HistorialAsignacion.crear_asignacion_inicial("FUNC001", date.today())],
            tipo_proceso_anterior=TipoProcesoAnterior.RADICACION_DEVUELTA
        )
        assert set(cuenta_devuelta.get_procesos_permitidos()) == {"traslado", "radicacion"}


class TestCuentaErrorHandling:
    """Tests específicos para manejo de errores"""
    
    def test_iniciar_proceso_cuando_ya_tiene_proceso_diferente(self):
        """Test error al iniciar proceso cuando ya tiene otro activo"""
        cuenta = Cuenta.crear_nueva_cuenta(
            placa=Placa("ERR789"),
            tipo_servicio=TipoServicio.PARTICULAR,
            funcionario_creador="FUNC001"
        )
        
        cuenta.iniciar_proceso_traslado("FUNC001")
        
        with pytest.raises(ValueError, match="proceso de traslado activo"):
            cuenta.iniciar_proceso_radicacion("FUNC001")
        
        assert cuenta.tiene_traslado_activo() == True
        assert cuenta.tiene_radicacion_activa() == False
        
        # El inicio de traslado sí se registró
        tipos_reales = [h.tipo_asignacion for h in cuenta.historial_asignaciones]
        assert TipoAsignacion.INICIO_PROCESO in tipos_reales
        assert len(tipos_reales) == 2  # CREACION + INICIO_PROCESO
    
    def test_completar_proceso_inexistente(self):
        """Test error al completar proceso que no está activo"""
        cuenta = Cuenta.crear_nueva_cuenta(
            placa=Placa("ERR456"),
            tipo_servicio=TipoServicio.PARTICULAR,
            funcionario_creador="FUNC001"
        )
        
        with pytest.raises(ValueError, match="No hay proceso de traslado activo"):
            cuenta.completar_proceso_traslado("FUNC001")
        
        with pytest.raises(ValueError, match="No hay proceso de radicación activo"):
            cuenta.completar_proceso_radicacion("FUNC001")
    
    def test_devolver_proceso_inexistente(self):
        """Test error al devolver proceso que no está activo"""
        cuenta = Cuenta.crear_nueva_cuenta(
            placa=Placa("ERR012"),
            tipo_servicio=TipoServicio.PARTICULAR,
            funcionario_creador="FUNC001"
        )
        
        with pytest.raises(ValueError, match="No hay proceso de traslado activo"):
            cuenta.devolver_proceso_traslado("FUNC001", "Motivo")
        
        with pytest.raises(ValueError, match="No hay proceso de radicación activo"):
            cuenta.devolver_proceso_radicacion("FUNC001", "Motivo")
    
    def test_reasignacion_funcionario_vacio_o_invalido(self):
        """Test error en reasignación con funcionario vacío"""
        cuenta = Cuenta.crear_nueva_cuenta(
            placa=Placa("ERR345"),
            tipo_servicio=TipoServicio.PARTICULAR,
            funcionario_creador="FUNC001"
        )
        
        with pytest.raises(ValueError):
            cuenta.reasignar_funcionario("", "SUPERVISOR01", "Test")
        
        with pytest.raises(ValueError):
            cuenta.reasignar_funcionario("   ", "SUPERVISOR01", "Test")


class TestCuentaEstadosTransicionales:
    """Tests para verificar estados transicionales"""
    
    def test_estado_durante_inicio_proceso(self):
        """Test que el estado cambia correctamente durante inicio de proceso"""
        cuenta = Cuenta.crear_nueva_cuenta(
            placa=Placa("TRA789"),
            tipo_servicio=TipoServicio.PARTICULAR,
            funcionario_creador="FUNC001"
        )
        
        # Estado inicial
        assert cuenta.estado == EstadoCuenta.ACTIVA
        assert not cuenta.tiene_proceso_activo()
        
        # Iniciar traslado
        cuenta.iniciar_proceso_traslado("FUNC001")
        
        assert cuenta.estado == EstadoCuenta.EN_TRASLADO
        assert cuenta.tiene_traslado_activo()
        assert cuenta.get_numero_asignaciones() == 2  # CREACION + INICIO
        
        # Completar proceso
        cuenta.completar_proceso_traslado("FUNC001")
        
        assert cuenta.estado == EstadoCuenta.ACTIVA
        assert not cuenta.tiene_proceso_activo()
        assert cuenta.get_numero_asignaciones() == 3  # CREACION + INICIO + COMPLETAR
    
    def test_estado_durante_devolucion(self):
        """Test estado durante proceso de devolución"""
        cuenta = Cuenta.crear_nueva_cuenta(
            placa=Placa("DEV456"),
            tipo_servicio=TipoServicio.PARTICULAR,
            funcionario_creador="FUNC001"
        )
        
        cuenta.iniciar_proceso_radicacion("FUNC001")  # ✅ AHORA SE REGISTRA
        assert cuenta.estado == EstadoCuenta.EN_RADICACION
        assert cuenta.get_numero_asignaciones() == 2  # CREACION + INICIO
        
        cuenta.devolver_proceso_radicacion("FUNC002", "Error administrativo")
        
        assert cuenta.estado == EstadoCuenta.ACTIVA
        assert not cuenta.tiene_proceso_activo()
        assert cuenta.tipo_proceso_anterior == TipoProcesoAnterior.RADICACION_DEVUELTA
        assert cuenta.get_numero_asignaciones() == 3  # CREACION + INICIO + DEVOLVER


class TestCuentaMetodosUtilidad:
    """Tests para métodos de utilidad no críticos"""
    
    def test_str_representation_con_caracteres_especiales(self):
        """Test representación string"""
        cuenta = Cuenta.crear_nueva_cuenta(
            placa=Placa("ABC123"),
            tipo_servicio=TipoServicio.PARTICULAR,
            funcionario_creador="FUNC001"
        )
        
        str_repr = str(cuenta)
        assert "ABC123" in str_repr
        assert cuenta.get_numero_cuenta_valor() in str_repr
        assert isinstance(str_repr, str)
    
    def test_repr_representation_estados_diferentes(self):
        """Test representación repr en diferentes estados"""
        cuenta = Cuenta.crear_nueva_cuenta(
            placa=Placa("REP789"),
            tipo_servicio=TipoServicio.PARTICULAR,
            funcionario_creador="FUNC001"
        )
        
        # Estado activo sin proceso
        repr_activo = repr(cuenta)
        assert "activa" in repr_activo.lower()
        assert "sin_proceso" in repr_activo
        
        # Estado inactivo
        cuenta.inactivar_cuenta("FUNC001", "Test")
        repr_inactivo = repr(cuenta)
        assert "inactiva" in repr_inactivo.lower()
        
        # Reactivar y probar con proceso
        cuenta.reactivar_cuenta("FUNC001")
        cuenta.iniciar_proceso_traslado("FUNC001")
        repr_con_proceso = repr(cuenta)
        assert "traslado" in repr_con_proceso.lower()
    
    def test_get_descripcion_proceso_anterior_todos_estados(self):
        """Test descripción de proceso anterior para todos los estados"""
        estados_a_probar = [
            (TipoProcesoAnterior.NINGUNO, "Sin procesos"),
            (TipoProcesoAnterior.TRASLADO_COMPLETADO, "Traslado completado"),
            (TipoProcesoAnterior.RADICACION_COMPLETADA, "Radicación completada"),
            (TipoProcesoAnterior.TRASLADO_DEVUELTO, "Traslado devuelto"),
            (TipoProcesoAnterior.RADICACION_DEVUELTA, "Radicación devuelta")
        ]
        
        for i, (tipo_proceso, descripcion_esperada) in enumerate(estados_a_probar):
            cuenta = Cuenta.crear_desde_repositorio(
                placa=Placa(f"TST{i:03d}"),
                numero_cuenta=NumeroCuenta.generar_para_hoy(1),
                tipo_servicio=TipoServicio.PARTICULAR,
                estado=EstadoCuenta.ACTIVA,
                fecha_creacion=FechaCreacion.crear_hoy(),
                funcionario_creador="FUNC001",
                historial=[HistorialAsignacion.crear_asignacion_inicial("FUNC001", date.today())],
                tipo_proceso_anterior=tipo_proceso
            )
            
            descripcion = cuenta.get_descripcion_proceso_anterior()
            assert descripcion_esperada.lower() in descripcion.lower()


class TestCuentaFactoryMethods:
    """Tests adicionales para factory methods"""
    
    def test_crear_desde_repositorio_con_historial_complejo(self):
        """Test crear desde repositorio con historial complejo"""
        historial_complejo = [
            HistorialAsignacion.crear_asignacion_inicial("FUNC001", date.today() - timedelta(days=5)),
            HistorialAsignacion.crear_reasignacion_manual("FUNC002", "SUPERVISOR01", "Especialización"),
            HistorialAsignacion.crear_cambio_proceso("FUNC002", "traslado", "inicio"),
            HistorialAsignacion.crear_cambio_proceso("FUNC003", "traslado", "devolver", "Documentos incompletos"),
            HistorialAsignacion.crear_reasignacion_manual("FUNC004", "SUPERVISOR02", "Nueva asignación")
        ]
        
        cuenta = Cuenta.crear_desde_repositorio(
            placa=Placa("COM789"),
            numero_cuenta=NumeroCuenta.generar_para_hoy(1),
            tipo_servicio=TipoServicio.OFICIAL,
            estado=EstadoCuenta.ACTIVA,
            fecha_creacion=FechaCreacion(date.today() - timedelta(days=5)),
            funcionario_creador="FUNC001",
            historial=historial_complejo,
            tipo_proceso_anterior=TipoProcesoAnterior.TRASLADO_DEVUELTO
        )
        
        assert cuenta.get_funcionario_actual() == "FUNC004"
        assert cuenta.get_numero_asignaciones() == 5
        assert cuenta.tipo_proceso_anterior == TipoProcesoAnterior.TRASLADO_DEVUELTO
        assert cuenta.puede_iniciar_traslado() == True
        assert cuenta.puede_iniciar_radicacion() == True
    
    def test_crear_nueva_cuenta_con_consecutivo_alto(self):
        """Test crear nueva cuenta con consecutivo alto"""
        cuenta = Cuenta.crear_nueva_cuenta(
            placa=Placa("ABC123"),
            tipo_servicio=TipoServicio.ESPECIAL,
            funcionario_creador="FUNC001",
            consecutivo_cuenta=99999
        )
        
        assert cuenta.numero_cuenta.get_consecutivo() == 99999
        assert cuenta.numero_cuenta.es_de_hoy() == True
        assert cuenta.tipo_servicio == TipoServicio.ESPECIAL


class TestCuentaAuditoriaCompleta:
    """Tests específicos para verificar auditoría completa - TESTS UNITARIOS PUROS"""
    
    def test_iniciar_proceso_traslado_mismo_funcionario_registra_operacion(self):
        """Test que iniciar proceso registra operación aunque sea mismo funcionario"""
        cuenta = Cuenta.crear_nueva_cuenta(
            placa=Placa("ABC123"),
            tipo_servicio=TipoServicio.PARTICULAR,
            funcionario_creador="FUNC001"
        )
        
        asignaciones_inicial = cuenta.get_numero_asignaciones()
        cuenta.iniciar_proceso_traslado("FUNC001")  # Mismo funcionario que creó la cuenta
        
        # 🔥 NUEVO COMPORTAMIENTO: Debe registrar la operación
        assert cuenta.get_numero_asignaciones() == asignaciones_inicial + 1
        
        # Verificar que la nueva asignación es de tipo INICIO_PROCESO
        ultima_asignacion = cuenta.historial_asignaciones[-1]
        assert ultima_asignacion.tipo_asignacion == TipoAsignacion.INICIO_PROCESO
        assert ultima_asignacion.funcionario_id == "FUNC001"

    def test_completar_proceso_traslado_mismo_funcionario_registra_operacion(self):
        """Test que completar proceso registra operación aunque sea mismo funcionario"""
        cuenta = Cuenta.crear_nueva_cuenta(
            placa=Placa("ABC123"),
            tipo_servicio=TipoServicio.PARTICULAR,
            funcionario_creador="FUNC001"
        )
        
        cuenta.iniciar_proceso_traslado("FUNC001")
        asignaciones_antes_completar = cuenta.get_numero_asignaciones()
        
        cuenta.completar_proceso_traslado("FUNC001")  # Mismo funcionario
        
        # 🔥 NUEVO COMPORTAMIENTO: Debe registrar la operación
        assert cuenta.get_numero_asignaciones() == asignaciones_antes_completar + 1
        
        # Verificar que la nueva asignación es de tipo COMPLETAR_PROCESO
        ultima_asignacion = cuenta.historial_asignaciones[-1]
        assert ultima_asignacion.tipo_asignacion == TipoAsignacion.COMPLETAR_PROCESO
        assert ultima_asignacion.funcionario_id == "FUNC001"

    def test_flujo_completo_mismo_funcionario_auditoria_completa(self):
        """Test flujo completo con mismo funcionario mantiene auditoría completa"""
        cuenta = Cuenta.crear_nueva_cuenta(
            placa=Placa("AUD123"),
            tipo_servicio=TipoServicio.PARTICULAR,
            funcionario_creador="FUNC001"
        )
        
        # Todo el flujo con el mismo funcionario
        cuenta.iniciar_proceso_traslado("FUNC001")
        cuenta.completar_proceso_traslado("FUNC001")
        
        # Verificar que se registraron TODAS las operaciones
        tipos_operaciones = [h.tipo_asignacion for h in cuenta.historial_asignaciones]
        assert tipos_operaciones == [
            TipoAsignacion.CREACION,
            TipoAsignacion.INICIO_PROCESO,     # ✅ Ahora se registra
            TipoAsignacion.COMPLETAR_PROCESO   # ✅ Ahora se registra
        ]
        
        # Todos los registros deben tener el mismo funcionario
        funcionarios = [h.funcionario_id for h in cuenta.historial_asignaciones]
        assert all(f == "FUNC001" for f in funcionarios)
        
        # Verificar timestamps progresivos
        fechas = [h.fecha_asignacion for h in cuenta.historial_asignaciones]
        assert fechas[0] <= fechas[1] <= fechas[2]  # Orden cronológico

    def test_get_asignaciones_por_tipo_con_auditoria_completa(self):
        """Test que get_asignaciones_por_tipo funciona correctamente con auditoría completa"""
        cuenta = Cuenta.crear_nueva_cuenta(
            placa=Placa("TIP123"),
            tipo_servicio=TipoServicio.PARTICULAR,
            funcionario_creador="FUNC001"
        )
        
        # Realizar operaciones
        cuenta.iniciar_proceso_traslado("FUNC001")
        cuenta.completar_proceso_traslado("FUNC001")
        cuenta.iniciar_proceso_radicacion("FUNC001")
        cuenta.completar_proceso_radicacion("FUNC001")
        
        # Verificar conteos por tipo
        creaciones = cuenta.get_asignaciones_por_tipo("creacion")
        inicios = cuenta.get_asignaciones_por_tipo("inicio_proceso")
        completaciones = cuenta.get_asignaciones_por_tipo("completar_proceso")
        
        assert len(creaciones) == 1
        assert len(inicios) == 2      # ✅ Ahora son 2 (traslado + radicación)
        assert len(completaciones) == 2  # ✅ Ahora son 2 (traslado + radicación)

    def test_comparacion_antes_despues_auditoria_completa(self):
        """Test que demuestra la diferencia entre comportamiento anterior y nuevo"""
        cuenta = Cuenta.crear_nueva_cuenta(
            placa=Placa("CMP123"),
            tipo_servicio=TipoServicio.PARTICULAR,
            funcionario_creador="FUNC001"
        )
        
        # ANTES: Solo se registraba si cambiaba funcionario
        # AHORA: Se registra SIEMPRE
        
        # Operaciones con el mismo funcionario
        cuenta.iniciar_proceso_traslado("FUNC001")      # ✅ NUEVO: Se registra
        cuenta.completar_proceso_traslado("FUNC001")    # ✅ NUEVO: Se registra
        
        # Operaciones con funcionario diferente (siempre se registraban)
        cuenta.iniciar_proceso_radicacion("FUNC002")    # ✅ Ya se registraba
        cuenta.completar_proceso_radicacion("FUNC002")  # ✅ NUEVO: Se registra
        
        # Verificar conteo total
        # ANTES hubiera sido: 3 (CREACION + INICIO_RADICACION + ¿?)
        # AHORA es: 5 (CREACION + INICIO_TRASLADO + COMPLETAR_TRASLADO + INICIO_RADICACION + COMPLETAR_RADICACION)
        assert cuenta.get_numero_asignaciones() == 5
        
        # Verificar que todas las operaciones críticas están registradas
        tipos_reales = [h.tipo_asignacion for h in cuenta.historial_asignaciones]
        assert tipos_reales.count(TipoAsignacion.INICIO_PROCESO) == 2
        assert tipos_reales.count(TipoAsignacion.COMPLETAR_PROCESO) == 2
        assert tipos_reales.count(TipoAsignacion.CREACION) == 1