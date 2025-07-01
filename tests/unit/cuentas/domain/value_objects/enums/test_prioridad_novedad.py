import pytest
from app.cuentas.domain.value_objects.enums.novedades.prioridad_novedad import PrioridadNovedad


class TestPrioridadNovedad:
    """Tests unitarios para PrioridadNovedad"""
    
    def test_valores_enum_correctos(self):
        """Verificar que los valores del enum son correctos"""
        assert PrioridadNovedad.BAJA.value == "baja"
        assert PrioridadNovedad.MEDIA.value == "media"
        assert PrioridadNovedad.ALTA.value == "alta"
        assert PrioridadNovedad.CRITICA.value == "critica"
    
    def test_comparacion_prioridades_baja(self):
        """Test comparaciones con prioridad BAJA"""
        baja = PrioridadNovedad.BAJA
        
        # BAJA no es mayor que ninguna
        assert baja.es_mayor_que(PrioridadNovedad.BAJA) == False
        assert baja.es_mayor_que(PrioridadNovedad.MEDIA) == False
        assert baja.es_mayor_que(PrioridadNovedad.ALTA) == False
        assert baja.es_mayor_que(PrioridadNovedad.CRITICA) == False
    
    def test_comparacion_prioridades_media(self):
        """Test comparaciones con prioridad MEDIA"""
        media = PrioridadNovedad.MEDIA
        
        # MEDIA es mayor que BAJA solamente
        assert media.es_mayor_que(PrioridadNovedad.BAJA) == True
        assert media.es_mayor_que(PrioridadNovedad.MEDIA) == False
        assert media.es_mayor_que(PrioridadNovedad.ALTA) == False
        assert media.es_mayor_que(PrioridadNovedad.CRITICA) == False
    
    def test_comparacion_prioridades_alta(self):
        """Test comparaciones con prioridad ALTA"""
        alta = PrioridadNovedad.ALTA
        
        # ALTA es mayor que BAJA y MEDIA
        assert alta.es_mayor_que(PrioridadNovedad.BAJA) == True
        assert alta.es_mayor_que(PrioridadNovedad.MEDIA) == True
        assert alta.es_mayor_que(PrioridadNovedad.ALTA) == False
        assert alta.es_mayor_que(PrioridadNovedad.CRITICA) == False
    
    def test_comparacion_prioridades_critica(self):
        """Test comparaciones con prioridad CRITICA"""
        critica = PrioridadNovedad.CRITICA
        
        # CRITICA es mayor que todas las demás
        assert critica.es_mayor_que(PrioridadNovedad.BAJA) == True
        assert critica.es_mayor_que(PrioridadNovedad.MEDIA) == True
        assert critica.es_mayor_que(PrioridadNovedad.ALTA) == True
        assert critica.es_mayor_que(PrioridadNovedad.CRITICA) == False
    
    def test_es_critica_o_alta_true(self):
        """Test que ALTA y CRITICA requieren atención inmediata"""
        assert PrioridadNovedad.ALTA.es_critica_o_alta() == True
        assert PrioridadNovedad.CRITICA.es_critica_o_alta() == True
    
    def test_es_critica_o_alta_false(self):
        """Test que BAJA y MEDIA no requieren atención inmediata"""
        assert PrioridadNovedad.BAJA.es_critica_o_alta() == False
        assert PrioridadNovedad.MEDIA.es_critica_o_alta() == False
    
    def test_orden_jerarquico_completo(self):
        """Test orden jerárquico completo de prioridades"""
        prioridades = [
            PrioridadNovedad.BAJA,
            PrioridadNovedad.MEDIA,
            PrioridadNovedad.ALTA,
            PrioridadNovedad.CRITICA
        ]
        
        # Cada prioridad es mayor que las anteriores y menor que las siguientes
        for i in range(len(prioridades)):
            for j in range(len(prioridades)):
                if i > j:
                    assert prioridades[i].es_mayor_que(prioridades[j]) == True
                elif i <= j:
                    assert prioridades[i].es_mayor_que(prioridades[j]) == False
    
    def test_reglas_negocio_atencion_inmediata(self):
        """Test reglas de negocio para atención inmediata"""
        # Casos que requieren atención inmediata
        casos_urgentes = [PrioridadNovedad.ALTA, PrioridadNovedad.CRITICA]
        for prioridad in casos_urgentes:
            assert prioridad.es_critica_o_alta() == True
        
        # Casos que no requieren atención inmediata
        casos_normales = [PrioridadNovedad.BAJA, PrioridadNovedad.MEDIA]
        for prioridad in casos_normales:
            assert prioridad.es_critica_o_alta() == False
    
    def test_casos_edge_comparacion_consigo_mismo(self):
        """Test casos edge: comparación consigo mismo"""
        todas_las_prioridades = [
            PrioridadNovedad.BAJA,
            PrioridadNovedad.MEDIA,
            PrioridadNovedad.ALTA,
            PrioridadNovedad.CRITICA
        ]
        
        for prioridad in todas_las_prioridades:
            # Ninguna prioridad es mayor que sí misma
            assert prioridad.es_mayor_que(prioridad) == False
    
    def test_uso_tipico_ordenamiento(self):
        """Test uso típico para ordenamiento de novedades"""
        # Lista desordenada de prioridades
        prioridades_desordenadas = [
            PrioridadNovedad.MEDIA,
            PrioridadNovedad.CRITICA,
            PrioridadNovedad.BAJA,
            PrioridadNovedad.ALTA
        ]
        
        # Verificar que se pueden comparar para ordenamiento
        # CRITICA es la más alta
        critica = PrioridadNovedad.CRITICA
        for otra in [PrioridadNovedad.BAJA, PrioridadNovedad.MEDIA, PrioridadNovedad.ALTA]:
            assert critica.es_mayor_que(otra) == True
        
        # BAJA es la más baja
        baja = PrioridadNovedad.BAJA
        for otra in [PrioridadNovedad.MEDIA, PrioridadNovedad.ALTA, PrioridadNovedad.CRITICA]:
            assert baja.es_mayor_que(otra) == False
    
    def test_escalamiento_prioridades(self):
        """Test lógica de escalamiento de prioridades"""
        # Si una novedad de prioridad BAJA no se resuelve, 
        # la lógica de negocio debería poder escalarla
        
        # Verificar que existe una jerarquía clara para escalamiento
        assert PrioridadNovedad.MEDIA.es_mayor_que(PrioridadNovedad.BAJA) == True
        assert PrioridadNovedad.ALTA.es_mayor_que(PrioridadNovedad.MEDIA) == True
        assert PrioridadNovedad.CRITICA.es_mayor_que(PrioridadNovedad.ALTA) == True