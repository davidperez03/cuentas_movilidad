import pytest
from app.cuentas.domain.value_objects.enums.novedades.estado_novedad import EstadoNovedad


class TestEstadoNovedad:
    """Tests unitarios para EstadoNovedad"""
    
    def test_valores_enum_correctos(self):
        """Verificar que los valores del enum son correctos"""
        assert EstadoNovedad.PENDIENTE.value == "pendiente"
        assert EstadoNovedad.EN_REVISION.value == "en_revision"
        assert EstadoNovedad.RESUELTA.value == "resuelta"
        assert EstadoNovedad.REABIERTA.value == "reabierta"
    
    def test_transiciones_pendiente(self):
        """Test transiciones desde PENDIENTE"""
        estado = EstadoNovedad.PENDIENTE
        
        # Transiciones válidas
        assert estado.puede_transicionar_a(EstadoNovedad.EN_REVISION) == True
        assert estado.puede_transicionar_a(EstadoNovedad.RESUELTA) == True
        
        # Transiciones inválidas
        assert estado.puede_transicionar_a(EstadoNovedad.REABIERTA) == False
        assert estado.puede_transicionar_a(EstadoNovedad.PENDIENTE) == False
    
    def test_transiciones_en_revision(self):
        """Test transiciones desde EN_REVISION"""
        estado = EstadoNovedad.EN_REVISION
        
        # Transiciones válidas
        assert estado.puede_transicionar_a(EstadoNovedad.RESUELTA) == True
        assert estado.puede_transicionar_a(EstadoNovedad.PENDIENTE) == True
        
        # Transiciones inválidas
        assert estado.puede_transicionar_a(EstadoNovedad.REABIERTA) == False
        assert estado.puede_transicionar_a(EstadoNovedad.EN_REVISION) == False
    
    def test_transiciones_resuelta(self):
        """Test transiciones desde RESUELTA"""
        estado = EstadoNovedad.RESUELTA
        
        # Transiciones válidas
        assert estado.puede_transicionar_a(EstadoNovedad.REABIERTA) == True
        
        # Transiciones inválidas
        assert estado.puede_transicionar_a(EstadoNovedad.PENDIENTE) == False
        assert estado.puede_transicionar_a(EstadoNovedad.EN_REVISION) == False
        assert estado.puede_transicionar_a(EstadoNovedad.RESUELTA) == False
    
    def test_transiciones_reabierta(self):
        """Test transiciones desde REABIERTA"""
        estado = EstadoNovedad.REABIERTA
        
        # Transiciones válidas
        assert estado.puede_transicionar_a(EstadoNovedad.EN_REVISION) == True
        assert estado.puede_transicionar_a(EstadoNovedad.RESUELTA) == True
        
        # Transiciones inválidas
        assert estado.puede_transicionar_a(EstadoNovedad.PENDIENTE) == False
        assert estado.puede_transicionar_a(EstadoNovedad.REABIERTA) == False
    
    def test_es_estado_final(self):
        """Test identificación de estado final"""
        # Solo RESUELTA permite cerrar el proceso
        assert EstadoNovedad.RESUELTA.es_estado_final() == True
        
        # Los demás no son finales
        assert EstadoNovedad.PENDIENTE.es_estado_final() == False
        assert EstadoNovedad.EN_REVISION.es_estado_final() == False
        assert EstadoNovedad.REABIERTA.es_estado_final() == False
    
    def test_requiere_accion(self):
        """Test estados que requieren acción del usuario"""
        # Estados que requieren acción
        assert EstadoNovedad.PENDIENTE.requiere_accion() == True
        assert EstadoNovedad.REABIERTA.requiere_accion() == True
        
        # Estados que no requieren acción inmediata
        assert EstadoNovedad.EN_REVISION.requiere_accion() == False
        assert EstadoNovedad.RESUELTA.requiere_accion() == False
    
    def test_ciclo_completo_directo(self):
        """Test ciclo directo: PENDIENTE -> RESUELTA"""
        estado = EstadoNovedad.PENDIENTE
        
        # Transición directa a resuelta
        assert estado.puede_transicionar_a(EstadoNovedad.RESUELTA) == True
        estado = EstadoNovedad.RESUELTA
        
        # Estado final alcanzado
        assert estado.es_estado_final() == True
        assert estado.requiere_accion() == False
    
    def test_ciclo_con_revision(self):
        """Test ciclo con revisión: PENDIENTE -> EN_REVISION -> RESUELTA"""
        estado = EstadoNovedad.PENDIENTE
        
        # PENDIENTE -> EN_REVISION
        assert estado.puede_transicionar_a(EstadoNovedad.EN_REVISION) == True
        estado = EstadoNovedad.EN_REVISION
        
        # EN_REVISION -> RESUELTA
        assert estado.puede_transicionar_a(EstadoNovedad.RESUELTA) == True
        estado = EstadoNovedad.RESUELTA
        
        assert estado.es_estado_final() == True
    
    def test_ciclo_con_reapertura(self):
        """Test ciclo con reapertura: RESUELTA -> REABIERTA -> RESUELTA"""
        estado = EstadoNovedad.RESUELTA
        
        # RESUELTA -> REABIERTA
        assert estado.puede_transicionar_a(EstadoNovedad.REABIERTA) == True
        estado = EstadoNovedad.REABIERTA
        
        # Requiere acción después de reabrirse
        assert estado.requiere_accion() == True
        
        # REABIERTA -> RESUELTA
        assert estado.puede_transicionar_a(EstadoNovedad.RESUELTA) == True
        estado = EstadoNovedad.RESUELTA
        
        assert estado.es_estado_final() == True
    
    def test_ciclo_revision_devuelve_pendiente(self):
        """Test que desde EN_REVISION se puede devolver a PENDIENTE"""
        estado = EstadoNovedad.EN_REVISION
        
        # EN_REVISION -> PENDIENTE (necesita más trabajo)
        assert estado.puede_transicionar_a(EstadoNovedad.PENDIENTE) == True
        estado = EstadoNovedad.PENDIENTE
        
        # Requiere acción nuevamente
        assert estado.requiere_accion() == True
    
    def test_casos_edge_transiciones_reflexivas(self):
        """Test casos edge: transiciones a sí mismo"""
        todos_los_estados = [
            EstadoNovedad.PENDIENTE,
            EstadoNovedad.EN_REVISION,
            EstadoNovedad.RESUELTA,
            EstadoNovedad.REABIERTA
        ]
        
        for estado in todos_los_estados:
            # Ningún estado puede transicionar a sí mismo
            assert estado.puede_transicionar_a(estado) == False
    
    def test_reglas_negocio_reapertura(self):
        """Test reglas de negocio específicas para reapertura"""
        # Solo se puede reabrir desde RESUELTA
        assert EstadoNovedad.RESUELTA.puede_transicionar_a(EstadoNovedad.REABIERTA) == True
        
        # No se puede reabrir desde otros estados
        assert EstadoNovedad.PENDIENTE.puede_transicionar_a(EstadoNovedad.REABIERTA) == False
        assert EstadoNovedad.EN_REVISION.puede_transicionar_a(EstadoNovedad.REABIERTA) == False
        assert EstadoNovedad.REABIERTA.puede_transicionar_a(EstadoNovedad.REABIERTA) == False
    
    def test_logica_escalamiento_por_estado(self):
        """Test lógica para escalamiento basado en estado"""
        # Estados que necesitan escalamiento (requieren acción)
        estados_criticos = [EstadoNovedad.PENDIENTE, EstadoNovedad.REABIERTA]
        for estado in estados_criticos:
            assert estado.requiere_accion() == True
        
        # Estados que están en progreso o resueltos
        estados_estables = [EstadoNovedad.EN_REVISION, EstadoNovedad.RESUELTA]
        for estado in estados_estables:
            assert estado.requiere_accion() == False
    
    def test_flujo_complejo_multiple_reaberturas(self):
        """Test flujo complejo con múltiples reaberturas"""
        # PENDIENTE -> RESUELTA -> REABIERTA -> EN_REVISION -> RESUELTA -> REABIERTA -> RESUELTA
        estado = EstadoNovedad.PENDIENTE
        
        # Primera resolución directa
        assert estado.puede_transicionar_a(EstadoNovedad.RESUELTA) == True
        estado = EstadoNovedad.RESUELTA
        
        # Primera reapertura
        assert estado.puede_transicionar_a(EstadoNovedad.REABIERTA) == True
        estado = EstadoNovedad.REABIERTA
        
        # Ir a revisión
        assert estado.puede_transicionar_a(EstadoNovedad.EN_REVISION) == True
        estado = EstadoNovedad.EN_REVISION
        
        # Segunda resolución
        assert estado.puede_transicionar_a(EstadoNovedad.RESUELTA) == True
        estado = EstadoNovedad.RESUELTA
        
        # Segunda reapertura
        assert estado.puede_transicionar_a(EstadoNovedad.REABIERTA) == True
        estado = EstadoNovedad.REABIERTA
        
        # Resolución final directa
        assert estado.puede_transicionar_a(EstadoNovedad.RESUELTA) == True
        estado = EstadoNovedad.RESUELTA
        
        assert estado.es_estado_final() == True