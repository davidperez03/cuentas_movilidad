import pytest
from app.cuentas.domain.value_objects.enums.tipo_servicio import TipoServicio
from app.cuentas.domain.value_objects.enums.estado_cuenta import EstadoCuenta
from app.cuentas.domain.value_objects.enums.novedades.tipo_novedad import TipoNovedad


class TestTipoServicio:
    """Tests unitarios para TipoServicio"""
    
    def test_valores_enum_correctos(self):
        """Verificar que los valores del enum son correctos"""
        assert TipoServicio.PARTICULAR.value == "particular"
        assert TipoServicio.OFICIAL.value == "oficial"
        assert TipoServicio.ESPECIAL.value == "especial"
        assert TipoServicio.SERVICIO_PUBLICO.value == "servicio_publico"
    
    def test_enum_es_inmutable(self):
        """Verificar que los valores del enum no se pueden cambiar"""
        with pytest.raises(AttributeError):
            TipoServicio.PARTICULAR.value = "nuevo_valor"
    
    def test_comparacion_enum_values(self):
        """Test comparación de valores de enum"""
        assert TipoServicio.PARTICULAR == TipoServicio.PARTICULAR
        assert TipoServicio.PARTICULAR != TipoServicio.OFICIAL
    
    def test_enum_en_listas(self):
        """Test uso de enum en listas y sets"""
        tipos_validos = [TipoServicio.PARTICULAR, TipoServicio.OFICIAL]
        assert TipoServicio.PARTICULAR in tipos_validos
        assert TipoServicio.ESPECIAL not in tipos_validos
        
        # Test en sets
        tipos_set = {TipoServicio.PARTICULAR, TipoServicio.OFICIAL}
        assert len(tipos_set) == 2
        assert TipoServicio.PARTICULAR in tipos_set
    
    def test_iteracion_sobre_enum(self):
        """Test iteración sobre todos los valores del enum"""
        valores_esperados = ["particular", "oficial", "especial", "servicio_publico"]
        valores_reales = [tipo.value for tipo in TipoServicio]
        assert valores_reales == valores_esperados
        assert len(list(TipoServicio)) == 4


class TestEstadoCuenta:
    """Tests unitarios para EstadoCuenta"""
    
    def test_valores_enum_correctos(self):
        """Verificar que los valores del enum son correctos"""
        assert EstadoCuenta.ACTIVA.value == "activa"
        assert EstadoCuenta.EN_TRASLADO.value == "en_traslado"
        assert EstadoCuenta.EN_RADICACION.value == "en_radicacion"
        assert EstadoCuenta.INACTIVA.value == "inactiva"
    
    def test_estados_mutuamente_excluyentes(self):
        """Test que estados de proceso son mutuamente excluyentes"""
        # Una cuenta no puede estar en traslado Y radicación simultáneamente
        assert EstadoCuenta.EN_TRASLADO != EstadoCuenta.EN_RADICACION
        
        # Estados activos vs inactivos
        estados_activos = [EstadoCuenta.ACTIVA, EstadoCuenta.EN_TRASLADO, EstadoCuenta.EN_RADICACION]
        for estado in estados_activos:
            assert estado != EstadoCuenta.INACTIVA
    
    def test_logica_negocio_estados_cuenta(self):
        """Test lógica implícita de estados de cuenta"""
        # Estados que indican proceso activo
        estados_en_proceso = [EstadoCuenta.EN_TRASLADO, EstadoCuenta.EN_RADICACION]
        assert len(estados_en_proceso) == 2
        
        # Estados sin proceso activo
        estados_sin_proceso = [EstadoCuenta.ACTIVA, EstadoCuenta.INACTIVA]
        assert len(estados_sin_proceso) == 2
        
        # Verificar que no hay overlap
        todos_estados = estados_en_proceso + estados_sin_proceso
        assert len(set(todos_estados)) == 4  # Sin duplicados


class TestTipoNovedad:
    """Tests unitarios para TipoNovedad"""
    
    def test_valores_enum_correctos(self):
        """Verificar que los valores del enum son correctos"""
        assert TipoNovedad.DOCUMENTO_FALTANTE.value == "documento_faltante"
        assert TipoNovedad.DOCUMENTO_INCORRECTO.value == "documento_incorrecto"
        assert TipoNovedad.INFORMACION_INCONSISTENTE.value == "informacion_inconsistente"
        assert TipoNovedad.OTRO.value == "otro"
    
    def test_tipos_especificos_vehiculos(self):
        """Test tipos específicos relacionados con vehículos"""
        tipos_vehiculos = [
            TipoNovedad.SOAT_VENCIDO,
            TipoNovedad.TECNICOMECANICA_VENCIDA
        ]
        
        for tipo in tipos_vehiculos:
            assert tipo in TipoNovedad
            assert isinstance(tipo.value, str)
    
    def test_tipos_documentales(self):
        """Test tipos relacionados con documentación"""
        tipos_docs = [
            TipoNovedad.DOCUMENTO_FALTANTE,
            TipoNovedad.DOCUMENTO_INCORRECTO,
            TipoNovedad.FIRMA_FALTANTE
        ]
        
        for tipo in tipos_docs:
            assert tipo in TipoNovedad
            assert "documento" in tipo.value or "firma" in tipo.value
    
    def test_tipo_otro_como_fallback(self):
        """Test que OTRO existe como fallback"""
        assert TipoNovedad.OTRO.value == "otro"
        
        # OTRO debería ser el último en una lista ordenada
        todos_tipos = list(TipoNovedad)
        assert TipoNovedad.OTRO in todos_tipos
    
    def test_cobertura_completa_tipos(self):
        """Test que tenemos cobertura completa de tipos de novedad"""
        # Verificar tipos exactos definidos en el enum
        tipos_esperados = [
            "documento_faltante", "documento_incorrecto", 
            "informacion_inconsistente", "firma_faltante",
            "fecha_incorrecta", "datos_propietario_incompletos", 
            "soat_vencido", "tecnicomecanica_vencida", "otro"
        ]
        
        tipos_reales = [tipo.value for tipo in TipoNovedad]
        
        # Verificar longitud exacta
        assert len(tipos_reales) == 9
        assert len(tipos_reales) == len(tipos_esperados)
        
        # Verificar que todos los tipos esperados están presentes
        for tipo_esperado in tipos_esperados:
            assert tipo_esperado in tipos_reales


class TestComportamientoGeneralEnums:
    """Tests de comportamiento general de todos los enums"""
    
    def test_enums_son_hashables(self):
        """Test que los enums se pueden usar como claves de diccionario"""
        dict_test = {
            TipoServicio.PARTICULAR: "particular_data",
            EstadoCuenta.ACTIVA: "cuenta_activa",
            TipoNovedad.DOCUMENTO_FALTANTE: "doc_missing"
        }
        
        assert dict_test[TipoServicio.PARTICULAR] == "particular_data"
        assert dict_test[EstadoCuenta.ACTIVA] == "cuenta_activa"
        assert dict_test[TipoNovedad.DOCUMENTO_FALTANTE] == "doc_missing"
    
    def test_enums_string_representation(self):
        """Test representación string de enums"""
        assert str(TipoServicio.PARTICULAR) == "TipoServicio.PARTICULAR"
        assert repr(TipoServicio.PARTICULAR) == "<TipoServicio.PARTICULAR: 'particular'>"
    
    def test_enums_equality(self):
        """Test igualdad de enums"""
        # Igualdad de instancia
        assert TipoServicio.PARTICULAR == TipoServicio.PARTICULAR
        
        # Diferentes enums no son iguales aunque tengan el mismo valor
        assert TipoServicio.PARTICULAR != EstadoCuenta.ACTIVA
    
    def test_enums_no_se_pueden_instanciar_directamente(self):
        """Test que no se pueden crear nuevas instancias"""
        # En Python, los enums lanzan ValueError para valores inválidos
        with pytest.raises(ValueError):
            TipoServicio("nuevo_tipo")
    
    def test_acceso_por_nombre(self):
        """Test acceso a enum por nombre"""
        assert TipoServicio["PARTICULAR"] == TipoServicio.PARTICULAR
        assert EstadoCuenta["ACTIVA"] == EstadoCuenta.ACTIVA
        
        with pytest.raises(KeyError):
            TipoServicio["NO_EXISTE"]
    
    def test_valores_unicos(self):
        """Test que no hay valores duplicados en cada enum"""
        # TipoServicio
        valores_tipo = [tipo.value for tipo in TipoServicio]
        assert len(valores_tipo) == len(set(valores_tipo))
        
        # EstadoCuenta  
        valores_estado = [estado.value for estado in EstadoCuenta]
        assert len(valores_estado) == len(set(valores_estado))
        
        # TipoNovedad
        valores_novedad = [tipo.value for tipo in TipoNovedad]
        assert len(valores_novedad) == len(set(valores_novedad))