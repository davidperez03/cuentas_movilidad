# tests/unit/cuentas/domain/value_objects/test_fecha_tramite.py
import pytest
from datetime import date, timedelta
from app.cuentas.domain.value_objects.fecha_tramite import FechaTramite


class TestFechaTramiteCreacion:
    """Tests para creación de fechas de trámite"""
    
    def test_crear_fecha_tramite_hoy(self):
        """Test crear fecha de trámite para hoy"""
        hoy = date.today()
        fecha = FechaTramite(hoy)
        assert fecha.fecha == hoy
        assert fecha.es_de_hoy() == True
        assert fecha.es_futuro() == False
        assert fecha.es_pasado() == False
    
    def test_crear_fecha_tramite_ayer(self):
        """Test crear fecha de trámite para ayer"""
        ayer = date.today() - timedelta(days=1)
        fecha = FechaTramite(ayer)
        assert fecha.fecha == ayer
        assert fecha.es_de_hoy() == False
        assert fecha.es_futuro() == False
        assert fecha.es_pasado() == True
    
    def test_crear_fecha_tramite_mañana(self):
        """Test crear fecha de trámite para mañana"""
        mañana = date.today() + timedelta(days=1)
        fecha = FechaTramite(mañana)
        assert fecha.fecha == mañana
        assert fecha.es_de_hoy() == False
        assert fecha.es_futuro() == True
        assert fecha.es_pasado() == False
    
    def test_fecha_tipo_invalido_error(self):
        """Test que tipo inválido genera error"""
        with pytest.raises(ValueError, match="debe ser un objeto date válido"):
            FechaTramite("2024-12-04")
    
    def test_fecha_none_error(self):
        """Test que None genera error"""
        with pytest.raises(ValueError, match="debe ser un objeto date válido"):
            FechaTramite(None)


class TestFechaTramiteValidacionRangos:
    """Tests para validación de rangos permitidos"""
    
    def test_fecha_futuro_cercano_valida(self):
        """Test que fecha futura cercana (30 días) es válida"""
        futuro_cercano = date.today() + timedelta(days=30)
        fecha = FechaTramite(futuro_cercano)
        assert fecha.es_futuro() == True
        assert fecha.esta_en_rango_permitido() == True
    
    def test_fecha_futuro_lejano_error(self):
        """Test que fecha futura lejana (>30 días) genera error"""
        futuro_lejano = date.today() + timedelta(days=31)
        with pytest.raises(ValueError, match="no puede ser más de 30 días en el futuro"):
            FechaTramite(futuro_lejano)
    
    def test_fecha_pasado_cercano_valida(self):
        """Test que fecha pasada cercana (1 año) es válida"""
        pasado_cercano = date.today() - timedelta(days=365)
        fecha = FechaTramite(pasado_cercano)
        assert fecha.es_pasado() == True
        assert fecha.esta_en_rango_permitido() == True
    
    def test_fecha_pasado_lejano_error(self):
        """Test que fecha pasada lejana (>1 año) genera error"""
        pasado_lejano = date.today() - timedelta(days=366)
        with pytest.raises(ValueError, match="no puede ser más de 1 año en el pasado"):
            FechaTramite(pasado_lejano)
    
    def test_esta_en_rango_permitido(self):
        """Test verificación de rango permitido"""
        # Fecha válida en el rango
        fecha_valida = date.today() - timedelta(days=100)
        fecha = FechaTramite(fecha_valida)
        assert fecha.esta_en_rango_permitido() == True


class TestFechaTramiteCalculos:
    """Tests para cálculos de días y diferencias"""
    
    def test_dias_desde_hoy_presente(self):
        """Test días desde hoy para fecha actual"""
        hoy = date.today()
        fecha = FechaTramite(hoy)
        assert fecha.dias_desde_hoy() == 0
    
    def test_dias_desde_hoy_pasado(self):
        """Test días desde hoy para fecha pasada"""
        hace_5_dias = date.today() - timedelta(days=5)
        fecha = FechaTramite(hace_5_dias)
        assert fecha.dias_desde_hoy() == 5  # Positivo = pasado
    
    def test_dias_desde_hoy_futuro(self):
        """Test días desde hoy para fecha futura"""
        en_3_dias = date.today() + timedelta(days=3)
        fecha = FechaTramite(en_3_dias)
        assert fecha.dias_desde_hoy() == -3  # Negativo = futuro
    
    def test_dias_hasta_tramite_futuro(self):
        """Test días hasta trámite para fecha futura"""
        en_7_dias = date.today() + timedelta(days=7)
        fecha = FechaTramite(en_7_dias)
        assert fecha.dias_hasta_tramite() == 7
    
    def test_dias_hasta_tramite_presente_pasado(self):
        """Test días hasta trámite para fecha presente/pasada"""
        hoy = date.today()
        ayer = date.today() - timedelta(days=1)
        
        fecha_hoy = FechaTramite(hoy)
        fecha_ayer = FechaTramite(ayer)
        
        assert fecha_hoy.dias_hasta_tramite() == 0
        assert fecha_ayer.dias_hasta_tramite() == 0


class TestFechaTramiteDiasLaborales:
    """Tests para funcionalidad de días laborales"""
    
    def test_es_fin_de_semana_sabado(self):
        """Test detección de sábado como fin de semana"""
        # Encontrar próximo sábado
        fecha_actual = date.today()
        dias_hasta_sabado = (5 - fecha_actual.weekday()) % 7
        if dias_hasta_sabado == 0:
            dias_hasta_sabado = 7
        sabado = fecha_actual + timedelta(days=dias_hasta_sabado)
        
        fecha = FechaTramite(sabado)
        assert fecha.es_fin_de_semana() == True
        assert fecha.es_dia_laboral() == False
    
    def test_es_fin_de_semana_domingo(self):
        """Test detección de domingo como fin de semana"""
        # Encontrar próximo domingo
        fecha_actual = date.today()
        dias_hasta_domingo = (6 - fecha_actual.weekday()) % 7
        if dias_hasta_domingo == 0:
            dias_hasta_domingo = 7
        domingo = fecha_actual + timedelta(days=dias_hasta_domingo)
        
        fecha = FechaTramite(domingo)
        assert fecha.es_fin_de_semana() == True
        assert fecha.es_dia_laboral() == False
    
    def test_es_dia_laboral_lunes(self):
        """Test detección de lunes como día laboral"""
        # Encontrar próximo lunes
        fecha_actual = date.today()
        dias_hasta_lunes = (0 - fecha_actual.weekday()) % 7
        if dias_hasta_lunes == 0:
            dias_hasta_lunes = 7
        lunes = fecha_actual + timedelta(days=dias_hasta_lunes)
        
        fecha = FechaTramite(lunes)
        assert fecha.es_dia_laboral() == True
        assert fecha.es_fin_de_semana() == False
    
    def test_siguiente_dia_laboral_desde_viernes(self):
        """Test siguiente día laboral desde viernes"""
        # Encontrar próximo viernes
        fecha_actual = date.today()
        dias_hasta_viernes = (4 - fecha_actual.weekday()) % 7
        if dias_hasta_viernes == 0:
            dias_hasta_viernes = 7
        viernes = fecha_actual + timedelta(days=dias_hasta_viernes)
        
        fecha = FechaTramite(viernes)
        siguiente = fecha.siguiente_dia_laboral()
        
        # Desde viernes, el siguiente día laboral es el mismo viernes
        assert siguiente == viernes
    
    def test_siguiente_dia_laboral_desde_sabado(self):
        """Test siguiente día laboral desde sábado"""
        # Encontrar próximo sábado
        fecha_actual = date.today()
        dias_hasta_sabado = (5 - fecha_actual.weekday()) % 7
        if dias_hasta_sabado == 0:
            dias_hasta_sabado = 7
        sabado = fecha_actual + timedelta(days=dias_hasta_sabado)
        
        fecha = FechaTramite(sabado)
        siguiente = fecha.siguiente_dia_laboral()
        
        # Desde sábado, el siguiente día laboral debe ser lunes
        assert siguiente.weekday() == 0  # 0 = Lunes


class TestFechaTramiteExtraccion:
    """Tests para extracción de componentes de fecha"""
    
    def test_get_componentes_fecha(self):
        """Test extracción de componentes de fecha"""
        fecha_test = date(2024, 12, 4)  # Miércoles
        fecha = FechaTramite(fecha_test)
        
        assert fecha.get_year() == 2024
        assert fecha.get_month() == 12
        assert fecha.get_day() == 4
        assert fecha.get_weekday() == 2  # 0=Lunes, 2=Miércoles
    
    def test_get_weekday_name(self):
        """Test obtención de nombre de día de la semana"""
        # Usar fecha conocida: 2024-12-04 es miércoles
        fecha_test = date(2024, 12, 4)
        fecha = FechaTramite(fecha_test)
        assert fecha.get_weekday_name() == "Miércoles"


class TestFechaTramiteFormatos:
    """Tests para formatos de salida"""
    
    def test_formato_legible(self):
        """Test formato legible ISO"""
        fecha_test = date(2024, 12, 4)
        fecha = FechaTramite(fecha_test)
        assert fecha.formato_legible() == "2024-12-04"
    
    def test_formato_español(self):
        """Test formato español"""
        fecha_test = date(2024, 12, 4)
        fecha = FechaTramite(fecha_test)
        assert fecha.formato_español() == "04/12/2024"
    
    def test_formato_completo(self):
        """Test formato completo con día de semana"""
        fecha_test = date(2024, 12, 4)  # Miércoles
        fecha = FechaTramite(fecha_test)
        assert fecha.formato_completo() == "Miércoles, 04/12/2024"
    
    def test_str_representation(self):
        """Test representación string"""
        fecha_test = date(2024, 12, 4)
        fecha = FechaTramite(fecha_test)
        assert str(fecha) == "2024-12-04"
    
    def test_repr_representation_hoy(self):
        """Test representación repr para hoy"""
        hoy = date.today()
        fecha = FechaTramite(hoy)
        expected = f"FechaTramite(fecha={hoy}, estado=hoy, dias_desde_hoy=0)"
        assert repr(fecha) == expected
    
    def test_repr_representation_futuro(self):
        """Test representación repr para fecha futura"""
        mañana = date.today() + timedelta(days=1)
        fecha = FechaTramite(mañana)
        expected = f"FechaTramite(fecha={mañana}, estado=futuro, dias_desde_hoy=-1)"
        assert repr(fecha) == expected


class TestFechaTramiteFactoryMethods:
    """Tests para factory methods"""
    
    def test_crear_hoy(self):
        """Test factory method crear_hoy"""
        fecha = FechaTramite.crear_hoy()
        assert fecha.fecha == date.today()
        assert fecha.es_de_hoy() == True
    
    def test_crear_para_fecha(self):
        """Test factory method crear_para_fecha"""
        fecha_test = date.today() - timedelta(days=5)
        fecha = FechaTramite.crear_para_fecha(fecha_test)
        assert fecha.fecha == fecha_test
    
    def test_crear_desde_string_iso(self):
        """Test factory method desde string ISO"""
        fecha = FechaTramite.crear_desde_string("2024-12-04")
        assert fecha.fecha == date(2024, 12, 4)
    
    def test_crear_desde_string_español(self):
        """Test factory method desde string español"""
        fecha = FechaTramite.crear_desde_string("04/12/2024")
        assert fecha.fecha == date(2024, 12, 4)
    
    def test_crear_desde_string_invalido(self):
        """Test factory method con string inválido"""
        with pytest.raises(ValueError, match="No se pudo parsear"):
            FechaTramite.crear_desde_string("fecha_invalida")
    
    def test_crear_si_valida_exitoso(self):
        """Test factory method crear_si_valida exitoso"""
        ayer = date.today() - timedelta(days=1)
        fecha = FechaTramite.crear_si_valida(ayer)
        assert fecha is not None
        assert fecha.fecha == ayer
    
    def test_crear_si_valida_fallido(self):
        """Test factory method crear_si_valida fallido"""
        fecha_invalida = date.today() + timedelta(days=100)  # Muy futuro
        fecha = FechaTramite.crear_si_valida(fecha_invalida)
        assert fecha is None
    
    def test_crear_siguiente_dia_laboral_dia_laboral(self):
        """Test crear siguiente día laboral cuando hoy es laboral"""
        # Este test depende del día actual, usaremos lógica condicional
        fecha = FechaTramite.crear_siguiente_dia_laboral()
        assert fecha.es_dia_laboral() == True
    
    def test_crear_con_validacion_laboral_sin_ajuste(self):
        """Test crear con validación laboral sin ajuste necesario"""
        # Usar lunes conocido: 2024-12-02
        lunes = date(2024, 12, 2)  # Asumiendo que es lunes
        if lunes.weekday() == 0:  # Verificar que sea lunes
            fecha = FechaTramite.crear_con_validacion_laboral(lunes, solo_dias_laborales=False)
            assert fecha.fecha == lunes
    
    def test_crear_con_validacion_laboral_con_ajuste(self):
        """Test crear con validación laboral con ajuste automático"""
        # Usar sábado conocido y verificar que se ajuste a lunes
        sabado = date(2024, 12, 7)  # Asumiendo que es sábado
        if sabado.weekday() == 5:  # Verificar que sea sábado
            fecha = FechaTramite.crear_con_validacion_laboral(sabado, solo_dias_laborales=True)
            assert fecha.es_dia_laboral() == True
            assert fecha.fecha.weekday() == 0  # Debería ajustarse a lunes


class TestFechaTramiteInmutabilidad:
    """Tests para inmutabilidad del value object"""
    
    def test_fecha_tramite_es_inmutable(self):
        """Test que fecha de trámite no se puede modificar"""
        fecha = FechaTramite.crear_hoy()
        
        with pytest.raises(AttributeError):
            fecha.fecha = date.today() - timedelta(days=1)
    
    def test_fecha_tramite_hasheable(self):
        """Test que fecha de trámite es hasheable"""
        fecha = FechaTramite.crear_hoy()
        conjunto = {fecha}
        assert len(conjunto) == 1
        assert fecha in conjunto
    
    def test_igualdad_fechas_tramite(self):
        """Test igualdad entre fechas de trámite"""
        hoy = date.today()
        fecha1 = FechaTramite(hoy)
        fecha2 = FechaTramite.crear_hoy()
        assert fecha1 == fecha2


class TestFechaTramiteCasosReales:
    """Tests con casos de uso reales del sistema"""
    
    def test_tramite_inmediato_hoy(self):
        """Test caso típico: trámite para hoy"""
        fecha = FechaTramite.crear_hoy()
        
        assert fecha.es_de_hoy() == True
        assert fecha.dias_desde_hoy() == 0
        assert fecha.dias_hasta_tramite() == 0
        assert fecha.esta_en_rango_permitido() == True
    
    def test_tramite_programado_futuro(self):
        """Test trámite programado para fecha futura"""
        en_una_semana = date.today() + timedelta(days=7)
        fecha = FechaTramite(en_una_semana)
        
        assert fecha.es_futuro() == True
        assert fecha.dias_hasta_tramite() == 7
        assert fecha.dias_desde_hoy() == -7
        assert fecha.esta_en_rango_permitido() == True
    
    def test_tramite_retroactivo_pasado(self):
        """Test trámite retroactivo (fecha pasada)"""
        hace_un_mes = date.today() - timedelta(days=30)
        fecha = FechaTramite(hace_un_mes)
        
        assert fecha.es_pasado() == True
        assert fecha.dias_desde_hoy() == 30
        assert fecha.dias_hasta_tramite() == 0
        assert fecha.esta_en_rango_permitido() == True
    
    def test_validacion_rangos_limite(self):
        """Test validación en los límites exactos del rango"""
        # Límite futuro exacto (30 días)
        limite_futuro = date.today() + timedelta(days=30)
        fecha_futuro = FechaTramite(limite_futuro)
        assert fecha_futuro.esta_en_rango_permitido() == True
        
        # Límite pasado exacto (365 días)
        limite_pasado = date.today() - timedelta(days=365)
        fecha_pasado = FechaTramite(limite_pasado)
        assert fecha_pasado.esta_en_rango_permitido() == True
    
    def test_uso_con_dias_laborales(self):
        """Test uso típico considerando días laborales"""
        # Crear fecha para próximo día laboral
        fecha = FechaTramite.crear_siguiente_dia_laboral()
        
        assert fecha.es_dia_laboral() == True
        # Si se crea hoy y es día laboral, debería ser hoy
        # Si se crea en fin de semana, debería ser el siguiente lunes
        
    def test_formato_para_interfaz_usuario(self):
        """Test formatos utilizados en interfaz de usuario"""
        fecha_test = date.today()
        fecha = FechaTramite(fecha_test)
        
        # Formato para mostrar en formularios
        formato_form = fecha.formato_español()
        assert "/" in formato_form
        
        # Formato para mostrar con contexto
        formato_completo = fecha.formato_completo()
        assert fecha.get_weekday_name() in formato_completo