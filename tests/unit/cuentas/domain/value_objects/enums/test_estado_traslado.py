import pytest
from app.cuentas.domain.value_objects.enums.estado_traslado import EstadoTraslado


class TestEstadoTraslado:
    """Tests unitarios para EstadoTraslado"""
    
    def test_valores_enum_correctos(self):
        """Verificar que los valores del enum son correctos"""
        assert EstadoTraslado.ENVIADO_ORGANISMO_DESTINO.value == "enviado_organismo_destino"
        assert EstadoTraslado.REVISADO.value == "revisado"
        assert EstadoTraslado.CON_NOVEDADES.value == "con_novedades"
        assert EstadoTraslado.TRASLADADO.value == "trasladado"
        assert EstadoTraslado.DEVUELTO.value == "devuelto"
    
    def test_transiciones_enviado_organismo_destino(self):
        """Test transiciones desde ENVIADO_ORGANISMO_DESTINO"""
        estado = EstadoTraslado.ENVIADO_ORGANISMO_DESTINO
        
        # Transiciones válidas
        assert estado.puede_transicionar_a(EstadoTraslado.REVISADO) == True
        
        # Transiciones inválidas
        assert estado.puede_transicionar_a(EstadoTraslado.TRASLADADO) == False
        assert estado.puede_transicionar_a(EstadoTraslado.CON_NOVEDADES) == False
        assert estado.puede_transicionar_a(EstadoTraslado.DEVUELTO) == False
    
    def test_transiciones_revisado(self):
        """Test transiciones desde REVISADO"""
        estado = EstadoTraslado.REVISADO
        
        # Transiciones válidas
        assert estado.puede_transicionar_a(EstadoTraslado.TRASLADADO) == True
        assert estado.puede_transicionar_a(EstadoTraslado.CON_NOVEDADES) == True
        
        # Transiciones inválidas
        assert estado.puede_transicionar_a(EstadoTraslado.ENVIADO_ORGANISMO_DESTINO) == False
        assert estado.puede_transicionar_a(EstadoTraslado.DEVUELTO) == False
    
    def test_transiciones_con_novedades(self):
        """Test transiciones desde CON_NOVEDADES"""
        estado = EstadoTraslado.CON_NOVEDADES
        
        # Transiciones válidas
        assert estado.puede_transicionar_a(EstadoTraslado.REVISADO) == True
        
        # Transiciones inválidas
        assert estado.puede_transicionar_a(EstadoTraslado.TRASLADADO) == False
        assert estado.puede_transicionar_a(EstadoTraslado.ENVIADO_ORGANISMO_DESTINO) == False
        assert estado.puede_transicionar_a(EstadoTraslado.DEVUELTO) == False
    
    def test_estados_finales_sin_transiciones(self):
        """Test que estados finales no permiten transiciones"""
        # TRASLADADO no puede transicionar a nada
        estado_trasladado = EstadoTraslado.TRASLADADO
        assert estado_trasladado.puede_transicionar_a(EstadoTraslado.REVISADO) == False
        assert estado_trasladado.puede_transicionar_a(EstadoTraslado.CON_NOVEDADES) == False
        assert estado_trasladado.puede_transicionar_a(EstadoTraslado.DEVUELTO) == False
        
        # DEVUELTO no puede transicionar a nada
        estado_devuelto = EstadoTraslado.DEVUELTO
        assert estado_devuelto.puede_transicionar_a(EstadoTraslado.REVISADO) == False
        assert estado_devuelto.puede_transicionar_a(EstadoTraslado.TRASLADADO) == False
    
    def test_admin_puede_devolver_desde_cualquier_estado(self):
        """Test que admin puede devolver desde cualquier estado"""
        todos_los_estados = [
            EstadoTraslado.ENVIADO_ORGANISMO_DESTINO,
            EstadoTraslado.REVISADO,
            EstadoTraslado.CON_NOVEDADES,
            EstadoTraslado.TRASLADADO,
            EstadoTraslado.DEVUELTO
        ]
        
        for estado in todos_los_estados:
            assert estado.puede_transicionar_a(EstadoTraslado.DEVUELTO, es_admin=True) == True
    
    def test_admin_no_afecta_otras_transiciones(self):
        """Test que ser admin no afecta otras transiciones válidas/inválidas"""
        estado = EstadoTraslado.ENVIADO_ORGANISMO_DESTINO
        
        # Transición válida sigue siendo válida
        assert estado.puede_transicionar_a(EstadoTraslado.REVISADO, es_admin=True) == True
        
        # Transición inválida sigue siendo inválida (excepto DEVUELTO)
        assert estado.puede_transicionar_a(EstadoTraslado.TRASLADADO, es_admin=True) == False
    
    def test_es_estado_final(self):
        """Test identificación de estados finales"""
        # Estados finales
        assert EstadoTraslado.TRASLADADO.es_estado_final() == True
        assert EstadoTraslado.DEVUELTO.es_estado_final() == True
        
        # Estados no finales
        assert EstadoTraslado.ENVIADO_ORGANISMO_DESTINO.es_estado_final() == False
        assert EstadoTraslado.REVISADO.es_estado_final() == False
        assert EstadoTraslado.CON_NOVEDADES.es_estado_final() == False
    
    def test_transiciones_permitidas_privado(self):
        """Test método privado _get_transiciones_permitidas"""
        # ENVIADO_ORGANISMO_DESTINO
        transiciones = EstadoTraslado.ENVIADO_ORGANISMO_DESTINO._get_transiciones_permitidas()
        assert EstadoTraslado.REVISADO in transiciones
        assert len(transiciones) == 1
        
        # REVISADO
        transiciones = EstadoTraslado.REVISADO._get_transiciones_permitidas()
        assert EstadoTraslado.TRASLADADO in transiciones
        assert EstadoTraslado.CON_NOVEDADES in transiciones
        assert len(transiciones) == 2
        
        # CON_NOVEDADES
        transiciones = EstadoTraslado.CON_NOVEDADES._get_transiciones_permitidas()
        assert EstadoTraslado.REVISADO in transiciones
        assert len(transiciones) == 1
        
        # Estados finales
        assert EstadoTraslado.TRASLADADO._get_transiciones_permitidas() == []
        assert EstadoTraslado.DEVUELTO._get_transiciones_permitidas() == []
    
    def test_ciclo_completo_feliz(self):
        """Test ciclo completo de transiciones exitosas"""
        # Flujo feliz: ENVIADO -> REVISADO -> TRASLADADO
        estado = EstadoTraslado.ENVIADO_ORGANISMO_DESTINO
        
        # Primera transición
        assert estado.puede_transicionar_a(EstadoTraslado.REVISADO) == True
        estado = EstadoTraslado.REVISADO
        
        # Segunda transición
        assert estado.puede_transicionar_a(EstadoTraslado.TRASLADADO) == True
        estado = EstadoTraslado.TRASLADADO
        
        # Estado final
        assert estado.es_estado_final() == True
    
    def test_ciclo_con_novedades(self):
        """Test ciclo con manejo de novedades"""
        # Flujo con novedades: ENVIADO -> REVISADO -> CON_NOVEDADES -> REVISADO -> TRASLADADO
        estado = EstadoTraslado.ENVIADO_ORGANISMO_DESTINO
        
        # ENVIADO -> REVISADO
        assert estado.puede_transicionar_a(EstadoTraslado.REVISADO) == True
        estado = EstadoTraslado.REVISADO
        
        # REVISADO -> CON_NOVEDADES
        assert estado.puede_transicionar_a(EstadoTraslado.CON_NOVEDADES) == True
        estado = EstadoTraslado.CON_NOVEDADES
        
        # CON_NOVEDADES -> REVISADO (novedades resueltas)
        assert estado.puede_transicionar_a(EstadoTraslado.REVISADO) == True
        estado = EstadoTraslado.REVISADO
        
        # REVISADO -> TRASLADADO
        assert estado.puede_transicionar_a(EstadoTraslado.TRASLADADO) == True
        estado = EstadoTraslado.TRASLADADO
        
        assert estado.es_estado_final() == True
    
    def test_casos_edge_transiciones_reflexivas(self):
        """Test casos edge: transiciones a sí mismo"""
        todos_los_estados = [
            EstadoTraslado.ENVIADO_ORGANISMO_DESTINO,
            EstadoTraslado.REVISADO,
            EstadoTraslado.CON_NOVEDADES,
            EstadoTraslado.TRASLADADO,
            EstadoTraslado.DEVUELTO
        ]
        
        for estado in todos_los_estados:
            # Ningún estado puede transicionar a sí mismo
            assert estado.puede_transicionar_a(estado) == False