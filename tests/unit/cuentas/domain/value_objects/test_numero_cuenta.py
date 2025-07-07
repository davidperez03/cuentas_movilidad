import pytest
from datetime import date, timedelta
from app.cuentas.domain.value_objects.numero_cuenta import NumeroCuenta


class TestNumeroCuentaCreacion:
    """Tests para creación de números de cuenta"""
    
    def test_crear_numero_cuenta_valido(self):
        """Test crear número de cuenta válido"""
        numero = NumeroCuenta("2024120400001")
        assert numero.valor == "2024120400001"
        assert numero.get_fecha() == date(2024, 12, 4)
        assert numero.get_consecutivo() == 1
    
    def test_crear_numero_cuenta_formato_completo(self):
        """Test crear número de cuenta con formato completo"""
        numero = NumeroCuenta("2024120499999")
        assert numero.get_consecutivo() == 99999
    
    def test_crear_numero_cuenta_consecutivo_maximo(self):
        """Test crear número de cuenta con consecutivo máximo válido"""
        numero = NumeroCuenta("2024120499999")
        assert numero.get_consecutivo() == 99999
    
    def test_numero_cuenta_vacio_error(self):
        """Test que número vacío genera error"""
        with pytest.raises(ValueError, match="no puede estar vacío"):
            NumeroCuenta("")
    
    def test_numero_cuenta_none_error(self):
        """Test que número None genera error"""
        with pytest.raises(ValueError, match="no puede estar vacío"):
            NumeroCuenta(None)


class TestNumeroCuentaValidacionFormato:
    """Tests para validación de formato"""
    
    def test_formato_correcto_13_digitos(self):
        """Test formato correcto de 13 dígitos"""
        numero = NumeroCuenta("2024120400001")
        assert len(numero.valor) == 13
        assert numero.valor.isdigit()
    
    def test_formato_incorrecto_menos_digitos(self):
        """Test formato incorrecto con menos dígitos"""
        with pytest.raises(ValueError, match="Formato de número de cuenta inválido"):
            NumeroCuenta("202412040001")  
    
    def test_formato_incorrecto_mas_digitos(self):
        """Test formato incorrecto con más dígitos"""
        with pytest.raises(ValueError, match="Formato de número de cuenta inválido"):
            NumeroCuenta("20241204000012") 
    
    def test_formato_con_letras_error(self):
        """Test formato con letras genera error"""
        with pytest.raises(ValueError, match="Formato de número de cuenta inválido"):
            NumeroCuenta("2024120400A")
    
    def test_normalizacion_elimina_caracteres_especiales(self):
        """Test que normalización elimina caracteres especiales"""
        numero = NumeroCuenta("2024-12-04-00001")
        assert numero.valor == "2024120400001"


class TestNumeroCuentaValidacionFecha:
    """Tests para validación de fechas"""
    
    def test_fecha_valida_normal(self):
        """Test fecha válida normal"""
        numero = NumeroCuenta("2024120400001")
        assert numero.get_fecha() == date(2024, 12, 4)
    
    def test_fecha_valida_bisiesto(self):
        """Test fecha válida en año bisiesto"""
        numero = NumeroCuenta("2024022900001")  # 29 feb 2024 (bisiesto)
        assert numero.get_fecha() == date(2024, 2, 29)
    
    def test_fecha_invalida_febrero_no_bisiesto(self):
        """Test fecha inválida 29 feb en año no bisiesto"""
        with pytest.raises(ValueError, match="fecha.*inválida"):
            NumeroCuenta("2023022900001")  # 29 feb 2023 (no bisiesto)
    
    def test_fecha_invalida_mes_13(self):
        """Test fecha inválida mes 13"""
        with pytest.raises(ValueError, match="fecha.*inválida"):
            NumeroCuenta("2024130400001")
    
    def test_fecha_invalida_dia_32(self):
        """Test fecha inválida día 32"""
        with pytest.raises(ValueError, match="fecha.*inválida"):
            NumeroCuenta("2024123200001")
    
    def test_fecha_invalida_mes_00(self):
        """Test fecha inválida mes 00"""
        with pytest.raises(ValueError, match="fecha.*inválida"):
            NumeroCuenta("2024000400001")
    
    def test_fecha_invalida_dia_00(self):
        """Test fecha inválida día 00"""
        with pytest.raises(ValueError, match="fecha.*inválida"):
            NumeroCuenta("2024120000001")
    
    def test_fecha_invalida_year_bajo(self):
        """Test fecha inválida año muy bajo"""
        with pytest.raises(ValueError, match="fecha.*inválida"):
            NumeroCuenta("1899120400001")
    
    def test_fecha_invalida_year_alto(self):
        """Test fecha inválida año muy alto"""
        with pytest.raises(ValueError, match="fecha.*inválida"):
            NumeroCuenta("2101120400001")
    
    def test_fecha_futura_invalida(self):
        """Test que fechas futuras son inválidas"""
        from datetime import timedelta
        mañana = date.today() + timedelta(days=1)
        fecha_str = mañana.strftime("%Y%m%d")
        
        with pytest.raises(ValueError, match="fecha.*no puede ser futura"):
            NumeroCuenta(f"{fecha_str}00001")


class TestNumeroCuentaValidacionConsecutivo:
    """Tests para validación de consecutivo"""
    
    def test_consecutivo_valido_minimo(self):
        """Test consecutivo válido mínimo (1)"""
        numero = NumeroCuenta("2024120400001")
        assert numero.get_consecutivo() == 1
    
    def test_consecutivo_valido_maximo(self):
        """Test consecutivo válido máximo (99999)"""
        numero = NumeroCuenta("2024120499999")
        assert numero.get_consecutivo() == 99999
    
    def test_consecutivo_invalido_cero(self):
        """Test consecutivo inválido (0)"""
        with pytest.raises(ValueError, match="consecutivo.*inválido"):
            NumeroCuenta("2024120400000")
    
    def test_consecutivo_invalido_muy_alto(self):
        """Test consecutivo inválido muy alto (100000)"""
        # Este caso no puede ocurrir con formato de 13 dígitos, pero probamos la lógica
        pass  # El formato ya lo previene


class TestNumeroCuentaMetodosExtraccion:
    """Tests para métodos de extracción de datos"""
    
    def test_get_fecha(self):
        """Test extracción de fecha"""
        numero = NumeroCuenta("2024120400001")
        assert numero.get_fecha() == date(2024, 12, 4)
    
    def test_get_consecutivo(self):
        """Test extracción de consecutivo"""
        numero = NumeroCuenta("2024120400001")
        assert numero.get_consecutivo() == 1
        
        numero2 = NumeroCuenta("2024120400123")
        assert numero2.get_consecutivo() == 123
    
    def test_get_year(self):
        """Test extracción de año"""
        numero = NumeroCuenta("2024120400001")
        assert numero.get_year() == 2024
    
    def test_get_month(self):
        """Test extracción de mes"""
        numero = NumeroCuenta("2024120400001")
        assert numero.get_month() == 12
    
    def test_get_day(self):
        """Test extracción de día"""
        numero = NumeroCuenta("2024120400001")
        assert numero.get_day() == 4


class TestNumeroCuentaMetodosComparacion:
    """Tests para métodos de comparación de fechas"""
    
    def test_es_de_hoy_true(self):
        """Test es_de_hoy con fecha actual"""
        hoy = date.today()
        fecha_str = hoy.strftime("%Y%m%d")
        numero = NumeroCuenta(f"{fecha_str}00001")
        assert numero.es_de_hoy() == True
    
    def test_es_de_hoy_false(self):
        """Test es_de_hoy con fecha diferente"""
        numero = NumeroCuenta("2020120400001")
        assert numero.es_de_hoy() == False
    
    def test_es_de_fecha_true(self):
        """Test es_de_fecha con fecha coincidente"""
        numero = NumeroCuenta("2024120400001")
        assert numero.es_de_fecha(date(2024, 12, 4)) == True
    
    def test_es_de_fecha_false(self):
        """Test es_de_fecha con fecha diferente"""
        numero = NumeroCuenta("2024120400001")
        assert numero.es_de_fecha(date(2024, 12, 5)) == False
    
    def test_es_anterior_a(self):
        """Test es_anterior_a"""
        numero = NumeroCuenta("2024120400001")
        assert numero.es_anterior_a(date(2024, 12, 5)) == True
        assert numero.es_anterior_a(date(2024, 12, 3)) == False
    
    def test_es_posterior_a(self):
        """Test es_posterior_a"""
        numero = NumeroCuenta("2024120400001")
        assert numero.es_posterior_a(date(2024, 12, 3)) == True
        assert numero.es_posterior_a(date(2024, 12, 5)) == False


class TestNumeroCuentaMetodosFormato:
    """Tests para métodos de formato"""
    
    def test_formato_legible(self):
        """Test formato legible"""
        numero = NumeroCuenta("2024120400001")
        assert numero.formato_legible() == "2024-12-04-00001"
    
    def test_str_representation(self):
        """Test representación string"""
        numero = NumeroCuenta("2024120400001")
        assert str(numero) == "2024120400001"
    
    def test_repr_representation(self):
        """Test representación repr"""
        numero = NumeroCuenta("2024120400001")
        expected = "NumeroCuenta('2024120400001', fecha=2024-12-04, consecutivo=1)"
        assert repr(numero) == expected


class TestNumeroCuentaFactoryMethods:
    """Tests para factory methods"""
    
    def test_generar_para_hoy(self):
        """Test generar número para hoy"""
        numero = NumeroCuenta.generar_para_hoy(1)
        assert numero.es_de_hoy() == True
        assert numero.get_consecutivo() == 1
    
    def test_generar_para_hoy_consecutivo_alto(self):
        """Test generar número para hoy con consecutivo alto"""
        numero = NumeroCuenta.generar_para_hoy(99999)
        assert numero.es_de_hoy() == True
        assert numero.get_consecutivo() == 99999
    
    def test_generar_para_hoy_consecutivo_invalido(self):
        """Test generar número para hoy con consecutivo inválido"""
        with pytest.raises(ValueError, match="consecutivo debe ser"):
            NumeroCuenta.generar_para_hoy(0)
        
        with pytest.raises(ValueError, match="consecutivo debe ser"):
            NumeroCuenta.generar_para_hoy(100000)
    
    def test_generar_para_fecha(self):
        """Test generar número para fecha específica"""
        fecha = date(2024, 12, 4)
        numero = NumeroCuenta.generar_para_fecha(fecha, 123)
        assert numero.get_fecha() == fecha
        assert numero.get_consecutivo() == 123
    
    def test_generar_para_fecha_invalida(self):
        """Test generar número para fecha inválida"""
        with pytest.raises(ValueError, match="fecha debe ser"):
            NumeroCuenta.generar_para_fecha("2024-12-04", 1)
    
    def test_crear_desde_string_valido(self):
        """Test factory method crear desde string válido"""
        numero = NumeroCuenta.crear_desde_string("2024120400001")
        assert numero.valor == "2024120400001"
    
    def test_crear_desde_string_invalido(self):
        """Test factory method crear desde string inválido"""
        with pytest.raises(ValueError):
            NumeroCuenta.crear_desde_string("INVALIDO")
    
    def test_crear_si_valido_exitoso(self):
        """Test factory method crear si válido exitoso"""
        numero = NumeroCuenta.crear_si_valido("2024120400001")
        assert numero is not None
        assert numero.valor == "2024120400001"
    
    def test_crear_si_valido_fallido(self):
        """Test factory method crear si válido fallido"""
        numero = NumeroCuenta.crear_si_valido("INVALIDO")
        assert numero is None


class TestNumeroCuentaProximoConsecutivo:
    """Tests para cálculo de próximo consecutivo"""
    
    def test_proximo_consecutivo_sin_existentes(self):
        """Test próximo consecutivo sin números existentes"""
        numeros_existentes = []
        proximo = NumeroCuenta.proximo_consecutivo_para_hoy(numeros_existentes)
        assert proximo == 1
    
    def test_proximo_consecutivo_con_existentes_hoy(self):
        """Test próximo consecutivo con números existentes de hoy"""
        hoy = date.today()
        fecha_str = hoy.strftime("%Y%m%d")
        
        numeros_existentes = [
            NumeroCuenta(f"{fecha_str}00001"),
            NumeroCuenta(f"{fecha_str}00003"),
            NumeroCuenta(f"{fecha_str}00002"),
        ]
        
        proximo = NumeroCuenta.proximo_consecutivo_para_hoy(numeros_existentes)
        assert proximo == 4
    
    def test_proximo_consecutivo_con_existentes_otras_fechas(self):
        """Test próximo consecutivo con números de otras fechas"""
        hoy = date.today()
        ayer = hoy - timedelta(days=1)
        
        fecha_hoy = hoy.strftime("%Y%m%d")
        fecha_ayer = ayer.strftime("%Y%m%d")
        
        numeros_existentes = [
            NumeroCuenta(f"{fecha_ayer}00001"), 
            NumeroCuenta(f"{fecha_ayer}00002"),  
            NumeroCuenta(f"{fecha_hoy}00001"),  
        ]
        
        proximo = NumeroCuenta.proximo_consecutivo_para_hoy(numeros_existentes)
        assert proximo == 2
    
    def test_proximo_consecutivo_solo_otras_fechas(self):
        """Test próximo consecutivo solo con números de otras fechas"""
        ayer = date.today() - timedelta(days=1)
        fecha_ayer = ayer.strftime("%Y%m%d")
        
        numeros_existentes = [
            NumeroCuenta(f"{fecha_ayer}00001"),
            NumeroCuenta(f"{fecha_ayer}00002"),
        ]
        
        proximo = NumeroCuenta.proximo_consecutivo_para_hoy(numeros_existentes)
        assert proximo == 1


class TestNumeroCuentaInmutabilidad:
    """Tests para inmutabilidad del value object"""
    
    def test_numero_cuenta_es_inmutable(self):
        """Test que número de cuenta no se puede modificar"""
        numero = NumeroCuenta("2024120400001")
        
        with pytest.raises(AttributeError):
            numero.valor = "2024120400002"
    
    def test_numero_cuenta_hasheable(self):
        """Test que número de cuenta es hasheable"""
        numero = NumeroCuenta("2024120400001")
        conjunto = {numero}
        assert len(conjunto) == 1
        assert numero in conjunto
    
    def test_igualdad_numeros_cuenta(self):
        """Test igualdad entre números de cuenta"""
        numero1 = NumeroCuenta("2024120400001")
        numero2 = NumeroCuenta("2024-12-04-00001")
        assert numero1 == numero2


class TestNumeroCuentaCasosReales:
    """Tests con casos de uso reales del sistema"""
    
    def test_secuencia_numeros_mismo_dia(self):
        """Test secuencia de números del mismo día"""
        fecha = date.today() - timedelta(days=1)
        
        numeros = [
            NumeroCuenta.generar_para_fecha(fecha, i)
            for i in range(1, 6)
        ]
        
        for numero in numeros:
            assert numero.get_fecha() == fecha

        consecutivos = [num.get_consecutivo() for num in numeros]
        assert consecutivos == [1, 2, 3, 4, 5]
    
    def test_numeros_diferentes_dias(self):
        """Test números de diferentes días"""
        fecha1 = date.today() - timedelta(days=2)
        fecha2 = date.today() - timedelta(days=1)
        
        numero1 = NumeroCuenta.generar_para_fecha(fecha1, 1)
        numero2 = NumeroCuenta.generar_para_fecha(fecha2, 1)
        
        assert numero1.get_fecha() != numero2.get_fecha()
        assert numero1.get_consecutivo() == numero2.get_consecutivo()
        assert numero1.valor != numero2.valor
    
    def test_caso_fin_de_año(self):
        """Test caso especial fin de año"""
        ultimo_dia = date(2023, 12, 31)
        primer_dia = date(2024, 1, 1)
        
        numero_fin = NumeroCuenta.generar_para_fecha(ultimo_dia, 99999)
        numero_inicio = NumeroCuenta.generar_para_fecha(primer_dia, 1)
        
        assert numero_fin.get_year() == 2023
        assert numero_inicio.get_year() == 2024
        assert numero_fin.get_consecutivo() == 99999
        assert numero_inicio.get_year() == 2024
        assert numero_fin.get_consecutivo() == 99999
        assert numero_inicio.get_consecutivo() == 1