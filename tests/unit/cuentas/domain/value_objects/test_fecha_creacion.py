import pytest
from datetime import date, timedelta
from app.cuentas.domain.value_objects.fecha_creacion import FechaCreacion


class TestFechaCreacionCreacion:
    """Tests para creación de fechas de creación"""
    
    def test_crear_fecha_creacion_hoy(self):
        """Test crear fecha de creación para hoy"""
        hoy = date.today()
        fecha = FechaCreacion(hoy)
        assert fecha.fecha == hoy
        assert fecha.es_de_hoy() == True
    
    def test_crear_fecha_creacion_ayer(self):
        """Test crear fecha de creación para ayer"""
        ayer = date.today() - timedelta(days=1)
        fecha = FechaCreacion(ayer)
        assert fecha.fecha == ayer
        assert fecha.es_de_ayer() == True
    
    def test_crear_fecha_creacion_antigua(self):
        """Test crear fecha de creación antigua"""
        antigua = date.today() - timedelta(days=365)
        fecha = FechaCreacion(antigua)
        assert fecha.fecha == antigua
        assert fecha.es_antigua() == True
    
    def test_fecha_futura_error(self):
        """Test que fecha futura genera error"""
        mañana = date.today() + timedelta(days=1)
        with pytest.raises(ValueError, match="no puede ser futura"):
            FechaCreacion(mañana)
    
    def test_fecha_invalida_tipo_error(self):
        """Test que tipo inválido genera error"""
        with pytest.raises(ValueError, match="debe ser un objeto date válido"):
            FechaCreacion("2024-12-04")
    
    def test_fecha_none_error(self):
        """Test que None genera error"""
        with pytest.raises(ValueError, match="debe ser un objeto date válido"):
            FechaCreacion(None)


class TestFechaCreacionValidaciones:
    """Tests para validaciones de fechas"""
    
    def test_fecha_hoy_valida(self):
        """Test que fecha de hoy es válida"""
        hoy = date.today()
        fecha = FechaCreacion(hoy)
        assert fecha.es_de_hoy() == True
        assert fecha.dias_desde_creacion() == 0
    
    def test_fecha_ayer_valida(self):
        """Test que fecha de ayer es válida"""
        ayer = date.today() - timedelta(days=1)
        fecha = FechaCreacion(ayer)
        assert fecha.es_de_ayer() == True
        assert fecha.dias_desde_creacion() == 1
    
    def test_fecha_muy_futura_error(self):
        """Test que fecha muy futura genera error"""
        futuro = date.today() + timedelta(days=365)
        with pytest.raises(ValueError, match="no puede ser futura"):
            FechaCreacion(futuro)


class TestFechaCreacionCalculos:
    """Tests para cálculos de tiempo transcurrido"""
    
    def test_dias_desde_creacion_hoy(self):
        """Test días desde creación para hoy"""
        hoy = date.today()
        fecha = FechaCreacion(hoy)
        assert fecha.dias_desde_creacion() == 0
    
    def test_dias_desde_creacion_ayer(self):
        """Test días desde creación para ayer"""
        ayer = date.today() - timedelta(days=1)
        fecha = FechaCreacion(ayer)
        assert fecha.dias_desde_creacion() == 1
    
    def test_dias_desde_creacion_semana(self):
        """Test días desde creación para hace una semana"""
        semana_pasada = date.today() - timedelta(days=7)
        fecha = FechaCreacion(semana_pasada)
        assert fecha.dias_desde_creacion() == 7
    
    def test_semanas_desde_creacion(self):
        """Test semanas desde creación"""
        hace_3_semanas = date.today() - timedelta(days=21)
        fecha = FechaCreacion(hace_3_semanas)
        assert fecha.semanas_desde_creacion() == 3
    
    def test_meses_desde_creacion(self):
        """Test meses aproximados desde creación"""
        hace_2_meses = date.today() - timedelta(days=60)
        fecha = FechaCreacion(hace_2_meses)
        assert fecha.meses_desde_creacion() == 2
    
    def test_meses_desde_creacion_parcial(self):
        """Test meses parciales desde creación"""
        hace_45_dias = date.today() - timedelta(days=45)
        fecha = FechaCreacion(hace_45_dias)
        assert fecha.meses_desde_creacion() == 1  


class TestFechaCreacionClasificaciones:
    """Tests para clasificaciones de fechas"""
    
    def test_es_reciente_verdadero(self):
        """Test es_reciente para fechas recientes"""
        hace_3_dias = date.today() - timedelta(days=3)
        fecha = FechaCreacion(hace_3_dias)
        assert fecha.es_reciente() == True  
        assert fecha.es_reciente(5) == True  
    
    def test_es_reciente_falso(self):
        """Test es_reciente para fechas no recientes"""
        hace_10_dias = date.today() - timedelta(days=10)
        fecha = FechaCreacion(hace_10_dias)
        assert fecha.es_reciente() == False  
        assert fecha.es_reciente(5) == False  
    
    def test_es_antigua_verdadero(self):
        """Test es_antigua para fechas antiguas"""
        hace_2_años = date.today() - timedelta(days=730)
        fecha = FechaCreacion(hace_2_años)
        assert fecha.es_antigua() == True  
        assert fecha.es_antigua(365) == True 
    
    def test_es_antigua_falso(self):
        """Test es_antigua para fechas no antiguas"""
        hace_6_meses = date.today() - timedelta(days=180)
        fecha = FechaCreacion(hace_6_meses)
        assert fecha.es_antigua() == False  
        assert fecha.es_antigua(100) == True  
    
    def test_clasificaciones_hoy(self):
        """Test clasificaciones para fecha de hoy"""
        hoy = date.today()
        fecha = FechaCreacion(hoy)
        assert fecha.es_reciente() == True
        assert fecha.es_antigua() == False
        assert fecha.es_de_hoy() == True
        assert fecha.es_de_ayer() == False


class TestFechaCreacionExtraccion:
    """Tests para extracción de componentes de fecha"""
    
    def test_get_year(self):
        """Test extracción de año"""
        fecha_test = date(2024, 12, 4)
        fecha = FechaCreacion(fecha_test)
        assert fecha.get_year() == 2024
    
    def test_get_month(self):
        """Test extracción de mes"""
        fecha_test = date(2024, 12, 4)
        fecha = FechaCreacion(fecha_test)
        assert fecha.get_month() == 12
    
    def test_get_day(self):
        """Test extracción de día"""
        fecha_test = date(2024, 12, 4)
        fecha = FechaCreacion(fecha_test)
        assert fecha.get_day() == 4


class TestFechaCreacionFormatos:
    """Tests para formatos de salida"""
    
    def test_formato_legible(self):
        """Test formato legible ISO"""
        fecha_test = date(2024, 12, 4)
        fecha = FechaCreacion(fecha_test)
        assert fecha.formato_legible() == "2024-12-04"
    
    def test_formato_español(self):
        """Test formato español"""
        fecha_test = date(2024, 12, 4)
        fecha = FechaCreacion(fecha_test)
        assert fecha.formato_español() == "04/12/2024"
    
    def test_str_representation(self):
        """Test representación string"""
        fecha_test = date(2024, 12, 4)
        fecha = FechaCreacion(fecha_test)
        assert str(fecha) == "2024-12-04"
    
    def test_repr_representation(self):
        """Test representación repr"""
        ayer = date.today() - timedelta(days=1)
        fecha = FechaCreacion(ayer)
        expected = f"FechaCreacion(fecha={ayer}, dias_transcurridos=1)"
        assert repr(fecha) == expected


class TestFechaCreacionFactoryMethods:
    """Tests para factory methods"""
    
    def test_crear_hoy(self):
        """Test factory method crear_hoy"""
        fecha = FechaCreacion.crear_hoy()
        assert fecha.fecha == date.today()
        assert fecha.es_de_hoy() == True
    
    def test_crear_para_fecha(self):
        """Test factory method crear_para_fecha"""
        fecha_test = date(2024, 12, 4)
        fecha = FechaCreacion.crear_para_fecha(fecha_test)
        assert fecha.fecha == fecha_test
    
    def test_crear_para_fecha_futura_error(self):
        """Test factory method con fecha futura"""
        mañana = date.today() + timedelta(days=1)
        with pytest.raises(ValueError, match="no puede ser futura"):
            FechaCreacion.crear_para_fecha(mañana)
    
    def test_crear_desde_string_iso(self):
        """Test factory method desde string ISO"""
        fecha = FechaCreacion.crear_desde_string("2024-12-04")
        assert fecha.fecha == date(2024, 12, 4)
    
    def test_crear_desde_string_español(self):
        """Test factory method desde string español"""
        fecha = FechaCreacion.crear_desde_string("04/12/2024")
        assert fecha.fecha == date(2024, 12, 4)
    
    def test_crear_desde_string_invalido(self):
        """Test factory method con string inválido"""
        with pytest.raises(ValueError, match="No se pudo parsear"):
            FechaCreacion.crear_desde_string("fecha_invalida")
    
    def test_crear_desde_string_formato_incorrecto(self):
        """Test factory method con formato incorrecto"""
        with pytest.raises(ValueError, match="No se pudo parsear"):
            FechaCreacion.crear_desde_string("2024/12/04")  
    
    def test_crear_si_valida_exitoso(self):
        """Test factory method crear_si_valida exitoso"""
        ayer = date.today() - timedelta(days=1)
        fecha = FechaCreacion.crear_si_valida(ayer)
        assert fecha is not None
        assert fecha.fecha == ayer
    
    def test_crear_si_valida_fallido(self):
        """Test factory method crear_si_valida fallido"""
        mañana = date.today() + timedelta(days=1)
        fecha = FechaCreacion.crear_si_valida(mañana)
        assert fecha is None


class TestFechaCreacionInmutabilidad:
    """Tests para inmutabilidad del value object"""
    
    def test_fecha_creacion_es_inmutable(self):
        """Test que fecha de creación no se puede modificar"""
        fecha = FechaCreacion.crear_hoy()
        
        with pytest.raises(AttributeError):
            fecha.fecha = date.today() - timedelta(days=1)
    
    def test_fecha_creacion_hasheable(self):
        """Test que fecha de creación es hasheable"""
        fecha = FechaCreacion.crear_hoy()
        conjunto = {fecha}
        assert len(conjunto) == 1
        assert fecha in conjunto
    
    def test_igualdad_fechas_creacion(self):
        """Test igualdad entre fechas de creación"""
        hoy = date.today()
        fecha1 = FechaCreacion(hoy)
        fecha2 = FechaCreacion.crear_hoy()
        assert fecha1 == fecha2


class TestFechaCreacionCasosReales:
    """Tests con casos de uso reales del sistema"""
    
    def test_cuenta_creada_hoy_uso_tipico(self):
        """Test caso típico: cuenta creada hoy"""
        fecha = FechaCreacion.crear_hoy()
        
        assert fecha.es_de_hoy() == True
        assert fecha.es_reciente() == True
        assert fecha.es_antigua() == False
        assert fecha.dias_desde_creacion() == 0
    
    def test_cuenta_creada_hace_una_semana(self):
        """Test cuenta creada hace una semana"""
        hace_semana = date.today() - timedelta(days=7)
        fecha = FechaCreacion(hace_semana)
        
        assert fecha.es_de_hoy() == False
        assert fecha.es_reciente() == True  
        assert fecha.es_antigua() == False
        assert fecha.semanas_desde_creacion() == 1
    
    def test_cuenta_creada_hace_un_año(self):
        """Test cuenta creada hace exactamente un año (365 días)"""
        hace_año = date.today() - timedelta(days=365)
        fecha = FechaCreacion(hace_año)
        
        assert fecha.es_de_hoy() == False
        assert fecha.es_reciente() == False
        assert fecha.es_antigua() == True  
        assert fecha.meses_desde_creacion() == 12
    
    def test_cuenta_creada_hace_364_dias(self):
        """Test cuenta creada hace 364 días (justo antes del límite)"""
        hace_364_dias = date.today() - timedelta(days=364)
        fecha = FechaCreacion(hace_364_dias)
        
        assert fecha.es_de_hoy() == False
        assert fecha.es_reciente() == False  
        assert fecha.es_antigua() == False  
        assert fecha.meses_desde_creacion() == 12 
    
    def test_cuenta_muy_antigua(self):
        """Test cuenta muy antigua (más de 2 años)"""
        muy_antigua = date.today() - timedelta(days=800)
        fecha = FechaCreacion(muy_antigua)
        
        assert fecha.es_antigua() == True
        assert fecha.es_reciente() == False
        assert fecha.meses_desde_creacion() >= 24
    
    def test_clasificacion_por_antiguedad_personalizada(self):
        """Test clasificación personalizada por antigüedad"""
        hace_30_dias = date.today() - timedelta(days=30)
        fecha = FechaCreacion(hace_30_dias)
        
        assert fecha.es_antigua() == False
        assert fecha.es_antigua(30) == True
        assert fecha.es_antigua(20) == True
        assert fecha.es_reciente(45) == True