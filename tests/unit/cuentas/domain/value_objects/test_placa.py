import pytest
from app.cuentas.domain.value_objects.placa import Placa


class TestPlacaCreacionBasica:
    """Tests básicos de creación de placas"""
    
    def test_crear_placa_carro_simple(self):
        """Test crear placa de carro básica"""
        placa = Placa("ABC123")
        assert placa.valor == "ABC123"
        assert placa.get_tipo_vehiculo() == "CARRO"
        assert placa.es_carro() == True
    
    def test_crear_placa_moto_con_letra(self):
        """Test crear placa de moto con letra final"""
        placa = Placa("ABC12F")
        assert placa.valor == "ABC12F"
        assert placa.get_tipo_vehiculo() == "MOTO"
        assert placa.es_moto() == True
    
    def test_crear_placa_moto_sin_letra(self):
        """Test crear placa de moto sin letra final"""
        placa = Placa("ABC12")
        assert placa.valor == "ABC12"
        assert placa.get_tipo_vehiculo() == "MOTO"
        assert placa.es_moto() == True
    
    def test_crear_placa_motocarro(self):
        """Test crear placa de motocarro"""
        placa = Placa("123ABC")
        assert placa.valor == "123ABC"
        assert placa.get_tipo_vehiculo() == "MOTOCARRO"
        assert placa.es_motocarro() == True


class TestPlacaNormalizacion:
    """Tests de normalización de entrada"""
    
    def test_normalizar_espacios_carro(self):
        """Test normalización de espacios en carro"""
        placa = Placa(" ABC 123 ")
        assert placa.valor == "ABC123"
        assert placa.es_carro() == True
    
    def test_normalizar_minusculas(self):
        """Test normalización de minúsculas"""
        placa = Placa("abc123")
        assert placa.valor == "ABC123"
        assert placa.es_carro() == True
    
    def test_normalizar_mixto(self):
        """Test normalización mixta"""
        placa = Placa("  aBc 12 F  ")
        assert placa.valor == "ABC12F"
        assert placa.es_moto() == True
    
    def test_normalizar_multiples_espacios(self):
        """Test normalización múltiples espacios"""
        placa = Placa("  ABC    123  ")
        assert placa.valor == "ABC123"
        assert placa.es_carro() == True


class TestPlacaValidacionCaracteres:
    """Tests de validación de caracteres especiales"""
    
    def test_rechazar_eñe(self):
        """Test rechazar letra Ñ"""
        with pytest.raises(ValueError, match="letras no válidas"):
            Placa("AÑC123")
    
    def test_rechazar_acentos(self):
        """Test rechazar acentos"""
        with pytest.raises(ValueError, match="letras no válidas"):
            Placa("ÁBC123")
    
    def test_rechazar_diéresis(self):
        """Test rechazar diéresis"""
        with pytest.raises(ValueError, match="letras no válidas"):
            Placa("AÜC123")
    
    def test_rechazar_cedilla(self):
        """Test rechazar cedilla"""
        with pytest.raises(ValueError, match="letras no válidas"):
            Placa("AÇC123")
    
    def test_rechazar_simbolos(self):
        """Test rechazar símbolos"""
        simbolos = ["@", "#", "$", "%", "&", "*", "(", ")", "-", "_", "=", "+"]
        for simbolo in simbolos:
            with pytest.raises(ValueError, match="letras no válidas"):
                Placa(f"ABC{simbolo}123")


class TestPlacaValidacionFormato:
    """Tests de validación de formato"""
    
    def test_rechazar_formato_invalido(self):
        """Test rechazar formatos inválidos"""
        formatos_invalidos = [
            "AB123",      # Solo 2 letras
            "ABCD123",    # 4 letras
            "ABC1234",    # 4 dígitos
            "ABC1",       # Solo 1 dígito
            "ABC12GH",    # Demasiadas letras al final
            "12AB34",     # Formato híbrido
        ]
        
        for formato in formatos_invalidos:
            with pytest.raises(ValueError, match="Formato de placa inválido"):
                Placa(formato)
    
    def test_rechazar_placa_vacia(self):
        """Test rechazar placa vacía"""
        with pytest.raises(ValueError, match="no puede estar vacía"):
            Placa("")
    
    def test_rechazar_placa_none(self):
        """Test rechazar placa None"""
        with pytest.raises(ValueError, match="no puede estar vacía"):
            Placa(None)
    
    def test_rechazar_solo_espacios(self):
        """Test rechazar solo espacios"""
        with pytest.raises(ValueError, match="no puede estar vacía"):
            Placa("   ")


class TestPlacaFactoryMethods:
    """Tests de factory methods"""
    
    def test_crear_desde_string_valida(self):
        """Test crear desde string válida"""
        placa = Placa.crear_desde_string("ABC123")
        assert placa.valor == "ABC123"
        assert placa.es_carro() == True
    
    def test_crear_desde_string_invalida(self):
        """Test crear desde string inválida"""
        with pytest.raises(ValueError):
            Placa.crear_desde_string("INVALIDA")
    
    def test_crear_si_valida_exitosa(self):
        """Test crear si válida con entrada correcta"""
        placa = Placa.crear_si_valida("ABC123")
        assert placa is not None
        assert placa.valor == "ABC123"
    
    def test_crear_si_valida_fallida(self):
        """Test crear si válida con entrada incorrecta"""
        placa = Placa.crear_si_valida("INVALIDA")
        assert placa is None


class TestPlacaInmutabilidad:
    """Tests de inmutabilidad"""
    
    def test_placa_es_inmutable(self):
        """Test que placa no se puede modificar"""
        placa = Placa("ABC123")
        
        with pytest.raises(AttributeError):
            placa.valor = "XYZ789"
    
    def test_placa_hasheable(self):
        """Test que placa es hasheable"""
        placa = Placa("ABC123")
        conjunto = {placa}
        assert len(conjunto) == 1
        assert placa in conjunto


class TestPlacaMetodos:
    """Tests de métodos de la clase"""
    
    def test_str_representation(self):
        """Test representación string"""
        placa = Placa("ABC123")
        assert str(placa) == "ABC123"
    
    def test_repr_representation(self):
        """Test representación repr"""
        placa = Placa("ABC123")
        expected = "Placa('ABC123', tipo=CARRO)"
        assert repr(placa) == expected
    
    def test_equality(self):
        """Test igualdad entre placas"""
        placa1 = Placa("ABC123")
        placa2 = Placa("abc 123")
        assert placa1 == placa2


class TestPlacaCasosReales:
    """Tests con casos reales colombianos"""
    
    def test_placas_carros_reales(self):
        """Test placas de carros reales"""
        placas_carros = [
            "ABC123", "XYZ999", "DEF001", "GHI456",
            "JKL789", "MNO012", "PQR345", "STU678"
        ]
        
        for placa_str in placas_carros:
            placa = Placa(placa_str)
            assert placa.es_carro() == True
            assert placa.es_moto() == False
            assert placa.es_motocarro() == False
    
    def test_placas_motos_reales(self):
        """Test placas de motos reales"""
        placas_motos = [
            "ABC12F", "XYZ34G", "DEF56H", "GHI78J",
            "ABC12", "XYZ34", "DEF56", "GHI78"
        ]
        
        for placa_str in placas_motos:
            placa = Placa(placa_str)
            assert placa.es_moto() == True
            assert placa.es_carro() == False
            assert placa.es_motocarro() == False
    
    def test_placas_motocarros_reales(self):
        """Test placas de motocarros reales"""
        placas_motocarros = [
            "123ABC", "456XYZ", "789DEF", "012GHI",
            "345JKL", "678MNO", "901PQR", "234STU"
        ]
        
        for placa_str in placas_motocarros:
            placa = Placa(placa_str)
            assert placa.es_motocarro() == True
            assert placa.es_carro() == False
            assert placa.es_moto() == False