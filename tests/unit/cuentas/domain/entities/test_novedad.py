import pytest
from datetime import date, timedelta

from app.cuentas.domain.entities.novedad import Novedad
from app.cuentas.domain.value_objects.placa import Placa
from app.cuentas.domain.value_objects.ids.id_novedad import IdentificadorNovedad
from app.cuentas.domain.value_objects.descripcion_novedad import DescripcionNovedad
from app.cuentas.domain.value_objects.observacion import Observacion
from app.cuentas.domain.value_objects.enums.novedades.tipo_novedad import TipoNovedad
from app.cuentas.domain.value_objects.enums.novedades.estado_novedad import EstadoNovedad
from app.cuentas.domain.value_objects.enums.novedades.prioridad_novedad import PrioridadNovedad


class TestNovedadCreacion:
    """Tests para creación de novedades"""
    
    @pytest.fixture
    def datos_novedad_base(self):
        """Datos base para crear novedad"""
        return {
            'identificador': IdentificadorNovedad.generar_para_hoy(1),
            'placa': Placa("NOV123"),
            'tipo_novedad': TipoNovedad.DOCUMENTO_FALTANTE,
            'descripcion': DescripcionNovedad.crear_desde_texto("El certificado de tradición y libertad no se encuentra en el expediente"),
            'prioridad': PrioridadNovedad.ALTA,
            'funcionario_reporta': "JPEREZ",
            'fecha_reporte': date.today(),
            'tipo_proceso': "traslado"
        }
    
    def test_crear_novedad_valida(self, datos_novedad_base):
        """Test creación de novedad con datos válidos"""
        novedad = Novedad(
            identificador=datos_novedad_base['identificador'],
            placa=datos_novedad_base['placa'],
            tipo_novedad=datos_novedad_base['tipo_novedad'],
            descripcion=datos_novedad_base['descripcion'],
            prioridad=datos_novedad_base['prioridad'],
            funcionario_reporta=datos_novedad_base['funcionario_reporta'],
            fecha_reporte=datos_novedad_base['fecha_reporte'],
            tipo_proceso=datos_novedad_base['tipo_proceso']
        )
        
        assert novedad.identificador == datos_novedad_base['identificador']
        assert novedad.placa == datos_novedad_base['placa']
        assert novedad.tipo_novedad == TipoNovedad.DOCUMENTO_FALTANTE
        assert novedad.prioridad == PrioridadNovedad.ALTA
        assert novedad.funcionario_reporta == "JPEREZ"
        assert novedad.tipo_proceso == "traslado"
        assert novedad.estado == EstadoNovedad.PENDIENTE
        assert novedad.funcionario_actual == "JPEREZ"
        assert novedad.fecha_ultima_actualizacion == date.today()
        assert novedad.observaciones.esta_vacia()
        assert novedad.funcionario_resuelve is None
        assert novedad.fecha_resolucion is None
    
    def test_crear_novedad_factory_method(self):
        """Test factory method para crear novedad"""
        placa = Placa("FAC123")
        descripcion = DescripcionNovedad.crear_desde_texto("La firma del propietario no coincide con la cédula")
        
        novedad = Novedad.crear_nueva(
            placa=placa,
            tipo_novedad=TipoNovedad.FIRMA_FALTANTE,
            descripcion=descripcion,
            prioridad=PrioridadNovedad.CRITICA,
            funcionario_reporta="MLOPEZ",
            tipo_proceso="radicacion",
            consecutivo_novedad=5,
            observaciones_iniciales="Requiere verificación urgente"
        )
        
        assert novedad.get_placa_valor() == "FAC123"
        assert novedad.tipo_novedad == TipoNovedad.FIRMA_FALTANTE
        assert novedad.prioridad == PrioridadNovedad.CRITICA
        assert novedad.tipo_proceso == "radicacion"
        assert novedad.get_codigo_novedad().endswith("0005")
        assert not novedad.observaciones.esta_vacia()
        assert "verificación" in novedad.observaciones.valor.lower()
    
    def test_crear_novedad_funcionario_normalizado(self, datos_novedad_base):
        """Test normalización de funcionario que reporta"""
        datos_novedad_base['funcionario_reporta'] = "  ana.garcia  "
        
        novedad = Novedad(
            identificador=datos_novedad_base['identificador'],
            placa=datos_novedad_base['placa'],
            tipo_novedad=datos_novedad_base['tipo_novedad'],
            descripcion=datos_novedad_base['descripcion'],
            prioridad=datos_novedad_base['prioridad'],
            funcionario_reporta=datos_novedad_base['funcionario_reporta'],
            fecha_reporte=datos_novedad_base['fecha_reporte'],
            tipo_proceso=datos_novedad_base['tipo_proceso']
        )
        
        assert novedad.funcionario_reporta == "ANA.GARCIA"
        assert novedad.funcionario_actual == "ANA.GARCIA"
    
    def test_crear_novedad_tipo_proceso_normalizado(self, datos_novedad_base):
        """Test normalización de tipo de proceso"""
        datos_novedad_base['tipo_proceso'] = "  TRASLADO  "
        
        novedad = Novedad(
            identificador=datos_novedad_base['identificador'],
            placa=datos_novedad_base['placa'],
            tipo_novedad=datos_novedad_base['tipo_novedad'],
            descripcion=datos_novedad_base['descripcion'],
            prioridad=datos_novedad_base['prioridad'],
            funcionario_reporta=datos_novedad_base['funcionario_reporta'],
            fecha_reporte=datos_novedad_base['fecha_reporte'],
            tipo_proceso=datos_novedad_base['tipo_proceso']
        )
        
        assert novedad.tipo_proceso == "traslado"
    
    def test_crear_novedad_funcionario_vacio_error(self, datos_novedad_base):
        """Test error con funcionario vacío"""
        with pytest.raises(ValueError, match="funcionario que reporta no puede estar vacío"):
            Novedad(
                identificador=datos_novedad_base['identificador'],
                placa=datos_novedad_base['placa'],
                tipo_novedad=datos_novedad_base['tipo_novedad'],
                descripcion=datos_novedad_base['descripcion'],
                prioridad=datos_novedad_base['prioridad'],
                funcionario_reporta="",
                fecha_reporte=datos_novedad_base['fecha_reporte'],
                tipo_proceso=datos_novedad_base['tipo_proceso']
            )
    
    def test_crear_novedad_tipo_proceso_invalido_error(self, datos_novedad_base):
        """Test error con tipo de proceso inválido"""
        with pytest.raises(ValueError, match="tipo de proceso debe ser 'traslado' o 'radicacion'"):
            Novedad(
                identificador=datos_novedad_base['identificador'],
                placa=datos_novedad_base['placa'],
                tipo_novedad=datos_novedad_base['tipo_novedad'],
                descripcion=datos_novedad_base['descripcion'],
                prioridad=datos_novedad_base['prioridad'],
                funcionario_reporta=datos_novedad_base['funcionario_reporta'],
                fecha_reporte=datos_novedad_base['fecha_reporte'],
                tipo_proceso="invalido"
            )
    
    def test_crear_novedad_fecha_futura_error(self, datos_novedad_base):
        """Test error con fecha futura"""
        with pytest.raises(ValueError, match="fecha de reporte no puede ser futura"):
            Novedad(
                identificador=datos_novedad_base['identificador'],
                placa=datos_novedad_base['placa'],
                tipo_novedad=datos_novedad_base['tipo_novedad'],
                descripcion=datos_novedad_base['descripcion'],
                prioridad=datos_novedad_base['prioridad'],
                funcionario_reporta=datos_novedad_base['funcionario_reporta'],
                fecha_reporte=date.today() + timedelta(days=1),
                tipo_proceso=datos_novedad_base['tipo_proceso']
            )


class TestNovedadConsultas:
    """Tests para métodos de consulta"""
    
    @pytest.fixture
    def novedad_base(self):
        """Novedad base para tests"""
        return Novedad.crear_nueva(
            placa=Placa("CON456"),
            tipo_novedad=TipoNovedad.INFORMACION_INCONSISTENTE,
            descripcion=DescripcionNovedad.crear_desde_texto("Los datos del propietario no coinciden entre la cédula y el RUNT"),
            prioridad=PrioridadNovedad.MEDIA,
            funcionario_reporta="NLOPEZ",
            tipo_proceso="traslado",
            consecutivo_novedad=10
        )
    
    def test_get_informacion_basica(self, novedad_base):
        """Test obtener información básica"""
        assert novedad_base.get_placa_valor() == "CON456"
        assert novedad_base.get_tipo_novedad_descripcion() == "Informacion Inconsistente"
        assert novedad_base.get_prioridad_descripcion() == "MEDIA"
        assert novedad_base.get_codigo_novedad().endswith("0010")
    
    def test_get_funcionario_responsable(self, novedad_base):
        """Test obtener funcionario responsable"""
        assert novedad_base.get_funcionario_responsable() == "NLOPEZ"
        
        # Cambiar a revisión
        novedad_base.tomar_en_revision("REVISOR")
        assert novedad_base.get_funcionario_responsable() == "REVISOR"
        
        # Resolver
        novedad_base.resolver_novedad("RESOLVEDOR", "Datos corregidos en el sistema")
        assert novedad_base.get_funcionario_responsable() == "RESOLVEDOR"
    
    def test_get_informacion_temporal(self, novedad_base):
        """Test información temporal"""
        assert novedad_base.get_dias_desde_reporte() == 0  # Creada hoy
        assert novedad_base.get_dias_desde_ultima_actualizacion() == 0
        assert novedad_base.get_tiempo_resolucion_dias() is None  # No resuelta
    
    def test_get_tiempo_resolucion_cuando_resuelta(self, novedad_base):
        """Test tiempo de resolución cuando está resuelta"""
        novedad_base.tomar_en_revision("REVISOR")
        novedad_base.resolver_novedad("RESOLVEDOR", "Problema solucionado")
        
        assert novedad_base.get_tiempo_resolucion_dias() == 0  # Resuelta el mismo día


class TestNovedadValidacionesEstado:
    """Tests para validaciones de estado"""
    
    @pytest.fixture
    def novedad_pendiente(self):
        """Novedad en estado pendiente"""
        return Novedad.crear_nueva(
            placa=Placa("PEN123"),
            tipo_novedad=TipoNovedad.SOAT_VENCIDO,
            descripcion=DescripcionNovedad.crear_desde_texto("La póliza SOAT está vencida desde hace 15 días"),
            prioridad=PrioridadNovedad.ALTA,
            funcionario_reporta="JPEREZ",
            tipo_proceso="radicacion",
            consecutivo_novedad=1
        )
    
    def test_estado_inicial_validaciones(self, novedad_pendiente):
        """Test validaciones en estado inicial (pendiente)"""
        assert novedad_pendiente.esta_pendiente()
        assert not novedad_pendiente.esta_en_revision()
        assert not novedad_pendiente.esta_resuelta()
        assert not novedad_pendiente.esta_reabierta()
        assert not novedad_pendiente.esta_en_estado_final()
        assert novedad_pendiente.requiere_atencion_inmediata()  # Prioridad ALTA
        assert not novedad_pendiente.es_novedad_critica()
        assert not novedad_pendiente.es_novedad_antigua()
    
    def test_novedad_critica_validaciones(self):
        """Test validaciones para novedad crítica"""
        novedad_critica = Novedad.crear_nueva(
            placa=Placa("CRI123"),
            tipo_novedad=TipoNovedad.DATOS_PROPIETARIO_INCOMPLETOS,
            descripcion=DescripcionNovedad.crear_desde_texto("Faltan datos completos del propietario del vehículo"),
            prioridad=PrioridadNovedad.CRITICA,
            funcionario_reporta="JPEREZ",
            tipo_proceso="traslado",
            consecutivo_novedad=2
        )
        
        assert novedad_critica.es_novedad_critica()
        assert novedad_critica.requiere_atencion_inmediata()
    
    def test_novedad_antigua_validaciones(self):
        """Test validaciones para novedad antigua"""
        # Simular novedad antigua (más de 30 días)
        fecha_antigua = date.today() - timedelta(days=35)
        identificador_antiguo = IdentificadorNovedad.generar_para_fecha(fecha_antigua, 1)
        
        novedad_antigua = Novedad(
            identificador=identificador_antiguo,
            placa=Placa("ANT123"),
            tipo_novedad=TipoNovedad.OTRO,
            descripcion=DescripcionNovedad.crear_desde_texto("Novedad antigua sin resolver"),
            prioridad=PrioridadNovedad.BAJA,
            funcionario_reporta="JPEREZ",
            fecha_reporte=fecha_antigua,
            tipo_proceso="traslado"
        )
        
        assert novedad_antigua.es_novedad_antigua()
        assert novedad_antigua.get_dias_desde_reporte() == 35


class TestNovedadReglasTansiciones:
    """Tests para reglas de transiciones de estado"""
    
    @pytest.fixture
    def novedad_pendiente(self):
        """Novedad pendiente para tests de transición"""
        return Novedad.crear_nueva(
            placa=Placa("TRA123"),
            tipo_novedad=TipoNovedad.FECHA_INCORRECTA,
            descripcion=DescripcionNovedad.crear_desde_texto("La fecha en el certificado no corresponde"),
            prioridad=PrioridadNovedad.MEDIA,
            funcionario_reporta="JPEREZ",
            tipo_proceso="traslado",
            consecutivo_novedad=3
        )
    
    def test_puede_pasar_a_revision_desde_pendiente(self, novedad_pendiente):
        """Test puede pasar a revisión desde pendiente"""
        assert novedad_pendiente.puede_pasar_a_revision()
        assert novedad_pendiente.puede_ser_resuelta()  # También puede ir directo a resuelta
        assert not novedad_pendiente.puede_ser_reabierta()
        assert novedad_pendiente.puede_cambiar_prioridad()
    
    @pytest.fixture
    def novedad_en_revision(self, novedad_pendiente):
        """Novedad en revisión para tests"""
        novedad_pendiente.tomar_en_revision("REVISOR")
        return novedad_pendiente
    
    def test_puede_ser_resuelta_desde_revision(self, novedad_en_revision):
        """Test puede ser resuelta desde revisión"""
        assert not novedad_en_revision.puede_pasar_a_revision()  # Ya está en revisión
        assert novedad_en_revision.puede_ser_resuelta()
        assert not novedad_en_revision.puede_ser_reabierta()
        assert novedad_en_revision.puede_cambiar_prioridad()
    
    @pytest.fixture
    def novedad_resuelta(self, novedad_en_revision):
        """Novedad resuelta para tests"""
        novedad_en_revision.resolver_novedad("RESOLVEDOR", "Fecha corregida en el sistema")
        return novedad_en_revision
    
    def test_puede_ser_reabierta_desde_resuelta(self, novedad_resuelta):
        """Test puede ser reabierta desde resuelta"""
        assert not novedad_resuelta.puede_pasar_a_revision()
        assert not novedad_resuelta.puede_ser_resuelta()
        assert novedad_resuelta.puede_ser_reabierta()
        assert not novedad_resuelta.puede_cambiar_prioridad()  # No puede cambiar si está resuelta


class TestNovedadTransicionesEstado:
    """Tests para transiciones de estado"""
    
    @pytest.fixture
    def novedad_para_transiciones(self):
        """Novedad para tests de transiciones"""
        return Novedad.crear_nueva(
            placa=Placa("TRN123"),
            tipo_novedad=TipoNovedad.TECNICOMECANICA_VENCIDA,
            descripcion=DescripcionNovedad.crear_desde_texto("La revisión técnico mecánica está vencida"),
            prioridad=PrioridadNovedad.ALTA,
            funcionario_reporta="JPEREZ",
            tipo_proceso="radicacion",
            consecutivo_novedad=4,
            observaciones_iniciales="Novedad detectada en revisión inicial"
        )
    
    def test_tomar_en_revision_exitoso(self, novedad_para_transiciones):
        """Test tomar en revisión exitosamente"""
        novedad_para_transiciones.tomar_en_revision("REVISOR001")
        
        assert novedad_para_transiciones.estado == EstadoNovedad.EN_REVISION
        assert novedad_para_transiciones.esta_en_revision()
        assert novedad_para_transiciones.funcionario_actual == "REVISOR001"
        assert novedad_para_transiciones.fecha_ultima_actualizacion == date.today()
        
        # Verificar observación de toma en revisión se agregó
        obs = novedad_para_transiciones.observaciones.valor
        assert "tomada en revisión" in obs.lower()
        assert "REVISOR001" in obs
        
        # Las observaciones iniciales se mantienen
        assert "inicial" in obs.lower()
    
    def test_resolver_novedad_exitoso(self, novedad_para_transiciones):
        """Test resolver novedad exitosamente"""
        novedad_para_transiciones.tomar_en_revision("REVISOR001")
        novedad_para_transiciones.resolver_novedad("RESOLVEDOR", "Técnico mecánica actualizada en el sistema")
        
        assert novedad_para_transiciones.estado == EstadoNovedad.RESUELTA
        assert novedad_para_transiciones.esta_resuelta()
        assert novedad_para_transiciones.esta_en_estado_final()
        assert novedad_para_transiciones.funcionario_resuelve == "RESOLVEDOR"
        assert novedad_para_transiciones.funcionario_actual == "RESOLVEDOR"
        assert novedad_para_transiciones.fecha_resolucion == date.today()
        assert novedad_para_transiciones.descripcion_resolucion == "Técnico mecánica actualizada en el sistema"
        
        # Verificar observaciones incluyen resolución
        assert "NOVEDAD RESUELTA" in novedad_para_transiciones.observaciones.valor
        assert "actualizada" in novedad_para_transiciones.observaciones.valor
        
        # Verificar tiempo de resolución
        assert novedad_para_transiciones.get_tiempo_resolucion_dias() == 0
    
    def test_resolver_novedad_directo_desde_pendiente(self, novedad_para_transiciones):
        """Test resolver novedad directamente desde pendiente"""
        novedad_para_transiciones.resolver_novedad("RESOLVEDOR_DIRECTO", "Solucionado directamente")
        
        assert novedad_para_transiciones.esta_resuelta()
        assert novedad_para_transiciones.funcionario_resuelve == "RESOLVEDOR_DIRECTO"
        assert "Solucionado directamente" == novedad_para_transiciones.descripcion_resolucion
    
    def test_reabrir_novedad_exitoso(self, novedad_para_transiciones):
        """Test reabrir novedad exitosamente"""
        novedad_para_transiciones.resolver_novedad("RESOLVEDOR", "Resuelto inicialmente")
        novedad_para_transiciones.reabrir_novedad("REABRIDOR", "La solución no fue efectiva")
        
        assert novedad_para_transiciones.estado == EstadoNovedad.REABIERTA
        assert novedad_para_transiciones.esta_reabierta()
        assert not novedad_para_transiciones.esta_en_estado_final()
        assert novedad_para_transiciones.funcionario_actual == "REABRIDOR"
        
        # Verificar que los datos de resolución se limpiaron
        assert novedad_para_transiciones.funcionario_resuelve is None
        assert novedad_para_transiciones.fecha_resolucion is None
        assert novedad_para_transiciones.descripcion_resolucion is None
        
        # Verificar observación de reapertura
        assert "NOVEDAD REABIERTA" in novedad_para_transiciones.observaciones.valor
        assert "no fue efectiva" in novedad_para_transiciones.observaciones.valor
    
    def test_cambiar_prioridad_exitoso(self, novedad_para_transiciones):
        """Test cambiar prioridad exitosamente"""
        prioridad_original = novedad_para_transiciones.prioridad
        
        novedad_para_transiciones.cambiar_prioridad(
            "SUPERVISOR", 
            PrioridadNovedad.CRITICA, 
            "Escalamiento por impacto en otros procesos"
        )
        
        assert novedad_para_transiciones.prioridad == PrioridadNovedad.CRITICA
        assert novedad_para_transiciones.funcionario_actual == "SUPERVISOR"
        assert novedad_para_transiciones.es_novedad_critica()
        
        # Verificar observación del cambio
        obs = novedad_para_transiciones.observaciones.valor
        assert "PRIORIDAD CAMBIADA" in obs
        assert "ALTA" in obs  # Prioridad anterior
        assert "CRITICA" in obs  # Nueva prioridad
        assert "impacto" in obs.lower()
    
    def test_actualizar_observaciones_exitoso(self, novedad_para_transiciones):
        """Test actualizar observaciones exitosamente"""
        observaciones_anteriores = novedad_para_transiciones.observaciones.valor
        
        novedad_para_transiciones.actualizar_observaciones("ACTUALIZADOR", "Información adicional importante")
        
        assert "Información adicional importante" in novedad_para_transiciones.observaciones.valor
        assert "ACTUALIZADOR" in novedad_para_transiciones.observaciones.valor
        assert novedad_para_transiciones.fecha_ultima_actualizacion == date.today()
        
        # Las observaciones anteriores se mantienen
        assert "inicial" in novedad_para_transiciones.observaciones.valor.lower()


class TestNovedadTransicionesError:
    """Tests para errores en transiciones"""
    
    @pytest.fixture
    def novedad_resuelta(self):
        """Novedad resuelta para tests de error"""
        novedad = Novedad.crear_nueva(
            placa=Placa("ERR123"),
            tipo_novedad=TipoNovedad.DOCUMENTO_INCORRECTO,
            descripcion=DescripcionNovedad.crear_desde_texto("Documento presenta inconsistencias"),
            prioridad=PrioridadNovedad.MEDIA,
            funcionario_reporta="JPEREZ",
            tipo_proceso="traslado",
            consecutivo_novedad=5
        )
        novedad.resolver_novedad("RESOLVEDOR", "Problema solucionado")
        return novedad
    
    def test_tomar_revision_desde_estado_incorrecto(self, novedad_resuelta):
        """Test error al tomar en revisión desde estado incorrecto"""
        with pytest.raises(ValueError, match="No se puede pasar a revisión desde estado"):
            novedad_resuelta.tomar_en_revision("REVISOR")
    
    def test_resolver_novedad_descripcion_vacia_error(self):
        """Test error al resolver con descripción vacía"""
        novedad = Novedad.crear_nueva(
            placa=Placa("ERR456"),
            tipo_novedad=TipoNovedad.OTRO,
            descripcion=DescripcionNovedad.crear_desde_texto("Alguna novedad"),
            prioridad=PrioridadNovedad.BAJA,
            funcionario_reporta="JPEREZ",
            tipo_proceso="radicacion",
            consecutivo_novedad=6
        )
        
        with pytest.raises(ValueError, match="descripción de resolución no puede estar vacía"):
            novedad.resolver_novedad("RESOLVEDOR", "")
    
    def test_reabrir_novedad_sin_estar_resuelta_error(self):
        """Test error al reabrir novedad que no está resuelta"""
        novedad = Novedad.crear_nueva(
            placa=Placa("ERR789"),
            tipo_novedad=TipoNovedad.FIRMA_FALTANTE,
            descripcion=DescripcionNovedad.crear_desde_texto("Falta firma del propietario"),
            prioridad=PrioridadNovedad.ALTA,
            funcionario_reporta="JPEREZ",
            tipo_proceso="traslado",
            consecutivo_novedad=7
        )
        
        with pytest.raises(ValueError, match="No se puede reabrir desde estado"):
            novedad.reabrir_novedad("REABRIDOR", "Motivo de reapertura")
    
    def test_cambiar_prioridad_misma_prioridad_error(self):
        """Test error al cambiar a la misma prioridad"""
        novedad = Novedad.crear_nueva(
            placa=Placa("ERR101"),
            tipo_novedad=TipoNovedad.SOAT_VENCIDO,
            descripcion=DescripcionNovedad.crear_desde_texto("SOAT vencido"),
            prioridad=PrioridadNovedad.MEDIA,
            funcionario_reporta="JPEREZ",
            tipo_proceso="radicacion",
            consecutivo_novedad=8
        )
        
        with pytest.raises(ValueError, match="nueva prioridad debe ser diferente"):
            novedad.cambiar_prioridad("SUPERVISOR", PrioridadNovedad.MEDIA, "Sin cambio real")
    
    def test_cambiar_prioridad_novedad_resuelta_error(self, novedad_resuelta):
        """Test error al cambiar prioridad de novedad resuelta"""
        with pytest.raises(ValueError, match="No se puede cambiar la prioridad de una novedad resuelta"):
            novedad_resuelta.cambiar_prioridad("SUPERVISOR", PrioridadNovedad.CRITICA, "Intento cambio")
    
    def test_actualizar_observaciones_novedad_resuelta_error(self, novedad_resuelta):
        """Test error al actualizar observaciones en novedad resuelta"""
        with pytest.raises(ValueError, match="No se pueden actualizar observaciones de una novedad resuelta"):
            novedad_resuelta.actualizar_observaciones("ACTUALIZADOR", "Intento actualizar")


class TestNovedadAnalisis:
    """Tests para métodos de análisis"""
    
    def test_es_similar_a_otra_novedad(self):
        """Test verificar si es similar a otra novedad"""
        placa_comun = Placa("SIM123")
        tipo_comun = TipoNovedad.DOCUMENTO_FALTANTE
        descripcion1 = DescripcionNovedad.crear_desde_texto("Falta el certificado de tradición y libertad del vehículo")
        descripcion2 = DescripcionNovedad.crear_desde_texto("No se encuentra certificado de tradición y libertad")
        
        novedad1 = Novedad.crear_nueva(
            placa=placa_comun,
            tipo_novedad=tipo_comun,
            descripcion=descripcion1,
            prioridad=PrioridadNovedad.ALTA,
            funcionario_reporta="JPEREZ",
            tipo_proceso="traslado",
            consecutivo_novedad=1
        )
        
        novedad2 = Novedad.crear_nueva(
            placa=placa_comun,
            tipo_novedad=tipo_comun,
            descripcion=descripcion2,
            prioridad=PrioridadNovedad.MEDIA,
            funcionario_reporta="MLOPEZ",
            tipo_proceso="radicacion",
            consecutivo_novedad=2
        )
        
        # Deberían ser similares (misma placa, tipo y descripción similar)
        assert novedad1.es_similar_a(novedad2)
    
    def test_get_resumen_ejecutivo(self):
        """Test generar resumen ejecutivo"""
        novedad = Novedad.crear_nueva(
            placa=Placa("RES123"),
            tipo_novedad=TipoNovedad.INFORMACION_INCONSISTENTE,
            descripcion=DescripcionNovedad.crear_desde_texto("Datos inconsistentes entre documentos"),
            prioridad=PrioridadNovedad.CRITICA,
            funcionario_reporta="JPEREZ",
            tipo_proceso="traslado",
            consecutivo_novedad=9
        )
        
        resumen = novedad.get_resumen_ejecutivo()
        
        assert novedad.get_codigo_novedad() in resumen
        assert "RES123" in resumen
        assert "Informacion Inconsistente" in resumen
        assert "CRITICA" in resumen
        assert "0 días" in resumen  # Creada hoy
        
        # Resolver y verificar cambio en resumen
        novedad.resolver_novedad("RESOLVEDOR", "Datos corregidos")
        resumen_resuelto = novedad.get_resumen_ejecutivo()
        assert "Resuelta en 0 días" in resumen_resuelto


class TestNovedadFactoryMethods:
    """Tests para factory methods"""
    
    def test_crear_desde_repositorio_exitoso(self):
        """Test recrear novedad desde repositorio"""
        identificador = IdentificadorNovedad.generar_para_hoy(10)
        placa = Placa("REP123")
        descripcion = DescripcionNovedad.crear_desde_texto("Descripción desde repositorio")
        observaciones = Observacion.crear_desde_texto("Observación desde repo")
        fecha_pasada = date.today() - timedelta(days=2)
        
        novedad = Novedad.crear_desde_repositorio(
            identificador=identificador,
            placa=placa,
            tipo_novedad=TipoNovedad.OTRO,
            descripcion=descripcion,
            prioridad=PrioridadNovedad.BAJA,
            funcionario_reporta="ORIGINAL",
            fecha_reporte=fecha_pasada,
            tipo_proceso="traslado",
            estado=EstadoNovedad.RESUELTA,
            observaciones=observaciones,
            funcionario_resuelve="RESOLVEDOR",
            fecha_resolucion=date.today(),
            descripcion_resolucion="Problema solucionado desde repo",
            funcionario_actual="ACTUAL",
            fecha_ultima_actualizacion=date.today()
        )
        
        assert novedad.identificador == identificador
        assert novedad.placa == placa
        assert novedad.estado == EstadoNovedad.RESUELTA
        assert novedad.funcionario_reporta == "ORIGINAL"
        assert novedad.funcionario_resuelve == "RESOLVEDOR"
        assert novedad.funcionario_actual == "ACTUAL"
        assert novedad.fecha_reporte == fecha_pasada
        assert novedad.descripcion_resolucion == "Problema solucionado desde repo"
        assert novedad.observaciones == observaciones
        assert novedad.get_dias_desde_reporte() == 2


class TestNovedadRepresentacion:
    """Tests para métodos de representación"""
    
    def test_str_y_repr(self):
        """Test métodos __str__ y __repr__"""
        novedad = Novedad.crear_nueva(
            placa=Placa("STR123"),
            tipo_novedad=TipoNovedad.FECHA_INCORRECTA,
            descripcion=DescripcionNovedad.crear_desde_texto("Fecha incorrecta en el documento"),
            prioridad=PrioridadNovedad.ALTA,
            funcionario_reporta="JPEREZ",
            tipo_proceso="radicacion",
            consecutivo_novedad=15
        )
        
        str_resultado = str(novedad)
        assert novedad.get_codigo_novedad() in str_resultado
        assert "STR123" in str_resultado
        
        repr_resultado = repr(novedad)
        assert "Novedad" in repr_resultado
        assert f"codigo='{novedad.get_codigo_novedad()}'" in repr_resultado
        assert "placa='STR123'" in repr_resultado
        assert "tipo='fecha_incorrecta'" in repr_resultado
        assert "estado='pendiente'" in repr_resultado


class TestNovedadIntegracion:
    """Tests de integración completos"""
    
    def test_flujo_completo_exitoso(self):
        """Test flujo completo de novedad exitosa"""
        # 1. Crear novedad
        novedad = Novedad.crear_nueva(
            placa=Placa("FLU123"),
            tipo_novedad=TipoNovedad.DOCUMENTO_FALTANTE,
            descripcion=DescripcionNovedad.crear_desde_texto("Falta certificado SOAT vigente en el expediente del vehículo"),
            prioridad=PrioridadNovedad.ALTA,
            funcionario_reporta="REPORTADOR",
            tipo_proceso="traslado",
            consecutivo_novedad=20,
            observaciones_iniciales="Detectado en revisión de documentos"
        )
        
        assert novedad.esta_pendiente()
        assert novedad.requiere_atencion_inmediata()
        
        # 2. Tomar en revisión
        novedad.tomar_en_revision("REVISOR")
        assert novedad.esta_en_revision()
        assert novedad.funcionario_actual == "REVISOR"
        
        # 3. Cambiar prioridad por escalamiento
        novedad.cambiar_prioridad("SUPERVISOR", PrioridadNovedad.CRITICA, "Escalado por impacto en proceso")
        assert novedad.es_novedad_critica()
        
        # 4. Actualizar observaciones con más información
        novedad.actualizar_observaciones("REVISOR", "Contactado con propietario para obtener SOAT")
        
        # 5. Resolver novedad
        novedad.resolver_novedad("RESOLVEDOR", "SOAT vigente adjuntado correctamente al expediente")
        
        assert novedad.esta_resuelta()
        assert novedad.esta_en_estado_final()
        assert novedad.funcionario_resuelve == "RESOLVEDOR"
        
        # Verificar trazabilidad completa en observaciones
        obs = novedad.observaciones.valor
        assert "revisión de documentos" in obs.lower()
        assert "tomada en revisión" in obs.lower()
        assert "PRIORIDAD CAMBIADA" in obs
        assert "ALTA" in obs and "CRITICA" in obs
        assert "Contactado con propietario" in obs
        assert "NOVEDAD RESUELTA" in obs
        assert "adjuntado correctamente" in obs
        
        # Verificar funcionarios involucrados
        assert "REPORTADOR" == novedad.funcionario_reporta
        assert "RESOLVEDOR" == novedad.funcionario_resuelve
        assert "RESOLVEDOR" == novedad.funcionario_actual
    
    def test_flujo_con_reapertura(self):
        """Test flujo con reapertura de novedad"""
        novedad = Novedad.crear_nueva(
            placa=Placa("REA123"),
            tipo_novedad=TipoNovedad.TECNICOMECANICA_VENCIDA,
            descripcion=DescripcionNovedad.crear_desde_texto("Revisión técnico mecánica vencida hace 45 días"),
            prioridad=PrioridadNovedad.MEDIA,
            funcionario_reporta="REPORTADOR",
            tipo_proceso="radicacion",
            consecutivo_novedad=25
        )
        
        # 1. Resolver directamente
        novedad.resolver_novedad("RESOLVEDOR_INICIAL", "Técnico mecánica actualizada en el sistema")
        assert novedad.esta_resuelta()
        tiempo_inicial = novedad.get_tiempo_resolucion_dias()
        
        # 2. Reabrir por problema en la solución
        novedad.reabrir_novedad("SUPERVISOR", "La técnico mecánica sigue apareciendo vencida en RUNT")
        
        assert novedad.esta_reabierta()
        assert not novedad.esta_en_estado_final()
        assert novedad.funcionario_actual == "SUPERVISOR"
        
        # Verificar que datos de resolución se limpiaron
        assert novedad.funcionario_resuelve is None
        assert novedad.fecha_resolucion is None
        assert novedad.descripcion_resolucion is None
        assert novedad.get_tiempo_resolucion_dias() is None
        
        # 3. Tomar en revisión nuevamente
        novedad.tomar_en_revision("NUEVO_REVISOR")
        assert novedad.esta_en_revision()
        
        # 4. Resolver definitivamente
        novedad.resolver_novedad("RESOLVEDOR_FINAL", "Actualizado directamente en RUNT con soporte técnico")
        
        assert novedad.esta_resuelta()
        assert novedad.funcionario_resuelve == "RESOLVEDOR_FINAL"
        
        # Verificar el historial completo en observaciones
        obs = novedad.observaciones.valor
        assert "actualizada en el sistema" in obs.lower()  # Primera resolución
        assert "NOVEDAD REABIERTA" in obs
        assert "sigue apareciendo vencida" in obs.lower()  # Motivo reapertura
        assert "tomada en revisión" in obs.lower()  # Segunda toma
        assert "directamente en RUNT" in obs  # Resolución final
    
    def test_flujo_escalamiento_prioridad(self):
        """Test flujo de escalamiento de prioridad"""
        novedad = Novedad.crear_nueva(
            placa=Placa("ESC123"),
            tipo_novedad=TipoNovedad.INFORMACION_INCONSISTENTE,
            descripcion=DescripcionNovedad.crear_desde_texto("Datos del propietario no coinciden entre cédula y RUNT"),
            prioridad=PrioridadNovedad.BAJA,
            funcionario_reporta="FUNCIONARIO",
            tipo_proceso="traslado",
            consecutivo_novedad=30
        )
        
        assert not novedad.requiere_atencion_inmediata()  # Prioridad baja inicialmente
        
        # 1. Escalamiento por supervisor
        novedad.cambiar_prioridad("SUPERVISOR1", PrioridadNovedad.MEDIA, "Escalado por tiempo de espera")
        
        # 2. Nuevo escalamiento por impacto
        novedad.cambiar_prioridad("SUPERVISOR2", PrioridadNovedad.ALTA, "Afecta múltiples procesos")
        assert novedad.requiere_atencion_inmediata()
        
        # 3. Escalamiento crítico
        novedad.cambiar_prioridad("GERENTE", PrioridadNovedad.CRITICA, "Bloquea proceso urgente de cliente VIP")
        assert novedad.es_novedad_critica()
        
        # 4. Resolver inmediatamente por ser crítica
        novedad.resolver_novedad("ESPECIALISTA", "Datos corregidos manualmente con validación especial")
        
        # Verificar todo el escalamiento en observaciones
        obs = novedad.observaciones.valor
        assert "BAJA a MEDIA" in obs
        assert "tiempo de espera" in obs
        assert "MEDIA a ALTA" in obs  
        assert "múltiples procesos" in obs
        assert "ALTA a CRITICA" in obs
        assert "cliente VIP" in obs
        assert "validación especial" in obs
    
    def test_novedad_multiple_misma_placa(self):
        """Test múltiples novedades para la misma placa"""
        placa_comun = Placa("MUL123")
        
        # Novedad 1: Documento faltante
        novedad1 = Novedad.crear_nueva(
            placa=placa_comun,
            tipo_novedad=TipoNovedad.DOCUMENTO_FALTANTE,
            descripcion=DescripcionNovedad.crear_desde_texto("Falta certificado de tradición y libertad"),
            prioridad=PrioridadNovedad.ALTA,
            funcionario_reporta="FUNC1",
            tipo_proceso="traslado",
            consecutivo_novedad=31
        )
        
        # Novedad 2: SOAT vencido (misma placa, diferente tipo)
        novedad2 = Novedad.crear_nueva(
            placa=placa_comun,
            tipo_novedad=TipoNovedad.SOAT_VENCIDO,
            descripcion=DescripcionNovedad.crear_desde_texto("Póliza SOAT vencida hace 20 días"),
            prioridad=PrioridadNovedad.CRITICA,
            funcionario_reporta="FUNC2",
            tipo_proceso="traslado",
            consecutivo_novedad=32
        )
        
        # Ambas novedades son válidas e independientes
        assert novedad1.get_placa_valor() == novedad2.get_placa_valor()
        assert novedad1.tipo_novedad != novedad2.tipo_novedad
        assert novedad1.get_codigo_novedad() != novedad2.get_codigo_novedad()
        
        # No son similares (diferente tipo)
        assert not novedad1.es_similar_a(novedad2)
        
        # Resolver independientemente
        novedad1.resolver_novedad("RES1", "Certificado adjuntado")
        novedad2.resolver_novedad("RES2", "SOAT renovado")
        
        assert novedad1.esta_resuelta()
        assert novedad2.esta_resuelta()
        assert novedad1.funcionario_resuelve != novedad2.funcionario_resuelve


class TestNovedadPerformance:
    """Tests de rendimiento y edge cases"""
    
    def test_crear_muchas_novedades_mismo_dia(self):
        """Test crear múltiples novedades el mismo día"""
        placa_base = Placa("PER123")
        novedades = []
        
        # Crear 10 novedades con consecutivos diferentes
        for i in range(1, 11):
            novedad = Novedad.crear_nueva(
                placa=placa_base,
                tipo_novedad=TipoNovedad.OTRO,
                descripcion=DescripcionNovedad.crear_desde_texto(f"Novedad número {i} de prueba de rendimiento"),
                prioridad=PrioridadNovedad.BAJA,
                funcionario_reporta="JPEREZ",
                tipo_proceso="traslado",
                consecutivo_novedad=i
            )
            novedades.append(novedad)
        
        # Verificar que todas tienen códigos únicos
        codigos = [n.get_codigo_novedad() for n in novedades]
        assert len(set(codigos)) == 10  # Todos únicos
        
        # Verificar consecutivos correctos
        for i, novedad in enumerate(novedades, 1):
            assert novedad.get_codigo_novedad().endswith(f"{i:04d}")
    
    def test_transiciones_multiples_rapidas(self):
        """Test múltiples transiciones rápidas"""
        novedad = Novedad.crear_nueva(
            placa=Placa("RAP123"),
            tipo_novedad=TipoNovedad.DOCUMENTO_INCORRECTO,
            descripcion=DescripcionNovedad.crear_desde_texto("Documento presenta errores de digitación"),
            prioridad=PrioridadNovedad.MEDIA,
            funcionario_reporta="INICIAL",
            tipo_proceso="radicacion",
            consecutivo_novedad=100
        )
        
        # Múltiples cambios rápidos
        novedad.tomar_en_revision("REV1")
        novedad.cambiar_prioridad("SUP1", PrioridadNovedad.ALTA, "Escalado")
        novedad.actualizar_observaciones("REV1", "Información adicional")
        novedad.resolver_novedad("RES1", "Corregido")
        novedad.reabrir_novedad("SUP2", "Error persiste")
        novedad.cambiar_prioridad("SUP2", PrioridadNovedad.CRITICA, "Crítico ahora")
        novedad.tomar_en_revision("REV2")
        novedad.resolver_novedad("RES2", "Definitivamente solucionado")
        
        assert novedad.esta_resuelta()
        assert novedad.funcionario_resuelve == "RES2"
        assert novedad.prioridad == PrioridadNovedad.CRITICA
        
        # Verificar que todas las operaciones están en observaciones
        obs = novedad.observaciones.valor
        assert "tomada en revisión" in obs.lower()
        assert "MEDIA a ALTA" in obs
        assert "ALTA a CRITICA" in obs  
        assert "NOVEDAD REABIERTA" in obs
        assert "Error persiste" in obs
        assert "Definitivamente solucionado" in obs