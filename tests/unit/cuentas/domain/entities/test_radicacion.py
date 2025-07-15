import pytest
from datetime import date, timedelta

from app.cuentas.domain.entities.radicacion import Radicacion
from app.cuentas.domain.value_objects.placa import Placa
from app.cuentas.domain.value_objects.fecha_tramite import FechaTramite
from app.cuentas.domain.value_objects.fecha_vencimiento import FechaVencimiento
from app.cuentas.domain.value_objects.ubicacion import Ubicacion, UbicacionesPredefinidas
from app.cuentas.domain.value_objects.observacion import Observacion
from app.cuentas.domain.value_objects.enums.estado_radicacion import EstadoRadicacion


class TestRadicacionCreacion:
    """Tests para creación de radicaciones"""
    
    @pytest.fixture
    def datos_radicacion_base(self):
        """Datos base para crear radicación"""
        return {
            'placa': Placa("RAD123"),
            'organismo_origen': UbicacionesPredefinidas.SOGAMOSO,
            'fecha_tramite': FechaTramite.crear_hoy(),
            'funcionario_recibe': "MGARCIA"
        }
    
    def test_crear_radicacion_valida(self, datos_radicacion_base):
        """Test creación de radicación con datos válidos"""
        fecha_vencimiento = FechaVencimiento.calcular_desde_tramite(datos_radicacion_base['fecha_tramite'])
        
        radicacion = Radicacion(
            placa=datos_radicacion_base['placa'],
            organismo_origen=datos_radicacion_base['organismo_origen'],
            fecha_tramite=datos_radicacion_base['fecha_tramite'],
            fecha_vencimiento=fecha_vencimiento,
            funcionario_recibe=datos_radicacion_base['funcionario_recibe']
        )
        
        assert radicacion.placa == datos_radicacion_base['placa']
        assert radicacion.organismo_origen == datos_radicacion_base['organismo_origen']
        assert radicacion.funcionario_recibe == "MGARCIA"
        assert radicacion.estado == EstadoRadicacion.PENDIENTE_RADICAR
        assert radicacion.funcionario_actual == "MGARCIA"
        assert radicacion.fecha_ultima_actualizacion == date.today()
        assert radicacion.observaciones.esta_vacia()
    
    def test_crear_radicacion_factory_method(self, datos_radicacion_base):
        """Test factory method para crear radicación"""
        radicacion = Radicacion.crear_nueva(
            placa=datos_radicacion_base['placa'],
            organismo_origen=datos_radicacion_base['organismo_origen'],
            fecha_tramite=datos_radicacion_base['fecha_tramite'],
            funcionario_recibe=datos_radicacion_base['funcionario_recibe'],
            observaciones_iniciales="Recepción urgente por vencimiento"
        )
        
        assert radicacion.get_placa_valor() == "RAD123"
        assert radicacion.get_codigo_organismo_origen() == "SOGAMOSO"
        assert not radicacion.observaciones.esta_vacia()
        assert "urgente" in radicacion.observaciones.valor.lower()
        
        # Verificar cálculo automático de vencimiento (60 días)
        dias_diferencia = (radicacion.fecha_vencimiento.fecha - radicacion.fecha_tramite.fecha).days
        assert dias_diferencia == 60
    
    def test_crear_radicacion_funcionario_normalizado(self, datos_radicacion_base):
        """Test normalización de funcionario que recibe"""
        datos_radicacion_base['funcionario_recibe'] = "  carlos.lopez  "
        fecha_vencimiento = FechaVencimiento.calcular_desde_tramite(datos_radicacion_base['fecha_tramite'])
        
        radicacion = Radicacion(
            placa=datos_radicacion_base['placa'],
            organismo_origen=datos_radicacion_base['organismo_origen'],
            fecha_tramite=datos_radicacion_base['fecha_tramite'],
            fecha_vencimiento=fecha_vencimiento,
            funcionario_recibe=datos_radicacion_base['funcionario_recibe']
        )
        
        assert radicacion.funcionario_recibe == "CARLOS.LOPEZ"
    
    def test_crear_radicacion_funcionario_vacio_error(self, datos_radicacion_base):
        """Test error con funcionario vacío"""
        fecha_vencimiento = FechaVencimiento.calcular_desde_tramite(datos_radicacion_base['fecha_tramite'])
        
        with pytest.raises(ValueError, match="funcionario que recibe no puede estar vacío"):
            Radicacion(
                placa=datos_radicacion_base['placa'],
                organismo_origen=datos_radicacion_base['organismo_origen'],
                fecha_tramite=datos_radicacion_base['fecha_tramite'],
                fecha_vencimiento=fecha_vencimiento,
                funcionario_recibe=""
            )
    
    def test_crear_radicacion_fechas_incoherentes_error(self, datos_radicacion_base):
        """Test error con fechas incoherentes"""
        # Fecha de vencimiento anterior a fecha de trámite
        fecha_vencimiento = FechaVencimiento.crear_para_fecha(
            datos_radicacion_base['fecha_tramite'].fecha - timedelta(days=1)
        )
        
        with pytest.raises(ValueError, match="fecha de vencimiento debe ser posterior"):
            Radicacion(
                placa=datos_radicacion_base['placa'],
                organismo_origen=datos_radicacion_base['organismo_origen'],
                fecha_tramite=datos_radicacion_base['fecha_tramite'],
                fecha_vencimiento=fecha_vencimiento,
                funcionario_recibe=datos_radicacion_base['funcionario_recibe']
            )
    
    def test_crear_radicacion_value_objects_invalidos(self, datos_radicacion_base):
        """Test error con value objects de tipo incorrecto"""
        with pytest.raises(ValueError, match="organismo origen debe ser una instancia válida"):
            Radicacion(
                placa=datos_radicacion_base['placa'],
                organismo_origen="SOGAMOSO",  # String en lugar de Ubicacion
                fecha_tramite=datos_radicacion_base['fecha_tramite'],
                fecha_vencimiento=FechaVencimiento.calcular_desde_tramite(datos_radicacion_base['fecha_tramite']),
                funcionario_recibe=datos_radicacion_base['funcionario_recibe']
            )


class TestRadicacionConsultas:
    """Tests para métodos de consulta"""
    
    @pytest.fixture
    def radicacion_base(self):
        """Radicación base para tests"""
        return Radicacion.crear_nueva(
            placa=Placa("CON456"),
            organismo_origen=UbicacionesPredefinidas.MANIZALES,
            fecha_tramite=FechaTramite.crear_hoy(),
            funcionario_recibe="NLOPEZ"
        )
    
    def test_get_informacion_basica(self, radicacion_base):
        """Test obtener información básica"""
        assert radicacion_base.get_placa_valor() == "CON456"
        assert radicacion_base.get_codigo_organismo_origen() == "MANIZALES"
        assert radicacion_base.get_nombre_organismo_origen() == "Manizales"
        assert "Manizales" in radicacion_base.get_ubicacion_completa_origen()
        assert "Caldas" in radicacion_base.get_ubicacion_completa_origen()
    
    def test_get_funcionario_responsable(self, radicacion_base):
        """Test obtener funcionario responsable"""
        assert radicacion_base.get_funcionario_responsable() == "NLOPEZ"
        
        # Cambiar funcionario actual
        radicacion_base.marcar_como_recibida("NUEVOFUNC")
        assert radicacion_base.get_funcionario_responsable() == "NUEVOFUNC"
    
    def test_get_dias_informacion_temporal(self, radicacion_base):
        """Test información temporal"""
        assert radicacion_base.get_dias_en_proceso() == 0  # Creada hoy
        assert radicacion_base.get_dias_restantes_vencimiento() == 60  # 60 días para vencer
        assert radicacion_base.get_nivel_urgencia() == "normal"
    
    def test_get_nivel_urgencia_por_vencimiento(self):
        """Test niveles de urgencia según vencimiento"""
        # Radicación vencida
        fecha_pasada = FechaTramite.crear_para_fecha(date.today() - timedelta(days=70))
        radicacion_vencida = Radicacion.crear_nueva(
            placa=Placa("VEN123"),
            organismo_origen=UbicacionesPredefinidas.CALI,
            fecha_tramite=fecha_pasada,
            funcionario_recibe="JPEREZ"
        )
        assert radicacion_vencida.get_nivel_urgencia() == "vencida"
        
        # Radicación crítica (2 días)
        fecha_critica = FechaTramite.crear_para_fecha(date.today() - timedelta(days=59))
        radicacion_critica = Radicacion.crear_nueva(
            placa=Placa("CRI123"),
            organismo_origen=UbicacionesPredefinidas.FUNZA,
            fecha_tramite=fecha_critica,
            funcionario_recibe="JPEREZ"
        )
        assert radicacion_critica.get_nivel_urgencia() == "critica"


class TestRadicacionValidacionesEstado:
    """Tests para validaciones de estado"""
    
    @pytest.fixture
    def radicacion_pendiente(self):
        """Radicación en estado pendiente"""
        return Radicacion.crear_nueva(
            placa=Placa("PEN123"),
            organismo_origen=UbicacionesPredefinidas.BOGOTA_DC,
            fecha_tramite=FechaTramite.crear_hoy(),
            funcionario_recibe="JPEREZ"
        )
    
    def test_estado_inicial_validaciones(self, radicacion_pendiente):
        """Test validaciones en estado inicial (pendiente)"""
        assert not radicacion_pendiente.esta_vencida()
        assert not radicacion_pendiente.esta_por_vencer()
        assert not radicacion_pendiente.es_critica()
        assert radicacion_pendiente.esta_pendiente()
        assert not radicacion_pendiente.fue_recibida()
        assert not radicacion_pendiente.esta_en_revision()
        assert not radicacion_pendiente.tiene_novedades()
        assert not radicacion_pendiente.esta_completada()
        assert not radicacion_pendiente.fue_devuelta()
        assert not radicacion_pendiente.esta_en_estado_final()
    
    def test_validaciones_despues_recibida(self, radicacion_pendiente):
        """Test validaciones después de ser recibida"""
        radicacion_pendiente.marcar_como_recibida("RECEPTOR")
        
        assert not radicacion_pendiente.esta_pendiente()
        assert radicacion_pendiente.fue_recibida()
        assert radicacion_pendiente.estado == EstadoRadicacion.RECIBIDO
        assert not radicacion_pendiente.esta_en_estado_final()


class TestRadicacionReglasTansiciones:
    """Tests para reglas de transiciones de estado"""
    
    @pytest.fixture
    def radicacion_pendiente(self):
        """Radicación pendiente para tests de transición"""
        return Radicacion.crear_nueva(
            placa=Placa("TRA123"),
            organismo_origen=UbicacionesPredefinidas.MEDELLIN,
            fecha_tramite=FechaTramite.crear_hoy(),
            funcionario_recibe="JPEREZ"
        )
    
    def test_puede_ser_recibida_desde_pendiente(self, radicacion_pendiente):
        """Test puede ser recibida desde pendiente"""
        assert radicacion_pendiente.puede_ser_recibida()
        assert not radicacion_pendiente.puede_pasar_a_revision()
        assert not radicacion_pendiente.puede_completar_radicacion()
        assert not radicacion_pendiente.puede_reportar_novedad()
        assert not radicacion_pendiente.puede_resolver_novedad()
    
    @pytest.fixture
    def radicacion_recibida(self, radicacion_pendiente):
        """Radicación recibida para tests"""
        radicacion_pendiente.marcar_como_recibida("RECEPTOR")
        return radicacion_pendiente
    
    def test_puede_pasar_a_revision_desde_recibida(self, radicacion_recibida):
        """Test puede pasar a revisión desde recibida"""
        assert not radicacion_recibida.puede_ser_recibida()
        assert radicacion_recibida.puede_pasar_a_revision()
        assert not radicacion_recibida.puede_completar_radicacion()
    
    def test_puede_ser_devuelta_admin(self, radicacion_pendiente):
        """Test admin puede devolver desde cualquier estado"""
        assert radicacion_pendiente.puede_ser_devuelta(es_admin=True)
        
        radicacion_pendiente.marcar_como_recibida("RECEPTOR")
        assert radicacion_pendiente.puede_ser_devuelta(es_admin=True)
        
        radicacion_pendiente.marcar_como_revisada("REVISOR")
        assert radicacion_pendiente.puede_ser_devuelta(es_admin=True)


class TestRadicacionTransicionesEstado:
    """Tests para transiciones de estado"""
    
    @pytest.fixture
    def radicacion_para_transiciones(self):
        """Radicación para tests de transiciones"""
        return Radicacion.crear_nueva(
            placa=Placa("TRN123"),
            organismo_origen=UbicacionesPredefinidas.CALI,
            fecha_tramite=FechaTramite.crear_hoy(),
            funcionario_recibe="JPEREZ",
            observaciones_iniciales="Radicación de prueba"
        )
    
    def test_marcar_como_recibida_exitoso(self, radicacion_para_transiciones):
        """Test marcar como recibida exitosamente"""
        radicacion_para_transiciones.marcar_como_recibida("RECEPTOR001")
        
        assert radicacion_para_transiciones.estado == EstadoRadicacion.RECIBIDO
        assert radicacion_para_transiciones.fue_recibida()
        assert radicacion_para_transiciones.funcionario_actual == "RECEPTOR001"
        assert radicacion_para_transiciones.fecha_ultima_actualizacion == date.today()
        
        # Verificar observación de recepción se agregó
        obs = radicacion_para_transiciones.observaciones.valor
        assert "recibida" in obs.lower()
        assert "Cali" in obs  # Nombre del organismo origen
        
        # Ahora puede pasar a revisión
        assert radicacion_para_transiciones.puede_pasar_a_revision()
    
    def test_marcar_como_revisada_exitoso(self, radicacion_para_transiciones):
        """Test marcar como revisada exitosamente"""
        radicacion_para_transiciones.marcar_como_recibida("RECEPTOR001")
        radicacion_para_transiciones.marcar_como_revisada("REVISOR001")
        
        assert radicacion_para_transiciones.estado == EstadoRadicacion.REVISADO
        assert radicacion_para_transiciones.esta_en_revision()
        assert radicacion_para_transiciones.funcionario_actual == "REVISOR001"
        
        # Ahora puede completar o reportar novedad
        assert radicacion_para_transiciones.puede_completar_radicacion()
        assert radicacion_para_transiciones.puede_reportar_novedad()
    
    def test_completar_radicacion_exitoso(self, radicacion_para_transiciones):
        """Test completar radicación exitosamente"""
        radicacion_para_transiciones.marcar_como_recibida("RECEPTOR001")
        radicacion_para_transiciones.marcar_como_revisada("REVISOR001")
        radicacion_para_transiciones.completar_radicacion("COMPLETADOR", "Documentación completa")
        
        assert radicacion_para_transiciones.estado == EstadoRadicacion.RADICADO
        assert radicacion_para_transiciones.esta_completada()
        assert radicacion_para_transiciones.esta_en_estado_final()
        assert radicacion_para_transiciones.funcionario_actual == "COMPLETADOR"
        
        # Verificar observaciones se actualizaron
        assert "COMPLETADA" in radicacion_para_transiciones.observaciones.valor
        assert "completa" in radicacion_para_transiciones.observaciones.valor
    
    def test_reportar_novedad_exitoso(self, radicacion_para_transiciones):
        """Test reportar novedad exitosamente"""
        radicacion_para_transiciones.marcar_como_recibida("RECEPTOR001")
        radicacion_para_transiciones.marcar_como_revisada("REVISOR001")
        radicacion_para_transiciones.reportar_novedad("REVISOR001", "Falta certificado de tradición")
        
        assert radicacion_para_transiciones.estado == EstadoRadicacion.CON_NOVEDADES
        assert radicacion_para_transiciones.tiene_novedades()
        assert not radicacion_para_transiciones.esta_en_estado_final()
        
        # Ahora puede resolver novedad
        assert radicacion_para_transiciones.puede_resolver_novedad()
        assert not radicacion_para_transiciones.puede_completar_radicacion()
        
        # Verificar observaciones
        assert "NOVEDAD REPORTADA" in radicacion_para_transiciones.observaciones.valor
        assert "tradición" in radicacion_para_transiciones.observaciones.valor
    
    def test_resolver_novedad_exitoso(self, radicacion_para_transiciones):
        """Test resolver novedad exitosamente"""
        radicacion_para_transiciones.marcar_como_recibida("RECEPTOR001")
        radicacion_para_transiciones.marcar_como_revisada("REVISOR001")
        radicacion_para_transiciones.reportar_novedad("REVISOR001", "Documento faltante")
        radicacion_para_transiciones.resolver_novedad("RESOLVEDOR", "Documento adjuntado correctamente")
        
        assert radicacion_para_transiciones.estado == EstadoRadicacion.REVISADO
        assert radicacion_para_transiciones.esta_en_revision()
        assert not radicacion_para_transiciones.tiene_novedades()
        assert radicacion_para_transiciones.funcionario_actual == "RESOLVEDOR"
        
        # Vuelve a poder completar
        assert radicacion_para_transiciones.puede_completar_radicacion()
        
        # Verificar observaciones incluyen resolución
        assert "NOVEDAD RESUELTA" in radicacion_para_transiciones.observaciones.valor
        assert "adjuntado" in radicacion_para_transiciones.observaciones.valor
    
    def test_devolver_radicacion_exitoso(self, radicacion_para_transiciones):
        """Test devolver radicación exitosamente"""
        radicacion_para_transiciones.marcar_como_recibida("RECEPTOR001")
        radicacion_para_transiciones.devolver_radicacion("ADMIN", "Documentación incorrecta", es_admin=True)
        
        assert radicacion_para_transiciones.estado == EstadoRadicacion.DEVUELTO
        assert radicacion_para_transiciones.fue_devuelta()
        assert radicacion_para_transiciones.esta_en_estado_final()
        assert radicacion_para_transiciones.funcionario_actual == "ADMIN"
        
        # Verificar observaciones
        assert "RADICACIÓN DEVUELTA" in radicacion_para_transiciones.observaciones.valor
        assert "incorrecta" in radicacion_para_transiciones.observaciones.valor


class TestRadicacionTransicionesError:
    """Tests para errores en transiciones"""
    
    @pytest.fixture
    def radicacion_recibida(self):
        """Radicación en estado recibida"""
        radicacion = Radicacion.crear_nueva(
            placa=Placa("ERR123"),
            organismo_origen=UbicacionesPredefinidas.FUNZA,
            fecha_tramite=FechaTramite.crear_hoy(),
            funcionario_recibe="JPEREZ"
        )
        radicacion.marcar_como_recibida("RECEPTOR")
        return radicacion
    
    def test_marcar_recibida_desde_estado_incorrecto(self, radicacion_recibida):
        """Test error al marcar como recibida desde estado incorrecto"""
        with pytest.raises(ValueError, match="No se puede recibir desde estado"):
            radicacion_recibida.marcar_como_recibida("OTRO")
    
    def test_completar_radicacion_sin_revision_error(self):
        """Test error al completar sin estar en revisión"""
        radicacion = Radicacion.crear_nueva(
            placa=Placa("ERR456"),
            organismo_origen=UbicacionesPredefinidas.MARIQUITA,
            fecha_tramite=FechaTramite.crear_hoy(),
            funcionario_recibe="JPEREZ"
        )
        
        with pytest.raises(ValueError, match="No se puede completar radicación desde estado"):
            radicacion.completar_radicacion("COMPLETADOR")
    
    def test_reportar_novedad_estado_incorrecto_error(self):
        """Test error al reportar novedad desde estado incorrecto"""
        radicacion = Radicacion.crear_nueva(
            placa=Placa("ERR789"),
            organismo_origen=UbicacionesPredefinidas.SOGAMOSO,
            fecha_tramite=FechaTramite.crear_hoy(),
            funcionario_recibe="JPEREZ"
        )
        
        with pytest.raises(ValueError, match="No se puede reportar novedad desde estado"):
            radicacion.reportar_novedad("REVISOR", "Alguna novedad")
    
    def test_resolver_novedad_sin_novedades_error(self, radicacion_recibida):
        """Test error al resolver novedad sin tener novedades"""
        radicacion_recibida.marcar_como_revisada("REVISOR")
        
        with pytest.raises(ValueError, match="No se puede resolver novedad desde estado"):
            radicacion_recibida.resolver_novedad("RESOLVEDOR", "No hay novedades")


class TestRadicacionActualizacionObservaciones:
    """Tests para actualización de observaciones"""
    
    @pytest.fixture
    def radicacion_con_observaciones(self):
        """Radicación con observaciones iniciales"""
        return Radicacion.crear_nueva(
            placa=Placa("OBS123"),
            organismo_origen=UbicacionesPredefinidas.BOGOTA_DC,
            fecha_tramite=FechaTramite.crear_hoy(),
            funcionario_recibe="JPEREZ",
            observaciones_iniciales="Observación inicial"
        )
    
    def test_actualizar_observaciones_exitoso(self, radicacion_con_observaciones):
        """Test actualizar observaciones exitosamente"""
        radicacion_con_observaciones.actualizar_observaciones("ACTUALIZADOR", "Nueva información relevante")
        
        assert "Nueva información relevante" in radicacion_con_observaciones.observaciones.valor
        assert "ACTUALIZADOR" in radicacion_con_observaciones.observaciones.valor
        assert radicacion_con_observaciones.fecha_ultima_actualizacion == date.today()
        
        # Las observaciones anteriores se mantienen
        assert "inicial" in radicacion_con_observaciones.observaciones.valor.lower()
    
    def test_actualizar_observaciones_estado_final_error(self, radicacion_con_observaciones):
        """Test error al actualizar observaciones en estado final"""
        radicacion_con_observaciones.marcar_como_recibida("RECEPTOR")
        radicacion_con_observaciones.marcar_como_revisada("REVISOR")
        radicacion_con_observaciones.completar_radicacion("COMPLETADOR")
        
        with pytest.raises(ValueError, match="No se pueden actualizar observaciones en estado final"):
            radicacion_con_observaciones.actualizar_observaciones("ACTUALIZADOR", "Intento actualizar")


class TestRadicacionFactoryMethods:
    """Tests para factory methods"""
    
    def test_crear_desde_repositorio_exitoso(self):
        """Test recrear radicación desde repositorio"""
        placa = Placa("REP123")
        organismo = UbicacionesPredefinidas.MANIZALES
        fecha_tramite = FechaTramite.crear_hoy()
        fecha_vencimiento = FechaVencimiento.calcular_desde_tramite(fecha_tramite)
        observaciones = Observacion.crear_desde_texto("Observación desde repo")
        
        radicacion = Radicacion.crear_desde_repositorio(
            placa=placa,
            organismo_origen=organismo,
            fecha_tramite=fecha_tramite,
            fecha_vencimiento=fecha_vencimiento,
            funcionario_recibe="ORIGINAL",
            estado=EstadoRadicacion.REVISADO,
            observaciones=observaciones,
            funcionario_actual="ACTUAL",
            fecha_ultima_actualizacion=date.today() - timedelta(days=1)
        )
        
        assert radicacion.placa == placa
        assert radicacion.estado == EstadoRadicacion.REVISADO
        assert radicacion.funcionario_recibe == "ORIGINAL"
        assert radicacion.funcionario_actual == "ACTUAL"
        assert radicacion.observaciones == observaciones
        assert radicacion.fecha_ultima_actualizacion == date.today() - timedelta(days=1)


class TestRadicacionRepresentacion:
    """Tests para métodos de representación"""
    
    def test_str_y_repr(self):
        """Test métodos __str__ y __repr__"""
        radicacion = Radicacion.crear_nueva(
            placa=Placa("STR123"),
            organismo_origen=UbicacionesPredefinidas.CALI,
            fecha_tramite=FechaTramite.crear_hoy(),
            funcionario_recibe="JPEREZ"
        )
        
        str_resultado = str(radicacion)
        assert "STR123" in str_resultado
        assert "Cali" in str_resultado
        assert "←" in str_resultado  # Indica dirección de la radicación (recepción)
        
        repr_resultado = repr(radicacion)
        assert "Radicacion" in repr_resultado
        assert "placa='STR123'" in repr_resultado
        assert "origen='CALI'" in repr_resultado
        assert "estado='pendiente_radicar'" in repr_resultado


class TestRadicacionIntegracion:
    """Tests de integración completos"""
    
    def test_flujo_completo_exitoso(self):
        """Test flujo completo de radicación exitosa"""
        # 1. Crear radicación
        radicacion = Radicacion.crear_nueva(
            placa=Placa("FLU123"),
            organismo_origen=UbicacionesPredefinidas.MEDELLIN,
            fecha_tramite=FechaTramite.crear_hoy(),
            funcionario_recibe="RECEPTOR",
            observaciones_iniciales="Radicación por cambio de residencia"
        )
        
        assert radicacion.estado == EstadoRadicacion.PENDIENTE_RADICAR
        assert radicacion.esta_pendiente()
        
        # 2. Marcar como recibida
        radicacion.marcar_como_recibida("RECEPTOR")
        assert radicacion.fue_recibida()
        
        # 3. Marcar como revisada
        radicacion.marcar_como_revisada("REVISOR")
        assert radicacion.esta_en_revision()
        
        # 4. Completar radicación
        radicacion.completar_radicacion("COMPLETADOR", "Documentación verificada")
        assert radicacion.esta_completada()
        assert radicacion.esta_en_estado_final()
        
        # Verificar trazabilidad completa
        assert "RECEPTOR" == radicacion.funcionario_recibe
        assert "COMPLETADOR" == radicacion.funcionario_actual
        assert "residencia" in radicacion.observaciones.valor
        assert "verificada" in radicacion.observaciones.valor
        assert "recibida del Medellin" in radicacion.observaciones.valor
    
    def test_flujo_con_novedades(self):
        """Test flujo con novedades y resolución"""
        radicacion = Radicacion.crear_nueva(
            placa=Placa("NOV123"),
            organismo_origen=UbicacionesPredefinidas.FUNZA,
            fecha_tramite=FechaTramite.crear_hoy(),
            funcionario_recibe="RECEPTOR"
        )
        
        # 1. Recibir
        radicacion.marcar_como_recibida("RECEPTOR")
        
        # 2. Revisar
        radicacion.marcar_como_revisada("REVISOR")
        
        # 3. Reportar novedad
        radicacion.reportar_novedad("REVISOR", "Falta firma del propietario")
        assert radicacion.tiene_novedades()
        
        # 4. Resolver novedad
        radicacion.resolver_novedad("RESOLVEDOR", "Firma adjuntada")
        assert not radicacion.tiene_novedades()
        assert radicacion.esta_en_revision()
        
        # 5. Completar
        radicacion.completar_radicacion("COMPLETADOR")
        assert radicacion.esta_completada()
        
        # Verificar todas las observaciones están presentes
        obs = radicacion.observaciones.valor
        assert "NOVEDAD REPORTADA" in obs
        assert "firma" in obs.lower()
        assert "NOVEDAD RESUELTA" in obs
        assert "adjuntada" in obs.lower()
        assert "recibida del Funza" in obs
    
    def test_flujo_devolucion_admin(self):
        """Test flujo de devolución por admin"""
        radicacion = Radicacion.crear_nueva(
            placa=Placa("DEV123"),
            organismo_origen=UbicacionesPredefinidas.MARIQUITA,
            fecha_tramite=FechaTramite.crear_hoy(),
            funcionario_recibe="RECEPTOR"
        )
        
        # Recibir primero
        radicacion.marcar_como_recibida("RECEPTOR")
        
        # Admin puede devolver desde cualquier estado
        radicacion.devolver_radicacion("ADMIN", "Proceso cancelado por duplicado", es_admin=True)
        
        assert radicacion.fue_devuelta()
        assert radicacion.esta_en_estado_final()
        assert "cancelado" in radicacion.observaciones.valor.lower()
        assert "duplicado" in radicacion.observaciones.valor.lower()
        assert "ADMIN" == radicacion.funcionario_actual
    
    def test_flujo_directo_pendiente_a_devolucion(self):
        """Test devolución directa desde estado pendiente"""
        radicacion = Radicacion.crear_nueva(
            placa=Placa("DIR123"),
            organismo_origen=UbicacionesPredefinidas.SOGAMOSO,
            fecha_tramite=FechaTramite.crear_hoy(),
            funcionario_recibe="RECEPTOR"
        )
        
        # Admin puede devolver directamente sin recibir
        radicacion.devolver_radicacion("ADMIN", "Error en el envío", es_admin=True)
        
        assert radicacion.fue_devuelta()
        assert radicacion.esta_en_estado_final()
        assert not radicacion.fue_recibida()  # Nunca fue recibida
        assert "Error en el envío" in radicacion.observaciones.valor