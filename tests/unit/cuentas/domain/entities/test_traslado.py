import pytest
from datetime import date, timedelta

from app.cuentas.domain.entities.traslado import Traslado
from app.cuentas.domain.value_objects.placa import Placa
from app.cuentas.domain.value_objects.fecha_tramite import FechaTramite
from app.cuentas.domain.value_objects.fecha_vencimiento import FechaVencimiento
from app.cuentas.domain.value_objects.ubicacion import Ubicacion, UbicacionesPredefinidas
from app.cuentas.domain.value_objects.observacion import Observacion
from app.cuentas.domain.value_objects.enums.estado_traslado import EstadoTraslado


class TestTrasladoCreacion:
    """Tests para creación de traslados"""
    
    @pytest.fixture
    def datos_traslado_base(self):
        """Datos base para crear traslado"""
        return {
            'placa': Placa("ABC123"),
            'organismo_destino': UbicacionesPredefinidas.MEDELLIN,
            'fecha_tramite': FechaTramite.crear_hoy(),
            'funcionario_envia': "JPEREZ"
        }
    
    def test_crear_traslado_valido(self, datos_traslado_base):
        """Test creación de traslado con datos válidos"""
        fecha_vencimiento = FechaVencimiento.calcular_desde_tramite(datos_traslado_base['fecha_tramite'])
        
        traslado = Traslado(
            placa=datos_traslado_base['placa'],
            organismo_destino=datos_traslado_base['organismo_destino'],
            fecha_tramite=datos_traslado_base['fecha_tramite'],
            fecha_vencimiento=fecha_vencimiento,
            funcionario_envia=datos_traslado_base['funcionario_envia']
        )
        
        assert traslado.placa == datos_traslado_base['placa']
        assert traslado.organismo_destino == datos_traslado_base['organismo_destino']
        assert traslado.funcionario_envia == "JPEREZ"
        assert traslado.estado == EstadoTraslado.ENVIADO_ORGANISMO_DESTINO
        assert traslado.funcionario_actual == "JPEREZ"
        assert traslado.fecha_ultima_actualizacion == date.today()
        assert traslado.observaciones.esta_vacia()
    
    def test_crear_traslado_factory_method(self, datos_traslado_base):
        """Test factory method para crear traslado"""
        traslado = Traslado.crear_nuevo(
            placa=datos_traslado_base['placa'],
            organismo_destino=datos_traslado_base['organismo_destino'],
            fecha_tramite=datos_traslado_base['fecha_tramite'],
            funcionario_envia=datos_traslado_base['funcionario_envia'],
            observaciones_iniciales="Envío urgente por vencimiento"
        )
        
        assert traslado.get_placa_valor() == "ABC123"
        assert traslado.get_codigo_organismo_destino() == "MEDELLIN"
        assert not traslado.observaciones.esta_vacia()
        assert "urgente" in traslado.observaciones.valor.lower()
        
        # Verificar cálculo automático de vencimiento (60 días)
        dias_diferencia = (traslado.fecha_vencimiento.fecha - traslado.fecha_tramite.fecha).days
        assert dias_diferencia == 60
    
    def test_crear_traslado_funcionario_normalizado(self, datos_traslado_base):
        """Test normalización de funcionario que envía"""
        datos_traslado_base['funcionario_envia'] = "  ana.garcia  "
        fecha_vencimiento = FechaVencimiento.calcular_desde_tramite(datos_traslado_base['fecha_tramite'])
        
        traslado = Traslado(
            placa=datos_traslado_base['placa'],
            organismo_destino=datos_traslado_base['organismo_destino'],
            fecha_tramite=datos_traslado_base['fecha_tramite'],
            fecha_vencimiento=fecha_vencimiento,
            funcionario_envia=datos_traslado_base['funcionario_envia']
        )
        
        assert traslado.funcionario_envia == "ANA.GARCIA"
    
    def test_crear_traslado_funcionario_vacio_error(self, datos_traslado_base):
        """Test error con funcionario vacío"""
        fecha_vencimiento = FechaVencimiento.calcular_desde_tramite(datos_traslado_base['fecha_tramite'])
        
        with pytest.raises(ValueError, match="funcionario que envía no puede estar vacío"):
            Traslado(
                placa=datos_traslado_base['placa'],
                organismo_destino=datos_traslado_base['organismo_destino'],
                fecha_tramite=datos_traslado_base['fecha_tramite'],
                fecha_vencimiento=fecha_vencimiento,
                funcionario_envia=""
            )
    
    def test_crear_traslado_fechas_incoherentes_error(self, datos_traslado_base):
        """Test error con fechas incoherentes"""
        # Fecha de vencimiento anterior a fecha de trámite
        fecha_vencimiento = FechaVencimiento.crear_para_fecha(
            datos_traslado_base['fecha_tramite'].fecha - timedelta(days=1)
        )
        
        with pytest.raises(ValueError, match="fecha de vencimiento debe ser posterior"):
            Traslado(
                placa=datos_traslado_base['placa'],
                organismo_destino=datos_traslado_base['organismo_destino'],
                fecha_tramite=datos_traslado_base['fecha_tramite'],
                fecha_vencimiento=fecha_vencimiento,
                funcionario_envia=datos_traslado_base['funcionario_envia']
            )
    
    def test_crear_traslado_value_objects_invalidos(self, datos_traslado_base):
        """Test error con value objects de tipo incorrecto"""
        with pytest.raises(ValueError, match="placa debe ser una instancia válida"):
            Traslado(
                placa="ABC123",  # String en lugar de Placa
                organismo_destino=datos_traslado_base['organismo_destino'],
                fecha_tramite=datos_traslado_base['fecha_tramite'],
                fecha_vencimiento=FechaVencimiento.calcular_desde_tramite(datos_traslado_base['fecha_tramite']),
                funcionario_envia=datos_traslado_base['funcionario_envia']
            )


class TestTrasladoConsultas:
    """Tests para métodos de consulta"""
    
    @pytest.fixture
    def traslado_base(self):
        """Traslado base para tests"""
        return Traslado.crear_nuevo(
            placa=Placa("QRS456"),
            organismo_destino=UbicacionesPredefinidas.BOGOTA_DC,
            fecha_tramite=FechaTramite.crear_hoy(),
            funcionario_envia="MLOPEZ"
        )
    
    def test_get_informacion_basica(self, traslado_base):
        """Test obtener información básica"""
        assert traslado_base.get_placa_valor() == "QRS456"
        assert traslado_base.get_codigo_organismo_destino() == "BOGOTA_DC"
        assert traslado_base.get_nombre_organismo_destino() == "Bogota Dc"
        assert "Bogotá D.C." in traslado_base.get_ubicacion_completa_destino()
    
    def test_get_funcionario_responsable(self, traslado_base):
        """Test obtener funcionario responsable"""
        assert traslado_base.get_funcionario_responsable() == "MLOPEZ"
        
        # Cambiar funcionario actual
        traslado_base.marcar_como_revisado("NUEVOFUNC")
        assert traslado_base.get_funcionario_responsable() == "NUEVOFUNC"
    
    def test_get_dias_informacion_temporal(self, traslado_base):
        """Test información temporal"""
        assert traslado_base.get_dias_en_proceso() == 0  # Creado hoy
        assert traslado_base.get_dias_restantes_vencimiento() == 60  # 60 días para vencer
        assert traslado_base.get_nivel_urgencia() == "normal"
    
    def test_get_nivel_urgencia_por_vencimiento(self):
        """Test niveles de urgencia según vencimiento"""
        # Traslado vencido
        fecha_pasada = FechaTramite.crear_para_fecha(date.today() - timedelta(days=70))
        traslado_vencido = Traslado.crear_nuevo(
            placa=Placa("VEN123"),
            organismo_destino=UbicacionesPredefinidas.CALI,
            fecha_tramite=fecha_pasada,
            funcionario_envia="JPEREZ"
        )
        assert traslado_vencido.get_nivel_urgencia() == "vencida"
        
        # Traslado crítico (3 días)
        fecha_critica = FechaTramite.crear_para_fecha(date.today() - timedelta(days=58))
        traslado_critico = Traslado.crear_nuevo(
            placa=Placa("CRI123"),
            organismo_destino=UbicacionesPredefinidas.MANIZALES,
            fecha_tramite=fecha_critica,
            funcionario_envia="JPEREZ"
        )
        assert traslado_critico.get_nivel_urgencia() == "critica"


class TestTrasladoValidacionesEstado:
    """Tests para validaciones de estado"""
    
    @pytest.fixture
    def traslado_enviado(self):
        """Traslado en estado inicial"""
        return Traslado.crear_nuevo(
            placa=Placa("EST123"),
            organismo_destino=UbicacionesPredefinidas.FUNZA,
            fecha_tramite=FechaTramite.crear_hoy(),
            funcionario_envia="JPEREZ"
        )
    
    def test_estado_inicial_validaciones(self, traslado_enviado):
        """Test validaciones en estado inicial"""
        assert not traslado_enviado.esta_vencido()
        assert not traslado_enviado.esta_por_vencer()
        assert not traslado_enviado.es_critico()
        assert not traslado_enviado.esta_en_revision()
        assert not traslado_enviado.tiene_novedades()
        assert not traslado_enviado.esta_completado()
        assert not traslado_enviado.fue_devuelto()
        assert not traslado_enviado.esta_en_estado_final()
    
    def test_validaciones_vencimiento(self):
        """Test validaciones específicas de vencimiento"""
        # Traslado que vence en 5 días (alerta)
        fecha_alerta = FechaTramite.crear_para_fecha(date.today() - timedelta(days=56))
        traslado_alerta = Traslado.crear_nuevo(
            placa=Placa("ALE123"),
            organismo_destino=UbicacionesPredefinidas.MARIQUITA,
            fecha_tramite=fecha_alerta,
            funcionario_envia="JPEREZ"
        )
        
        assert traslado_alerta.esta_por_vencer()
        assert not traslado_alerta.es_critico()
        assert traslado_alerta.get_nivel_urgencia() == "alerta"
        
        # Traslado crítico (2 días)
        fecha_critica = FechaTramite.crear_para_fecha(date.today() - timedelta(days=59))
        traslado_critico = Traslado.crear_nuevo(
            placa=Placa("CRI123"),
            organismo_destino=UbicacionesPredefinidas.SOGAMOSO,
            fecha_tramite=fecha_critica,
            funcionario_envia="JPEREZ"
        )
        
        assert traslado_critico.esta_por_vencer()
        assert traslado_critico.es_critico()
        assert traslado_critico.get_nivel_urgencia() == "critica"


class TestTrasladoReglasTansiciones:
    """Tests para reglas de transiciones de estado"""
    
    @pytest.fixture
    def traslado_enviado(self):
        """Traslado enviado para tests de transición"""
        return Traslado.crear_nuevo(
            placa=Placa("TRA123"),
            organismo_destino=UbicacionesPredefinidas.MEDELLIN,
            fecha_tramite=FechaTramite.crear_hoy(),
            funcionario_envia="JPEREZ"
        )
    
    def test_puede_pasar_a_revision_desde_enviado(self, traslado_enviado):
        """Test puede pasar a revisión desde enviado"""
        assert traslado_enviado.puede_pasar_a_revision()
        assert not traslado_enviado.puede_completar_traslado()
        assert not traslado_enviado.puede_reportar_novedad()
        assert not traslado_enviado.puede_resolver_novedad()
    
    def test_puede_ser_devuelto_admin(self, traslado_enviado):
        """Test admin puede devolver desde cualquier estado"""
        assert traslado_enviado.puede_ser_devuelto(es_admin=True)
        
        traslado_enviado.marcar_como_revisado("REVISOR")
        assert traslado_enviado.puede_ser_devuelto(es_admin=True)
        
        traslado_enviado.completar_traslado("COMPLETADOR")
        assert not traslado_enviado.puede_ser_devuelto(es_admin=True)  # Estado final


class TestTrasladoTransicionesEstado:
    """Tests para transiciones de estado"""
    
    @pytest.fixture
    def traslado_para_transiciones(self):
        """Traslado para tests de transiciones"""
        return Traslado.crear_nuevo(
            placa=Placa("TRN123"),
            organismo_destino=UbicacionesPredefinidas.CALI,
            fecha_tramite=FechaTramite.crear_hoy(),
            funcionario_envia="JPEREZ",
            observaciones_iniciales="Traslado de prueba"
        )
    
    def test_marcar_como_revisado_exitoso(self, traslado_para_transiciones):
        """Test marcar como revisado exitosamente"""
        traslado_para_transiciones.marcar_como_revisado("REVISOR001")
        
        assert traslado_para_transiciones.estado == EstadoTraslado.REVISADO
        assert traslado_para_transiciones.esta_en_revision()
        assert traslado_para_transiciones.funcionario_actual == "REVISOR001"
        assert traslado_para_transiciones.fecha_ultima_actualizacion == date.today()
        
        # Ahora puede completar o reportar novedad
        assert traslado_para_transiciones.puede_completar_traslado()
        assert traslado_para_transiciones.puede_reportar_novedad()
    
    def test_completar_traslado_exitoso(self, traslado_para_transiciones):
        """Test completar traslado exitosamente"""
        traslado_para_transiciones.marcar_como_revisado("REVISOR001")
        traslado_para_transiciones.completar_traslado("COMPLETADOR", "Documentación correcta")
        
        assert traslado_para_transiciones.estado == EstadoTraslado.TRASLADADO
        assert traslado_para_transiciones.esta_completado()
        assert traslado_para_transiciones.esta_en_estado_final()
        assert traslado_para_transiciones.funcionario_actual == "COMPLETADOR"
        
        # Verificar observaciones se actualizaron
        assert "COMPLETADO" in traslado_para_transiciones.observaciones.valor
        assert "correcta" in traslado_para_transiciones.observaciones.valor
    
    def test_reportar_novedad_exitoso(self, traslado_para_transiciones):
        """Test reportar novedad exitosamente"""
        traslado_para_transiciones.marcar_como_revisado("REVISOR001")
        traslado_para_transiciones.reportar_novedad("REVISOR001", "Falta certificado SOAT")
        
        assert traslado_para_transiciones.estado == EstadoTraslado.CON_NOVEDADES
        assert traslado_para_transiciones.tiene_novedades()
        assert not traslado_para_transiciones.esta_en_estado_final()
        
        # Ahora puede resolver novedad
        assert traslado_para_transiciones.puede_resolver_novedad()
        assert not traslado_para_transiciones.puede_completar_traslado()
        
        # Verificar observaciones
        assert "NOVEDAD REPORTADA" in traslado_para_transiciones.observaciones.valor
        assert "SOAT" in traslado_para_transiciones.observaciones.valor
    
    def test_resolver_novedad_exitoso(self, traslado_para_transiciones):
        """Test resolver novedad exitosamente"""
        traslado_para_transiciones.marcar_como_revisado("REVISOR001")
        traslado_para_transiciones.reportar_novedad("REVISOR001", "Documento faltante")
        traslado_para_transiciones.resolver_novedad("RESOLVEDOR", "Documento adjuntado correctamente")
        
        assert traslado_para_transiciones.estado == EstadoTraslado.REVISADO
        assert traslado_para_transiciones.esta_en_revision()
        assert not traslado_para_transiciones.tiene_novedades()
        assert traslado_para_transiciones.funcionario_actual == "RESOLVEDOR"
        
        # Vuelve a poder completar
        assert traslado_para_transiciones.puede_completar_traslado()
        
        # Verificar observaciones incluyen resolución
        assert "NOVEDAD RESUELTA" in traslado_para_transiciones.observaciones.valor
        assert "adjuntado" in traslado_para_transiciones.observaciones.valor
    
    def test_devolver_traslado_exitoso(self, traslado_para_transiciones):
        """Test devolver traslado exitosamente"""
        traslado_para_transiciones.marcar_como_revisado("REVISOR001")
        traslado_para_transiciones.devolver_traslado("ADMIN", "Documentación incompleta", es_admin=True)
        
        assert traslado_para_transiciones.estado == EstadoTraslado.DEVUELTO
        assert traslado_para_transiciones.fue_devuelto()
        assert traslado_para_transiciones.esta_en_estado_final()
        assert traslado_para_transiciones.funcionario_actual == "ADMIN"
        
        # Verificar observaciones
        assert "TRASLADO DEVUELTO" in traslado_para_transiciones.observaciones.valor
        assert "incompleta" in traslado_para_transiciones.observaciones.valor


class TestTrasladoTransicionesError:
    """Tests para errores en transiciones"""
    
    @pytest.fixture
    def traslado_revisado(self):
        """Traslado en estado revisado"""
        traslado = Traslado.crear_nuevo(
            placa=Placa("ERR123"),
            organismo_destino=UbicacionesPredefinidas.FUNZA,
            fecha_tramite=FechaTramite.crear_hoy(),
            funcionario_envia="JPEREZ"
        )
        traslado.marcar_como_revisado("REVISOR")
        return traslado
    
    def test_marcar_revisado_desde_estado_incorrecto(self, traslado_revisado):
        """Test error al marcar como revisado desde estado incorrecto"""
        with pytest.raises(ValueError, match="No se puede pasar a revisión desde estado"):
            traslado_revisado.marcar_como_revisado("OTRO")
    
    def test_completar_traslado_sin_revision_error(self):
        """Test error al completar sin estar en revisión"""
        traslado = Traslado.crear_nuevo(
            placa=Placa("ERR456"),
            organismo_destino=UbicacionesPredefinidas.MARIQUITA,
            fecha_tramite=FechaTramite.crear_hoy(),
            funcionario_envia="JPEREZ"
        )
        
        with pytest.raises(ValueError, match="No se puede completar traslado desde estado"):
            traslado.completar_traslado("COMPLETADOR")
    
    def test_reportar_novedad_estado_incorrecto_error(self):
        """Test error al reportar novedad desde estado incorrecto"""
        traslado = Traslado.crear_nuevo(
            placa=Placa("ERR789"),
            organismo_destino=UbicacionesPredefinidas.SOGAMOSO,
            fecha_tramite=FechaTramite.crear_hoy(),
            funcionario_envia="JPEREZ"
        )
        
        with pytest.raises(ValueError, match="No se puede reportar novedad desde estado"):
            traslado.reportar_novedad("REVISOR", "Alguna novedad")
    
    def test_resolver_novedad_sin_novedades_error(self, traslado_revisado):
        """Test error al resolver novedad sin tener novedades"""
        with pytest.raises(ValueError, match="No se puede resolver novedad desde estado"):
            traslado_revisado.resolver_novedad("RESOLVEDOR", "No hay novedades")
    
    def test_devolver_sin_permisos_error(self, traslado_revisado):
        """Test error al devolver sin permisos de admin"""
        traslado_revisado.completar_traslado("COMPLETADOR")  # Estado final
        
        with pytest.raises(ValueError, match="No se puede devolver traslado desde estado"):
            traslado_revisado.devolver_traslado("NOADMIN", "Motivo", es_admin=False)


class TestTrasladoActualizacionObservaciones:
    """Tests para actualización de observaciones"""
    
    @pytest.fixture
    def traslado_con_observaciones(self):
        """Traslado con observaciones iniciales"""
        return Traslado.crear_nuevo(
            placa=Placa("OBS123"),
            organismo_destino=UbicacionesPredefinidas.BOGOTA_DC,
            fecha_tramite=FechaTramite.crear_hoy(),
            funcionario_envia="JPEREZ",
            observaciones_iniciales="Observación inicial"
        )
    
    def test_actualizar_observaciones_exitoso(self, traslado_con_observaciones):
        """Test actualizar observaciones exitosamente"""
        observaciones_anteriores = traslado_con_observaciones.observaciones.valor
        
        traslado_con_observaciones.actualizar_observaciones("ACTUALIZADOR", "Nueva información relevante")
        
        assert "Nueva información relevante" in traslado_con_observaciones.observaciones.valor
        assert "ACTUALIZADOR" in traslado_con_observaciones.observaciones.valor
        assert traslado_con_observaciones.fecha_ultima_actualizacion == date.today()
        
        # Las observaciones anteriores se mantienen
        assert "inicial" in traslado_con_observaciones.observaciones.valor.lower()
    
    def test_actualizar_observaciones_estado_final_error(self, traslado_con_observaciones):
        """Test error al actualizar observaciones en estado final"""
        traslado_con_observaciones.marcar_como_revisado("REVISOR")
        traslado_con_observaciones.completar_traslado("COMPLETADOR")
        
        with pytest.raises(ValueError, match="No se pueden actualizar observaciones en estado final"):
            traslado_con_observaciones.actualizar_observaciones("ACTUALIZADOR", "Intento actualizar")


class TestTrasladoFactoryMethods:
    """Tests para factory methods"""
    
    def test_crear_desde_repositorio_exitoso(self):
        """Test recrear traslado desde repositorio"""
        placa = Placa("REP123")
        organismo = UbicacionesPredefinidas.MANIZALES
        fecha_tramite = FechaTramite.crear_hoy()
        fecha_vencimiento = FechaVencimiento.calcular_desde_tramite(fecha_tramite)
        observaciones = Observacion.crear_desde_texto("Observación desde repo")
        
        traslado = Traslado.crear_desde_repositorio(
            placa=placa,
            organismo_destino=organismo,
            fecha_tramite=fecha_tramite,
            fecha_vencimiento=fecha_vencimiento,
            funcionario_envia="ORIGINAL",
            estado=EstadoTraslado.REVISADO,
            observaciones=observaciones,
            funcionario_actual="ACTUAL",
            fecha_ultima_actualizacion=date.today() - timedelta(days=1)
        )
        
        assert traslado.placa == placa
        assert traslado.estado == EstadoTraslado.REVISADO
        assert traslado.funcionario_envia == "ORIGINAL"
        assert traslado.funcionario_actual == "ACTUAL"
        assert traslado.observaciones == observaciones
        assert traslado.fecha_ultima_actualizacion == date.today() - timedelta(days=1)


class TestTrasladoRepresentacion:
    """Tests para métodos de representación"""
    
    def test_str_y_repr(self):
        """Test métodos __str__ y __repr__"""
        traslado = Traslado.crear_nuevo(
            placa=Placa("STR123"),
            organismo_destino=UbicacionesPredefinidas.CALI,
            fecha_tramite=FechaTramite.crear_hoy(),
            funcionario_envia="JPEREZ"
        )
        
        str_resultado = str(traslado)
        assert "STR123" in str_resultado
        assert "Cali" in str_resultado
        assert "→" in str_resultado  # Indica dirección del traslado
        
        repr_resultado = repr(traslado)
        assert "Traslado" in repr_resultado
        assert "placa='STR123'" in repr_resultado
        assert "destino='CALI'" in repr_resultado
        assert "estado='enviado_organismo_destino'" in repr_resultado


class TestTrasladoIntegracion:
    """Tests de integración completos"""
    
    def test_flujo_completo_exitoso(self):
        """Test flujo completo de traslado exitoso"""
        # 1. Crear traslado
        traslado = Traslado.crear_nuevo(
            placa=Placa("FLU123"),
            organismo_destino=UbicacionesPredefinidas.MEDELLIN,
            fecha_tramite=FechaTramite.crear_hoy(),
            funcionario_envia="ENVIADOR",
            observaciones_iniciales="Traslado por cambio de residencia"
        )
        
        assert traslado.estado == EstadoTraslado.ENVIADO_ORGANISMO_DESTINO
        
        # 2. Marcar como revisado
        traslado.marcar_como_revisado("REVISOR")
        assert traslado.esta_en_revision()
        
        # 3. Completar traslado
        traslado.completar_traslado("COMPLETADOR", "Documentación verificada")
        assert traslado.esta_completado()
        assert traslado.esta_en_estado_final()
        
        # Verificar trazabilidad completa
        assert "ENVIADOR" == traslado.funcionario_envia
        assert "COMPLETADOR" == traslado.funcionario_actual
        assert "residencia" in traslado.observaciones.valor
        assert "verificada" in traslado.observaciones.valor
    
    def test_flujo_con_novedades(self):
        """Test flujo con novedades y resolución"""
        traslado = Traslado.crear_nuevo(
            placa=Placa("NOV123"),
            organismo_destino=UbicacionesPredefinidas.FUNZA,
            fecha_tramite=FechaTramite.crear_hoy(),
            funcionario_envia="ENVIADOR"
        )
        
        # 1. Revisar
        traslado.marcar_como_revisado("REVISOR")
        
        # 2. Reportar novedad
        traslado.reportar_novedad("REVISOR", "Falta firma del propietario")
        assert traslado.tiene_novedades()
        
        # 3. Resolver novedad
        traslado.resolver_novedad("RESOLVEDOR", "Firma adjuntada")
        assert not traslado.tiene_novedades()
        assert traslado.esta_en_revision()
        
        # 4. Completar
        traslado.completar_traslado("COMPLETADOR")
        assert traslado.esta_completado()
        
        # Verificar todas las observaciones están presentes
        obs = traslado.observaciones.valor
        assert "NOVEDAD REPORTADA" in obs
        assert "firma" in obs.lower()
        assert "NOVEDAD RESUELTA" in obs
        assert "adjuntada" in obs.lower()
    
    def test_flujo_devolucion_admin(self):
        """Test flujo de devolución por admin"""
        traslado = Traslado.crear_nuevo(
            placa=Placa("DEV123"),
            organismo_destino=UbicacionesPredefinidas.MARIQUITA,
            fecha_tramite=FechaTramite.crear_hoy(),
            funcionario_envia="ENVIADOR"
        )
        
        # Admin puede devolver desde cualquier estado
        traslado.devolver_traslado("ADMIN", "Proceso cancelado por solicitud", es_admin=True)
        
        assert traslado.fue_devuelto()
        assert traslado.esta_en_estado_final()
        assert "cancelado" in traslado.observaciones.valor.lower()
        assert "ADMIN" == traslado.funcionario_actual