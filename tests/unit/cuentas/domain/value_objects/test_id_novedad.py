import pytest
from datetime import date, datetime, timedelta
from app.cuentas.domain.value_objects.id_novedad import IdentificadorNovedad, ReporteNovedad


class TestIdentificadorNovedadCreacion:
    """Tests para creación de identificadores"""
    def test_generar_para_hoy(self):
        """Test generar identificador para hoy"""
        identificador = IdentificadorNovedad.generar_para_hoy(1)
        assert identificador.es_de_hoy() == True
        assert identificador.consecutivo == 1
        assert identificador.codigo.startswith("NOV-")
    
    def test_generar_para_fecha(self):
        """Test generar para fecha específica"""
        fecha = date(2024, 12, 4)
        identificador = IdentificadorNovedad.generar_para_fecha(fecha, 5)
        assert identificador.fecha_creacion == fecha
        assert identificador.consecutivo == 5
        assert identificador.codigo == "NOV-20241204-0005"
    
    def test_formato_codigo_valido(self):
        """Test que el formato del código es correcto"""
        identificador = IdentificadorNovedad.generar_para_hoy(123)
        assert identificador._es_formato_valido(identificador.codigo) == True
        assert len(identificador.codigo) == 17  # NOV-YYYYMMDD-NNNN
    
    def test_consecutivo_fuera_de_rango(self):
        """Test consecutivo fuera de rango"""
        with pytest.raises(ValueError, match="consecutivo debe estar"):
            IdentificadorNovedad.generar_para_hoy(0)
        
        with pytest.raises(ValueError, match="consecutivo debe estar"):
            IdentificadorNovedad.generar_para_hoy(10000)


class TestIdentificadorNovedadMetodos:
    """Tests para métodos del identificador"""
    
    def test_get_fecha_string(self):
        """Test obtener fecha como string"""
        fecha = date(2024, 12, 4)
        identificador = IdentificadorNovedad.generar_para_fecha(fecha, 1)
        assert identificador.get_fecha_string() == "20241204"
    
    def test_get_componentes_fecha(self):
        """Test obtener componentes de fecha"""
        fecha = date(2024, 12, 4)
        identificador = IdentificadorNovedad.generar_para_fecha(fecha, 1)
        assert identificador.get_year() == 2024
        assert identificador.get_month() == 12
        assert identificador.get_day() == 4
    
    def test_es_de_fecha(self):
        """Test verificar si es de fecha específica"""
        fecha = date(2024, 12, 4)
        identificador = IdentificadorNovedad.generar_para_fecha(fecha, 1)
        assert identificador.es_de_fecha(fecha) == True
        assert identificador.es_de_fecha(date.today()) == (fecha == date.today())
    
    def test_dias_desde_creacion(self):
        """Test calcular días desde creación"""
        ayer = date.today() - timedelta(days=1)
        identificador = IdentificadorNovedad.generar_para_fecha(ayer, 1)
        assert identificador.dias_desde_creacion() == 1
    
    def test_formato_display(self):
        """Test formato para display"""
        fecha = date(2024, 12, 4)
        identificador = IdentificadorNovedad.generar_para_fecha(fecha, 42)
        assert identificador.formato_display() == "NOV-2024/12/04-0042"
    
    def test_formato_corto(self):
        """Test formato corto"""
        fecha = date(2024, 12, 4)
        identificador = IdentificadorNovedad.generar_para_fecha(fecha, 7)
        assert identificador.formato_corto() == "NOV-1204-0007"


class TestIdentificadorNovedadFactoryMethods:
    """Tests para factory methods"""
    
    def test_crear_desde_codigo(self):
        """Test crear desde código existente"""
        codigo = "NOV-20241204-0015"
        identificador = IdentificadorNovedad.crear_desde_codigo(codigo)
        assert identificador.codigo == codigo
        assert identificador.fecha_creacion == date(2024, 12, 4)
        assert identificador.consecutivo == 15
    
    def test_crear_desde_codigo_invalido(self):
        """Test crear desde código inválido"""
        with pytest.raises(ValueError, match="Formato.*inválido"):
            IdentificadorNovedad.crear_desde_codigo("CODIGO_MALO")
    
    def test_crear_si_valido_exitoso(self):
        """Test crear si válido exitoso"""
        codigo = "NOV-20241204-0001"
        identificador = IdentificadorNovedad.crear_si_valido(codigo)
        assert identificador is not None
        assert identificador.codigo == codigo
    
    def test_crear_si_valido_fallido(self):
        """Test crear si válido fallido"""
        identificador = IdentificadorNovedad.crear_si_valido("CODIGO_MALO")
        assert identificador is None
    
    def test_proximo_consecutivo_sin_existentes(self):
        """Test próximo consecutivo sin existentes"""
        proximo = IdentificadorNovedad.proximo_consecutivo_para_hoy([])
        assert proximo == 1
    
    def test_proximo_consecutivo_con_existentes(self):
        """Test próximo consecutivo con existentes"""
        hoy = date.today()
        existentes = [
            IdentificadorNovedad.generar_para_fecha(hoy, 1),
            IdentificadorNovedad.generar_para_fecha(hoy, 3),
            IdentificadorNovedad.generar_para_fecha(hoy, 2),
        ]
        
        proximo = IdentificadorNovedad.proximo_consecutivo_para_hoy(existentes)
        assert proximo == 4


class TestReporteNovedadCreacion:
    """Tests para creación de reportes"""
    
    def test_crear_nuevo_reporte(self):
        """Test crear nuevo reporte"""
        reporte = ReporteNovedad.crear_nuevo("LMURCIA001", "Documento faltante", 1)
        assert reporte.funcionario_reporta == "LMURCIA001"
        assert reporte.descripcion_corta == "Documento faltante"
        assert reporte.identificador.consecutivo == 1
    
    def test_crear_desde_existente(self):
        """Test crear desde identificador existente"""
        identificador = IdentificadorNovedad.generar_para_hoy(5)
        timestamp = datetime.now()
        
        reporte = ReporteNovedad.crear_desde_existente(
            identificador, "AGARCIA002", "Datos incorrectos", timestamp
        )
        assert reporte.identificador == identificador
        assert reporte.funcionario_reporta == "AGARCIA002"
        assert reporte.timestamp_reporte == timestamp
    
    def test_validaciones_reporte(self):
        """Test validaciones del reporte"""
        identificador = IdentificadorNovedad.generar_para_hoy(1)
        
        with pytest.raises(ValueError, match="funcionario.*no puede estar vacío"):
            ReporteNovedad(identificador, "", datetime.now(), "Descripción")
        
        with pytest.raises(ValueError, match="descripción.*no puede estar vacía"):
            ReporteNovedad(identificador, "FUNC001", datetime.now(), "")
        
        descripcion_larga = "X" * 201
        with pytest.raises(ValueError, match="no puede exceder 200 caracteres"):
            ReporteNovedad(identificador, "FUNC001", datetime.now(), descripcion_larga)


class TestReporteNovedadMetodos:
    """Tests para métodos del reporte"""
    
    def test_get_fecha_reporte(self):
        """Test obtener fecha del reporte"""
        timestamp = datetime(2024, 12, 4, 14, 30, 0)
        identificador = IdentificadorNovedad.generar_para_hoy(1)
        reporte = ReporteNovedad.crear_desde_existente(
            identificador, "FUNC001", "Test", timestamp
        )
        assert reporte.get_fecha_reporte() == date(2024, 12, 4)
    
    def test_get_hora_reporte(self):
        """Test obtener hora del reporte"""
        timestamp = datetime(2024, 12, 4, 14, 30, 0)
        identificador = IdentificadorNovedad.generar_para_hoy(1)
        reporte = ReporteNovedad.crear_desde_existente(
            identificador, "FUNC001", "Test", timestamp
        )
        assert reporte.get_hora_reporte() == "14:30"
    
    def test_get_timestamp_display(self):
        """Test formato de timestamp"""
        timestamp = datetime(2024, 12, 4, 14, 30, 0)
        identificador = IdentificadorNovedad.generar_para_hoy(1)
        reporte = ReporteNovedad.crear_desde_existente(
            identificador, "FUNC001", "Test", timestamp
        )
        assert reporte.get_timestamp_display() == "04/12/2024 14:30"
    
    def test_es_reporte_reciente(self):
        """Test verificar si es reporte reciente"""
        ahora = datetime.now()
        hace_1_hora = ahora - timedelta(hours=1)
        hace_2_dias = ahora - timedelta(days=2)
        
        identificador = IdentificadorNovedad.generar_para_hoy(1)
        
        reporte_reciente = ReporteNovedad.crear_desde_existente(
            identificador, "FUNC001", "Test", hace_1_hora
        )
        reporte_antiguo = ReporteNovedad.crear_desde_existente(
            identificador, "FUNC001", "Test", hace_2_dias
        )
        
        assert reporte_reciente.es_reporte_reciente(24) == True
        assert reporte_antiguo.es_reporte_reciente(24) == False
    
    def test_get_codigo_novedad(self):
        """Test obtener código de novedad"""
        reporte = ReporteNovedad.crear_nuevo("FUNC001", "Test", 42)
        codigo = reporte.get_codigo_novedad()
        assert codigo.startswith("NOV-")
        assert "0042" in codigo
    
    def test_get_info_completa(self):
        """Test información completa"""
        timestamp = datetime(2024, 12, 4, 14, 30, 0)
        identificador = IdentificadorNovedad.generar_para_fecha(date(2024, 12, 4), 1)
        reporte = ReporteNovedad.crear_desde_existente(
            identificador, "LMURCIA001", "Test", timestamp
        )
        
        info = reporte.get_info_completa()
        assert "NOV-20241204-0001" in info
        assert "LMURCIA001" in info
        assert "04/12/2024 14:30" in info