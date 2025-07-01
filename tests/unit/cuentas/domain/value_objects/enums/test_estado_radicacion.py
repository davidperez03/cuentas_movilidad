import pytest
from app.cuentas.domain.value_objects.enums.estado_radicacion import EstadoRadicacion


class TestEstadoRadicacion:
    """Tests unitarios para EstadoRadicacion"""
    
    def test_valores_enum_correctos(self):
        """Verificar que los valores del enum son correctos"""
        assert EstadoRadicacion.PENDIENTE_RADICAR.value == "pendiente_radicar"
        assert EstadoRadicacion.RECIBIDO.value == "recibido"
        assert EstadoRadicacion.REVISADO.value == "revisado"
        assert EstadoRadicacion.CON_NOVEDADES.value == "con_novedades"
        assert EstadoRadicacion.RADICADO.value == "radicado"
        assert EstadoRadicacion.DEVUELTO.value == "devuelto"
    
    def test_transiciones_pendiente_radicar(self):
        """Test transiciones desde PENDIENTE_RADICAR"""
        estado = EstadoRadicacion.PENDIENTE_RADICAR
        
        # Transiciones válidas
        assert estado.puede_transicionar_a(EstadoRadicacion.RECIBIDO) == True
        
        # Transiciones inválidas
        assert estado.puede_transicionar_a(EstadoRadicacion.REVISADO) == False
        assert estado.puede_transicionar_a(EstadoRadicacion.CON_NOVEDADES) == False
        assert estado.puede_transicionar_a(EstadoRadicacion.RADICADO) == False
        assert estado.puede_transicionar_a(EstadoRadicacion.DEVUELTO) == False
    
    def test_transiciones_recibido(self):
        """Test transiciones desde RECIBIDO"""
        estado = EstadoRadicacion.RECIBIDO
        
        # Transiciones válidas
        assert estado.puede_transicionar_a(EstadoRadicacion.REVISADO) == True
        
        # Transiciones inválidas
        assert estado.puede_transicionar_a(EstadoRadicacion.PENDIENTE_RADICAR) == False
        assert estado.puede_transicionar_a(EstadoRadicacion.CON_NOVEDADES) == False
        assert estado.puede_transicionar_a(EstadoRadicacion.RADICADO) == False
        assert estado.puede_transicionar_a(EstadoRadicacion.DEVUELTO) == False
    
    def test_transiciones_revisado(self):
        """Test transiciones desde REVISADO"""
        estado = EstadoRadicacion.REVISADO
        
        # Transiciones válidas
        assert estado.puede_transicionar_a(EstadoRadicacion.RADICADO) == True
        assert estado.puede_transicionar_a(EstadoRadicacion.CON_NOVEDADES) == True
        
        # Transiciones inválidas
        assert estado.puede_transicionar_a(EstadoRadicacion.PENDIENTE_RADICAR) == False
        assert estado.puede_transicionar_a(EstadoRadicacion.RECIBIDO) == False
        assert estado.puede_transicionar_a(EstadoRadicacion.DEVUELTO) == False
    
    def test_transiciones_con_novedades(self):
        """Test transiciones desde CON_NOVEDADES"""
        estado = EstadoRadicacion.CON_NOVEDADES
        
        # Transiciones válidas
        assert estado.puede_transicionar_a(EstadoRadicacion.REVISADO) == True
        
        # Transiciones inválidas
        assert estado.puede_transicionar_a(EstadoRadicacion.PENDIENTE_RADICAR) == False
        assert estado.puede_transicionar_a(EstadoRadicacion.RECIBIDO) == False
        assert estado.puede_transicionar_a(EstadoRadicacion.RADICADO) == False
        assert estado.puede_transicionar_a(EstadoRadicacion.DEVUELTO) == False
    
    def test_estados_finales_sin_transiciones(self):
        """Test que estados finales no permiten transiciones"""
        # RADICADO no puede transicionar a nada
        estado_radicado = EstadoRadicacion.RADICADO
        assert estado_radicado.puede_transicionar_a(EstadoRadicacion.REVISADO) == False
        assert estado_radicado.puede_transicionar_a(EstadoRadicacion.CON_NOVEDADES) == False
        assert estado_radicado.puede_transicionar_a(EstadoRadicacion.DEVUELTO) == False
        
        # DEVUELTO no puede transicionar a nada
        estado_devuelto = EstadoRadicacion.DEVUELTO
        assert estado_devuelto.puede_transicionar_a(EstadoRadicacion.REVISADO) == False
        assert estado_devuelto.puede_transicionar_a(EstadoRadicacion.RADICADO) == False
    
    def test_admin_puede_devolver_desde_cualquier_estado(self):
        """Test que admin puede devolver desde cualquier estado"""
        todos_los_estados = [
            EstadoRadicacion.PENDIENTE_RADICAR,
            EstadoRadicacion.RECIBIDO,
            EstadoRadicacion.REVISADO,
            EstadoRadicacion.CON_NOVEDADES,
            EstadoRadicacion.RADICADO,
            EstadoRadicacion.DEVUELTO
        ]
        
        for estado in todos_los_estados:
            assert estado.puede_transicionar_a(EstadoRadicacion.DEVUELTO, es_admin=True) == True
    
    def test_admin_no_afecta_otras_transiciones(self):
        """Test que ser admin no afecta otras transiciones válidas/inválidas"""
        estado = EstadoRadicacion.PENDIENTE_RADICAR
        
        # Transición válida sigue siendo válida
        assert estado.puede_transicionar_a(EstadoRadicacion.RECIBIDO, es_admin=True) == True
        
        # Transición inválida sigue siendo inválida (excepto DEVUELTO)
        assert estado.puede_transicionar_a(EstadoRadicacion.RADICADO, es_admin=True) == False
    
    def test_es_estado_final(self):
        """Test identificación de estados finales"""
        # Estados finales
        assert EstadoRadicacion.RADICADO.es_estado_final() == True
        assert EstadoRadicacion.DEVUELTO.es_estado_final() == True
        
        # Estados no finales
        assert EstadoRadicacion.PENDIENTE_RADICAR.es_estado_final() == False
        assert EstadoRadicacion.RECIBIDO.es_estado_final() == False
        assert EstadoRadicacion.REVISADO.es_estado_final() == False
        assert EstadoRadicacion.CON_NOVEDADES.es_estado_final() == False
    
    def test_ciclo_completo_feliz(self):
        """Test ciclo completo de transiciones exitosas"""
        # Flujo feliz: PENDIENTE -> RECIBIDO -> REVISADO -> RADICADO
        estado = EstadoRadicacion.PENDIENTE_RADICAR
        
        # Primera transición
        assert estado.puede_transicionar_a(EstadoRadicacion.RECIBIDO) == True
        estado = EstadoRadicacion.RECIBIDO
        
        # Segunda transición
        assert estado.puede_transicionar_a(EstadoRadicacion.REVISADO) == True
        estado = EstadoRadicacion.REVISADO
        
        # Tercera transición
        assert estado.puede_transicionar_a(EstadoRadicacion.RADICADO) == True
        estado = EstadoRadicacion.RADICADO
        
        # Estado final
        assert estado.es_estado_final() == True
    
    def test_ciclo_con_novedades(self):
        """Test ciclo con manejo de novedades"""
        # Flujo con novedades: PENDIENTE -> RECIBIDO -> REVISADO -> CON_NOVEDADES -> REVISADO -> RADICADO
        estado = EstadoRadicacion.PENDIENTE_RADICAR
        
        # PENDIENTE -> RECIBIDO
        assert estado.puede_transicionar_a(EstadoRadicacion.RECIBIDO) == True
        estado = EstadoRadicacion.RECIBIDO
        
        # RECIBIDO -> REVISADO
        assert estado.puede_transicionar_a(EstadoRadicacion.REVISADO) == True
        estado = EstadoRadicacion.REVISADO
        
        # REVISADO -> CON_NOVEDADES
        assert estado.puede_transicionar_a(EstadoRadicacion.CON_NOVEDADES) == True
        estado = EstadoRadicacion.CON_NOVEDADES
        
        # CON_NOVEDADES -> REVISADO (novedades resueltas)
        assert estado.puede_transicionar_a(EstadoRadicacion.REVISADO) == True
        estado = EstadoRadicacion.REVISADO
        
        # REVISADO -> RADICADO
        assert estado.puede_transicionar_a(EstadoRadicacion.RADICADO) == True
        estado = EstadoRadicacion.RADICADO
        
        assert estado.es_estado_final() == True
    
    def test_diferencias_con_traslado(self):
        """Test diferencias específicas del flujo de radicación vs traslado"""
        # Radicación tiene un paso más: PENDIENTE_RADICAR
        assert EstadoRadicacion.PENDIENTE_RADICAR.puede_transicionar_a(EstadoRadicacion.RECIBIDO) == True
        
        # El estado inicial es diferente
        estados_iniciales_validos = [EstadoRadicacion.PENDIENTE_RADICAR]
        for estado in estados_iniciales_validos:
            assert not estado.es_estado_final()
    
    def test_casos_edge_transiciones_reflexivas(self):
        """Test casos edge: transiciones a sí mismo"""
        todos_los_estados = [
            EstadoRadicacion.PENDIENTE_RADICAR,
            EstadoRadicacion.RECIBIDO,
            EstadoRadicacion.REVISADO,
            EstadoRadicacion.CON_NOVEDADES,
            EstadoRadicacion.RADICADO,
            EstadoRadicacion.DEVUELTO
        ]
        
        for estado in todos_los_estados:
            # Ningún estado puede transicionar a sí mismo
            assert estado.puede_transicionar_a(estado) == False