import pytest
from app.cuentas.domain.value_objects.ubicacion import Ubicacion, UbicacionesPredefinidas


class TestUbicacionCreacion:
    """Tests para creación de ubicaciones"""
    
    def test_crear_ubicacion_basica(self):
        """Test crear ubicación básica"""
        ubicacion = Ubicacion(
            codigo="SOGAMOSO",
            nombre_completo="Organismo de Tránsito de Sogamoso",
            municipio="Sogamoso",
            departamento="Boyacá"
        )
        assert ubicacion.codigo == "SOGAMOSO"
        assert ubicacion.municipio == "Sogamoso"
        assert ubicacion.departamento == "Boyacá"
    
    def test_crear_ubicacion_con_contacto(self):
        """Test crear ubicación con información de contacto"""
        ubicacion = Ubicacion(
            codigo="MEDELLIN",
            nombre_completo="Secretaría de Movilidad de Medellín",
            municipio="Medellín", 
            departamento="Antioquia",
            direccion="Carrera 55 # 42-180",
            telefono="604-385-5555"
        )
        assert ubicacion.tiene_contacto_completo() == True
        assert ubicacion.direccion == "Carrera 55 # 42-180"
    
    def test_normalizacion_codigo(self):
        """Test normalización de código"""
        ubicacion = Ubicacion(
            codigo="bogota dc",
            nombre_completo="Secretaría de Movilidad",
            municipio="Bogotá",
            departamento="Cundinamarca"
        )
        assert ubicacion.codigo == "BOGOTA_DC"
    
    def test_validaciones_campos_obligatorios(self):
        """Test validaciones de campos obligatorios"""
        with pytest.raises(ValueError, match="código.*no puede estar vacío"):
            Ubicacion("", "Nombre", "Municipio", "Departamento")
        
        with pytest.raises(ValueError, match="nombre completo.*no puede estar vacío"):
            Ubicacion("CODIGO", "", "Municipio", "Departamento")


class TestUbicacionMetodos:
    """Tests para métodos de ubicación"""
    
    def test_get_nombre_corto(self):
        """Test obtener nombre corto"""
        ubicacion = UbicacionesPredefinidas.SOGAMOSO
        assert ubicacion.get_nombre_corto() == "Sogamoso"
    
    def test_get_descripcion_completa(self):
        """Test descripción completa"""
        ubicacion = UbicacionesPredefinidas.SOGAMOSO
        assert ubicacion.get_descripcion_completa() == "Sogamoso - Boyacá"
    
    def test_get_ubicacion_display(self):
        """Test formato para display"""
        ubicacion = UbicacionesPredefinidas.SOGAMOSO
        expected = "Sogamoso (Sogamoso - Boyacá)"
        assert ubicacion.get_ubicacion_display() == expected
    
    def test_es_mismo_departamento(self):
        """Test verificar mismo departamento"""
        sogamoso = UbicacionesPredefinidas.SOGAMOSO
        funza = UbicacionesPredefinidas.FUNZA
        medellin = UbicacionesPredefinidas.MEDELLIN
        
        # Funza está en Cundinamarca, Sogamoso en Boyacá
        assert sogamoso.es_mismo_departamento(funza) == False
        assert sogamoso.es_mismo_departamento(medellin) == False


class TestUbicacionFactoryMethods:
    """Tests para factory methods"""
    
    def test_crear_desde_web_scraping(self):
        """Test crear desde datos de web scraping"""
        datos = {
            'nombre': 'DIR DPTAL TTOyTTE CASANARE/AGUAZUL',
            'direccion': 'DirecciónCARRERA 21 # 14-23 PISO 2',
            'municipio': 'AGUAZUL - CASANARE',
            'departamento': 'CASANARE',
            'telefono': 'Teléfono6384900'
        }
        
        ubicacion = Ubicacion.crear_desde_web_scraping(datos)
        assert ubicacion.municipio == "AGUAZUL"
        assert ubicacion.departamento == "CASANARE"
        assert ubicacion.direccion == "CARRERA 21 # 14-23 PISO 2"
        assert ubicacion.telefono == "6384900"
    
    def test_crear_basica(self):
        """Test factory method crear básica"""
        ubicacion = Ubicacion.crear_basica("TUNJA", "Tunja", "Boyacá")
        assert ubicacion.codigo == "TUNJA"
        assert ubicacion.municipio == "Tunja"
        assert ubicacion.nombre_completo == "Organismo de Tránsito de Tunja"


class TestUbicacionesPredefinidas:
    """Tests para ubicaciones predefinidas"""
    
    def test_obtener_todas(self):
        """Test obtener todas las ubicaciones"""
        ubicaciones = UbicacionesPredefinidas.obtener_todas()
        assert len(ubicaciones) == 7
        codigos = [ub.codigo for ub in ubicaciones]
        assert "SOGAMOSO" in codigos
        assert "MEDELLIN" in codigos
        assert "BOGOTA_DC" in codigos
    
    def test_obtener_por_codigo(self):
        """Test buscar por código"""
        ubicacion = UbicacionesPredefinidas.obtener_por_codigo("SOGAMOSO")
        assert ubicacion is not None
        assert ubicacion.municipio == "Sogamoso"
        
        # Test código no encontrado
        no_existe = UbicacionesPredefinidas.obtener_por_codigo("NO_EXISTE")
        assert no_existe is None
    
    def test_obtener_por_municipio(self):
        """Test buscar por municipio"""
        ubicaciones = UbicacionesPredefinidas.obtener_por_municipio("Medellín")
        assert len(ubicaciones) == 1
        assert ubicaciones[0].codigo == "MEDELLIN"