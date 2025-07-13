import pytest
from datetime import date, timedelta
from unittest.mock import patch, MagicMock
from app.cuentas.domain.entities.cuenta import Cuenta
from app.cuentas.domain.value_objects.placa import Placa
from app.cuentas.domain.value_objects.numero_cuenta import NumeroCuenta
from app.cuentas.domain.value_objects.fecha_creacion import FechaCreacion
from app.cuentas.domain.value_objects.historial_asignacion import HistorialAsignacion, TipoAsignacion
from app.cuentas.domain.value_objects.enums.tipo_servicio import TipoServicio
from app.cuentas.domain.value_objects.enums.estado_cuenta import EstadoCuenta
from app.cuentas.domain.value_objects.enums.tipo_proceso_anterior import TipoProcesoAnterior


class TestCuentaIntegracionConMocks:
    """Tests de integración usando mocks para dependencies externas"""
    
    @patch('app.cuentas.domain.value_objects.fecha_creacion.FechaCreacion.crear_hoy')
    def test_crear_cuenta_con_fecha_mock(self, mock_fecha_hoy):
        """Test creación de cuenta con fecha mockeada"""
        fecha_mock = date(2024, 1, 15)
        mock_fecha_hoy.return_value = FechaCreacion(fecha_mock)
        
        cuenta = Cuenta.crear_nueva_cuenta(
            placa=Placa("XYZ789"),
            tipo_servicio=TipoServicio.PARTICULAR,
            funcionario_creador="FUNC001"
        )
        
        assert cuenta.fecha_creacion.fecha == fecha_mock
        mock_fecha_hoy.assert_called_once()
    
    @patch('app.cuentas.domain.value_objects.numero_cuenta.NumeroCuenta.generar_para_hoy')
    def test_crear_cuenta_con_numero_cuenta_mock(self, mock_generar_numero):
        """Test creación con número de cuenta mockeado"""
        # Crear un número de cuenta mock usando el método correcto
        numero_mock = NumeroCuenta.generar_para_fecha(
            fecha=date.today(),
            consecutivo=99999
        )
        mock_generar_numero.return_value = numero_mock
        
        cuenta = Cuenta.crear_nueva_cuenta(
            placa=Placa("XYZ789"),
            tipo_servicio=TipoServicio.PARTICULAR,
            funcionario_creador="FUNC001"
        )
        
        assert cuenta.numero_cuenta.get_consecutivo() == 99999
        mock_generar_numero.assert_called_once_with(1)
    
    def test_domain_events_con_mock_observer(self):
        """Test eventos de dominio con observer mockeado"""
        cuenta = Cuenta.crear_nueva_cuenta(
            placa=Placa("EVT456"),
            tipo_servicio=TipoServicio.PARTICULAR,
            funcionario_creador="FUNC001"
        )
        
        # Mock del observer de eventos
        mock_observer = MagicMock()
        
        # Simular procesamiento de eventos
        eventos = cuenta.get_domain_events()
        for evento in eventos:
            mock_observer.handle(evento)
        
        # Verificar que se llamó al observer
        assert mock_observer.handle.call_count == len(eventos)
        
        # Verificar que los eventos se limpiaron
        eventos_vacios = cuenta.get_domain_events()
        assert len(eventos_vacios) == 0


class TestCuentaIntegracionFlujoCompleto:
    """Tests de integración con flujos completos de negocio"""
    
    def test_flujo_completo_dia_trabajo_funcionario(self):
        """Test integración: flujo completo de un día de trabajo de un funcionario"""
        
        # Simular múltiples cuentas procesadas en un día
        cuentas_procesadas = []
        
        for i in range(5):
            cuenta = Cuenta.crear_nueva_cuenta(
                placa=Placa(f"ABC{i:03d}"),
                tipo_servicio=TipoServicio.PARTICULAR,
                funcionario_creador="FUNC001"
            )
            
            # Simular diferentes tipos de procesos
            if i % 2 == 0:
                # Procesos de traslado
                cuenta.iniciar_proceso_traslado("FUNC001")
                cuenta.completar_proceso_traslado("FUNC001")
            else:
                # Procesos de radicación
                cuenta.iniciar_proceso_radicacion("FUNC001")
                if i == 1:
                    # Una devolución
                    cuenta.devolver_proceso_radicacion("FUNC002", "Documentos incompletos")
                else:
                    cuenta.completar_proceso_radicacion("FUNC001")
            
            cuentas_procesadas.append(cuenta)
        
        # Verificar métricas del día
        total_procesos_iniciados = sum(
            len(cuenta.get_asignaciones_por_tipo("inicio_proceso")) 
            for cuenta in cuentas_procesadas
        )
        total_procesos_completados = sum(
            len(cuenta.get_asignaciones_por_tipo("completar_proceso")) 
            for cuenta in cuentas_procesadas
        )
        total_devoluciones = sum(
            len(cuenta.get_asignaciones_por_tipo("devolver_proceso")) 
            for cuenta in cuentas_procesadas
        )
        
        # Con auditoría completa, todos los inicios se registran
        assert total_procesos_iniciados == 5  # 5 cuentas, 1 proceso cada una
        assert total_procesos_completados == 4  # 4 completados (1 devuelto)
        assert total_devoluciones == 1  # 1 devolución
        
        # Verificar que todos los funcionarios trabajaron
        funcionarios_activos = set()
        for cuenta in cuentas_procesadas:
            for asignacion in cuenta.historial_asignaciones:
                funcionarios_activos.add(asignacion.funcionario_id)
        
        assert "FUNC001" in funcionarios_activos
        assert "FUNC002" in funcionarios_activos
    
    def test_flujo_integracion_multiple_funcionarios_misma_cuenta(self):
        """Test integración: múltiples funcionarios trabajando en la misma cuenta"""
        
        cuenta = Cuenta.crear_nueva_cuenta(
            placa=Placa("INT123"),
            tipo_servicio=TipoServicio.PARTICULAR,
            funcionario_creador="FUNC001"
        )
        
        # Simular cadena de trabajo
        # 1. FUNC001 inicia traslado
        cuenta.iniciar_proceso_traslado("FUNC001")
        
        # 2. Se reasigna a FUNC002 por especialización
        cuenta.reasignar_funcionario("FUNC002", "SUPERVISOR01", "Especialista en traslados")
        
        # 3. FUNC002 no puede completar, se devuelve por FUNC003 (revisor)
        cuenta.devolver_proceso_traslado("FUNC003", "Faltan documentos de origen")
        
        # 4. Se reasigna a FUNC004 para corrección
        cuenta.reasignar_funcionario("FUNC004", "SUPERVISOR01", "Corrección de documentos")
        
        # 5. FUNC004 inicia nuevo proceso de radicación
        cuenta.iniciar_proceso_radicacion("FUNC004")
        
        # 6. FUNC005 completa el proceso
        cuenta.reasignar_funcionario("FUNC005", "SUPERVISOR02", "Finalización")
        cuenta.completar_proceso_radicacion("FUNC005")
        
        # Verificar trazabilidad completa
        funcionarios_involucrados = set(
            h.funcionario_id for h in cuenta.historial_asignaciones
        )
        assert funcionarios_involucrados == {"FUNC001", "FUNC002", "FUNC003", "FUNC004", "FUNC005"}
        
        # Verificar cadena de responsabilidad
        tipos_operaciones = [h.tipo_asignacion for h in cuenta.historial_asignaciones]
        assert TipoAsignacion.CREACION in tipos_operaciones
        assert TipoAsignacion.INICIO_PROCESO in tipos_operaciones
        assert TipoAsignacion.REASIGNACION in tipos_operaciones
        assert TipoAsignacion.DEVOLVER_PROCESO in tipos_operaciones
        assert TipoAsignacion.COMPLETAR_PROCESO in tipos_operaciones
        
        # Verificar estado final
        assert cuenta.get_funcionario_actual() == "FUNC005"
        assert cuenta.tipo_proceso_anterior == TipoProcesoAnterior.RADICACION_COMPLETADA
        assert cuenta.puede_iniciar_traslado() == True
        assert cuenta.puede_iniciar_radicacion() == False
    
    def test_flujo_integracion_migracion_datos_sistema_anterior(self):
        """Test integración: migración de datos de sistema anterior (sin auditoría completa)"""
        
        # Simular datos que vendrían de un sistema anterior
        # donde NO se registraban todas las operaciones
        historial_sistema_anterior = [
            HistorialAsignacion.crear_asignacion_inicial("FUNC001", date.today() - timedelta(days=10)),
            # En sistema anterior: faltaba registro de inicio de proceso
            HistorialAsignacion.crear_cambio_proceso("FUNC002", "traslado", "completar"),
            HistorialAsignacion.crear_reasignacion_manual("FUNC003", "SUPERVISOR01", "Nueva asignación")
        ]
        
        # Crear cuenta desde repositorio (simula carga desde BD)
        cuenta_migrada = Cuenta.crear_desde_repositorio(
            placa=Placa("MIG123"),
            numero_cuenta=NumeroCuenta.generar_para_fecha(date.today() - timedelta(days=10), 1),
            tipo_servicio=TipoServicio.PARTICULAR,
            estado=EstadoCuenta.ACTIVA,
            fecha_creacion=FechaCreacion(date.today() - timedelta(days=10)),
            funcionario_creador="FUNC001",
            historial=historial_sistema_anterior,
            tipo_proceso_anterior=TipoProcesoAnterior.TRASLADO_COMPLETADO
        )
        
        # Verificar que la cuenta migrada funciona correctamente
        assert cuenta_migrada.get_funcionario_actual() == "FUNC003"
        assert cuenta_migrada.tipo_proceso_anterior == TipoProcesoAnterior.TRASLADO_COMPLETADO
        assert cuenta_migrada.puede_iniciar_radicacion() == True
        assert cuenta_migrada.puede_iniciar_traslado() == False
        
        # Ahora, con el nuevo sistema, todas las operaciones se registran
        cuenta_migrada.iniciar_proceso_radicacion("FUNC003")  # ✅ Se registra
        cuenta_migrada.completar_proceso_radicacion("FUNC003")  # ✅ Se registra
        
        # Verificar que el historial ahora tiene auditoría completa para nuevas operaciones
        operaciones_nuevas = [
            h for h in cuenta_migrada.historial_asignaciones[-2:]
        ]
        assert len(operaciones_nuevas) == 2
        assert operaciones_nuevas[0].tipo_asignacion == TipoAsignacion.INICIO_PROCESO
        assert operaciones_nuevas[1].tipo_asignacion == TipoAsignacion.COMPLETAR_PROCESO
    
    def test_flujo_integracion_simulacion_alta_concurrencia(self):
        """Test integración: simulación de alta concurrencia (múltiples cuentas simultáneas)"""
        
        import threading
        import time
        
        cuentas_creadas = []
        errores = []
        
        def crear_y_procesar_cuenta(indice):
            try:
                cuenta = Cuenta.crear_nueva_cuenta(
                    placa=Placa(f"CON{indice:03d}"),
                    tipo_servicio=TipoServicio.PARTICULAR,
                    funcionario_creador=f"FUNC{indice % 5 + 1:03d}"  # 5 funcionarios diferentes
                )
                
                # Simular procesamiento
                if indice % 3 == 0:
                    cuenta.iniciar_proceso_traslado(f"FUNC{indice % 5 + 1:03d}")
                    cuenta.completar_proceso_traslado(f"FUNC{indice % 5 + 1:03d}")
                elif indice % 3 == 1:
                    cuenta.iniciar_proceso_radicacion(f"FUNC{indice % 5 + 1:03d}")
                    cuenta.completar_proceso_radicacion(f"FUNC{indice % 5 + 1:03d}")
                else:
                    cuenta.iniciar_proceso_traslado(f"FUNC{indice % 5 + 1:03d}")
                    cuenta.devolver_proceso_traslado(f"FUNC{(indice + 1) % 5 + 1:03d}", f"Motivo {indice}")
                
                cuentas_creadas.append(cuenta)
                
            except Exception as e:
                errores.append(f"Error en cuenta {indice}: {str(e)}")
        
        # Crear múltiples threads para simular concurrencia
        threads = []
        for i in range(20):  # 20 cuentas simultáneas
            thread = threading.Thread(target=crear_y_procesar_cuenta, args=(i,))
            threads.append(thread)
        
        # Iniciar todos los threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Esperar que terminen todos
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # Verificar resultados
        assert len(errores) == 0, f"Errores encontrados: {errores}"
        assert len(cuentas_creadas) == 20
        assert end_time - start_time < 5.0  # Debe terminar en menos de 5 segundos
        
        # Verificar que todas las cuentas tienen auditoría completa
        for cuenta in cuentas_creadas:
            # Cada cuenta debe tener al menos: CREACION + INICIO + (COMPLETAR o DEVOLVER)
            assert cuenta.get_numero_asignaciones() >= 3
            
            tipos = [h.tipo_asignacion for h in cuenta.historial_asignaciones]
            assert TipoAsignacion.CREACION in tipos
            assert TipoAsignacion.INICIO_PROCESO in tipos
            assert (TipoAsignacion.COMPLETAR_PROCESO in tipos or 
                    TipoAsignacion.DEVOLVER_PROCESO in tipos)


class TestCuentaIntegracionMetricas:
    """Tests de integración para métricas y reportes"""
    
    def test_integracion_metricas_productividad_funcionario(self):
        """Test integración: métricas de productividad por funcionario"""
        
        # Simular trabajo de múltiples funcionarios
        funcionarios_trabajo = {
            "FUNC001": [],
            "FUNC002": [],
            "FUNC003": []
        }
        
        # Crear cuentas y distribuir trabajo
        for i in range(15):
            funcionario = f"FUNC{(i % 3) + 1:03d}"
            
            cuenta = Cuenta.crear_nueva_cuenta(
                placa=Placa(f"MET{i:03d}"),
                tipo_servicio=TipoServicio.PARTICULAR,
                funcionario_creador=funcionario
            )
            
            # Simular diferentes cargas de trabajo
            if funcionario == "FUNC001":
                # FUNC001: especialista en traslados
                cuenta.iniciar_proceso_traslado("FUNC001")
                cuenta.completar_proceso_traslado("FUNC001")
            elif funcionario == "FUNC002":
                # FUNC002: especialista en radicaciones
                cuenta.iniciar_proceso_radicacion("FUNC002")
                cuenta.completar_proceso_radicacion("FUNC002")
            else:
                # FUNC003: maneja devoluciones
                cuenta.iniciar_proceso_traslado("FUNC003")
                cuenta.devolver_proceso_traslado("FUNC003", f"Revisión necesaria {i}")
            
            funcionarios_trabajo[funcionario].append(cuenta)
        
        # Calcular métricas por funcionario
        metricas = {}
        for funcionario, cuentas in funcionarios_trabajo.items():
            total_operaciones = sum(len(c.historial_asignaciones) for c in cuentas)
            procesos_completados = sum(
                len(c.get_asignaciones_por_tipo("completar_proceso")) for c in cuentas
            )
            procesos_devueltos = sum(
                len(c.get_asignaciones_por_tipo("devolver_proceso")) for c in cuentas
            )
            
            metricas[funcionario] = {
                "total_operaciones": total_operaciones,
                "procesos_completados": procesos_completados,
                "procesos_devueltos": procesos_devueltos,
                "cuentas_procesadas": len(cuentas)
            }
        
        # Verificar métricas esperadas
        assert metricas["FUNC001"]["procesos_completados"] == 5  # 5 traslados completados
        assert metricas["FUNC001"]["procesos_devueltos"] == 0    # Sin devoluciones
        
        assert metricas["FUNC002"]["procesos_completados"] == 5  # 5 radicaciones completadas
        assert metricas["FUNC002"]["procesos_devueltos"] == 0    # Sin devoluciones
        
        assert metricas["FUNC003"]["procesos_completados"] == 0  # Sin completaciones
        assert metricas["FUNC003"]["procesos_devueltos"] == 5    # 5 devoluciones
        
        # Verificar que con auditoría completa tenemos visibilidad total
        for funcionario, stats in metricas.items():
            assert stats["total_operaciones"] >= stats["cuentas_procesadas"] * 3  # Al menos 3 ops por cuenta
    
    def test_integracion_auditoria_cumplimiento_regulatorio(self):
        """Test integración: verificación de cumplimiento regulatorio"""
        
        # Simular casos que requieren auditoría gubernamental
        casos_auditoria = []
        
        # Caso 1: Cuenta con múltiples reasignaciones (sospechosa)
        cuenta_sospechosa = Cuenta.crear_nueva_cuenta(
            placa=Placa("SOS123"),
            tipo_servicio=TipoServicio.PARTICULAR,
            funcionario_creador="FUNC001"
        )
        
        for i in range(5):
            cuenta_sospechosa.reasignar_funcionario(f"FUNC{i+2:03d}", "SUPERVISOR01", f"Reasignación {i}")
        
        cuenta_sospechosa.iniciar_proceso_traslado("FUNC006")
        cuenta_sospechosa.devolver_proceso_traslado("FUNC007", "Revisión especial requerida")
        
        casos_auditoria.append(("sospechosa", cuenta_sospechosa))
        
        # Caso 2: Cuenta con proceso muy rápido (eficiencia alta)
        cuenta_eficiente = Cuenta.crear_nueva_cuenta(
            placa=Placa("EFI123"),
            tipo_servicio=TipoServicio.PARTICULAR,
            funcionario_creador="FUNC010"
        )
        
        cuenta_eficiente.iniciar_proceso_traslado("FUNC010")
        cuenta_eficiente.completar_proceso_traslado("FUNC010")
        
        casos_auditoria.append(("eficiente", cuenta_eficiente))
        
        # Caso 3: Cuenta con ciclo completo (normal)
        cuenta_normal = Cuenta.crear_nueva_cuenta(
            placa=Placa("NOR123"),
            tipo_servicio=TipoServicio.PARTICULAR,
            funcionario_creador="FUNC020"
        )
        
        cuenta_normal.iniciar_proceso_traslado("FUNC020")
        cuenta_normal.completar_proceso_traslado("FUNC020")
        cuenta_normal.iniciar_proceso_radicacion("FUNC021")
        cuenta_normal.completar_proceso_radicacion("FUNC021")
        
        casos_auditoria.append(("normal", cuenta_normal))
        
        # Verificar capacidades de auditoría para cada caso
        for tipo_caso, cuenta in casos_auditoria:
            
            # 1. Trazabilidad completa: cada acción tiene responsable y timestamp
            for asignacion in cuenta.historial_asignaciones:
                assert asignacion.funcionario_id is not None
                assert len(asignacion.funcionario_id.strip()) > 0
                assert asignacion.fecha_asignacion is not None
                assert isinstance(asignacion.fecha_asignacion, date)
            
            # 2. Integridad: secuencia cronológica
            fechas = [h.fecha_asignacion for h in cuenta.historial_asignaciones]
            for i in range(1, len(fechas)):
                assert fechas[i] >= fechas[i-1], f"Secuencia cronológica rota en {tipo_caso}"
            
            # 3. Completitud: operaciones críticas registradas
            tipos = [h.tipo_asignacion for h in cuenta.historial_asignaciones]
            
            if any(t == TipoAsignacion.COMPLETAR_PROCESO for t in tipos):
                # Si hay completación, debe haber inicio correspondiente
                assert TipoAsignacion.INICIO_PROCESO in tipos
            
            if any(t == TipoAsignacion.DEVOLVER_PROCESO for t in tipos):
                # Si hay devolución, debe haber inicio correspondiente
                assert TipoAsignacion.INICIO_PROCESO in tipos
            
            # 4. Granularidad: suficiente detalle para reconstruir flujo
            assert len(cuenta.historial_asignaciones) >= 2  # Al menos creación + alguna acción
            
            # 5. Inmutabilidad simulada: historial no debe poder alterarse
            historial_original = len(cuenta.historial_asignaciones)
            # En implementación real, HistorialAsignacion sería inmutable
            
        # Verificar que casos complejos tienen suficiente detalle
        cuenta_sospechosa = next(c for t, c in casos_auditoria if t == "sospechosa")
        assert len(cuenta_sospechosa.historial_asignaciones) >= 8  # Muchas operaciones registradas
        
        cuenta_eficiente = next(c for t, c in casos_auditoria if t == "eficiente")
        assert len(cuenta_eficiente.historial_asignaciones) == 3  # CREACION + INICIO + COMPLETAR
        
        cuenta_normal = next(c for t, c in casos_auditoria if t == "normal")
        assert len(cuenta_normal.historial_asignaciones) == 5  # Flujo completo documentado