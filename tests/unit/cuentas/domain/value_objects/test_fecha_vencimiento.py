import pytest
from datetime import date, timedelta
from app.cuentas.domain.value_objects.fecha_vencimiento import FechaVencimiento
from app.cuentas.domain.value_objects.fecha_tramite import FechaTramite


class TestFechaVencimientoCreacion:
    """Tests para creación de fechas de vencimiento"""
    
    def test_crear_fecha_vencimiento_futura(self):
        """Test crear fecha de vencimiento futura válida"""
        mañana = date.today() + timedelta(days=1)
        fecha = FechaVencimiento(mañana)
        assert fecha.fecha == mañana
        assert fecha.esta_vigente() == True
        assert fecha.esta_vencida() == False
    
    def test_crear_fecha_vencimiento_lejana(self):
        """Test crear fecha de vencimiento lejana"""
        en_dos_meses = date.today() + timedelta(days=60)
        fecha = FechaVencimiento(en_dos_meses)
        assert fecha.fecha == en_dos_meses
        assert fecha.esta_vigente() == True
    
    def test_crear_fecha_vencimiento_pasada_permitida(self):
        """Test que fechas pasadas son permitidas (trámites retroactivos)"""
        ayer = date.today() - timedelta(days=1)
        fecha = FechaVencimiento(ayer)
        assert fecha.fecha == ayer
        assert fecha.esta_vencida() == True
        assert fecha.esta_vigente() == False
    
    def test_crear_fecha_vencimiento_hoy_permitida(self):
        """Test que fecha de hoy es permitida (vence hoy)"""
        hoy = date.today()
        fecha = FechaVencimiento(hoy)
        assert fecha.fecha == hoy
        assert fecha.es_hoy() == True
        assert fecha.esta_vigente() == True  # Hoy aún está vigente
    
    def test_fecha_tipo_invalido_error(self):
        """Test que tipo inválido genera error"""
        with pytest.raises(ValueError, match="debe ser un objeto date válido"):
            FechaVencimiento("2024-12-04")
    
    def test_fecha_none_error(self):
        """Test que None genera error"""
        with pytest.raises(ValueError, match="debe ser un objeto date válido"):
            FechaVencimiento(None)


class TestFechaVencimientoEstados:
    """Tests para verificación de estados"""
    
    def test_esta_vigente_true(self):
        """Test está vigente para fecha futura"""
        en_una_semana = date.today() + timedelta(days=7)
        fecha = FechaVencimiento(en_una_semana)
        assert fecha.esta_vigente() == True
        assert fecha.esta_vencida() == False
    
    def test_esta_vencida_true(self):
        """Test está vencida para fecha pasada"""
        ayer = date.today() - timedelta(days=1)
        fecha = FechaVencimiento(ayer)
        assert fecha.esta_vencida() == True
        assert fecha.esta_vigente() == False
    
    def test_es_hoy_true(self):
        """Test es_hoy para fecha actual"""
        hoy = date.today()
        fecha = FechaVencimiento(hoy)
        assert fecha.es_hoy() == True
        assert fecha.esta_vigente() == True  # Hoy aún cuenta como vigente


class TestFechaVencimientoCalculos:
    """Tests para cálculos de días y períodos"""
    
    def test_dias_restantes_futuro(self):
        """Test días restantes para fecha futura"""
        en_10_dias = date.today() + timedelta(days=10)
        fecha = FechaVencimiento(en_10_dias)
        assert fecha.dias_restantes() == 10
    
    def test_dias_restantes_mañana(self):
        """Test días restantes para mañana"""
        mañana = date.today() + timedelta(days=1)
        fecha = FechaVencimiento(mañana)
        assert fecha.dias_restantes() == 1
    
    def test_dias_restantes_vencido(self):
        """Test días restantes para fecha vencida (negativo)"""
        hace_5_dias = date.today() - timedelta(days=5)
        fecha = FechaVencimiento(hace_5_dias)
        assert fecha.dias_restantes() == -5
    
    def test_semanas_restantes(self):
        """Test semanas restantes"""
        en_tres_semanas = date.today() + timedelta(days=21)
        fecha = FechaVencimiento(en_tres_semanas)
        assert fecha.semanas_restantes() == 3
    
    def test_semanas_restantes_parcial(self):
        """Test semanas restantes con días parciales"""
        en_10_dias = date.today() + timedelta(days=10)
        fecha = FechaVencimiento(en_10_dias)
        assert fecha.semanas_restantes() == 1  # 10 // 7 = 1


class TestFechaVencimientoAlertas:
    """Tests para sistema de alertas"""
    
    def test_esta_por_vencer_verdadero_defecto(self):
        """Test está por vencer con configuración por defecto (7 días)"""
        en_5_dias = date.today() + timedelta(days=5)
        fecha = FechaVencimiento(en_5_dias)
        assert fecha.esta_por_vencer() == True
    
    def test_esta_por_vencer_falso_defecto(self):
        """Test no está por vencer con configuración por defecto"""
        en_10_dias = date.today() + timedelta(days=10)
        fecha = FechaVencimiento(en_10_dias)
        assert fecha.esta_por_vencer() == False
    
    def test_esta_por_vencer_personalizado(self):
        """Test está por vencer con días personalizados"""
        en_5_dias = date.today() + timedelta(days=5)
        fecha = FechaVencimiento(en_5_dias)
        
        assert fecha.esta_por_vencer(3) == False  # 5 > 3
        assert fecha.esta_por_vencer(10) == True  # 5 <= 10
    
    def test_es_critica_verdadero(self):
        """Test es crítica para fechas muy cercanas"""
        en_2_dias = date.today() + timedelta(days=2)
        fecha = FechaVencimiento(en_2_dias)
        assert fecha.es_critica() == True
    
    def test_es_critica_falso(self):
        """Test no es crítica para fechas no tan cercanas"""
        en_5_dias = date.today() + timedelta(days=5)
        fecha = FechaVencimiento(en_5_dias)
        assert fecha.es_critica() == False
    
    def test_es_critica_personalizado(self):
        """Test es crítica con días críticos personalizados"""
        en_5_dias = date.today() + timedelta(days=5)
        fecha = FechaVencimiento(en_5_dias)
        
        assert fecha.es_critica(3) == False  # 5 > 3
        assert fecha.es_critica(7) == True   # 5 <= 7


class TestFechaVencimientoNiveles:
    """Tests para niveles de urgencia"""
    
    def test_nivel_urgencia_normal(self):
        """Test nivel de urgencia normal"""
        en_15_dias = date.today() + timedelta(days=15)
        fecha = FechaVencimiento(en_15_dias)
        assert fecha.nivel_urgencia() == "normal"
    
    def test_nivel_urgencia_alerta(self):
        """Test nivel de urgencia alerta"""
        en_5_dias = date.today() + timedelta(days=5)
        fecha = FechaVencimiento(en_5_dias)
        assert fecha.nivel_urgencia() == "alerta"
    
    def test_nivel_urgencia_critica(self):
        """Test nivel de urgencia crítica"""
        mañana = date.today() + timedelta(days=1)
        fecha = FechaVencimiento(mañana)
        assert fecha.nivel_urgencia() == "critica"
    
    def test_nivel_urgencia_vencida(self):
        """Test nivel de urgencia vencida"""
        hace_5_dias = date.today() - timedelta(days=5)
        fecha = FechaVencimiento(hace_5_dias)
        assert fecha.nivel_urgencia() == "vencida"
    
    def test_color_indicador_normal(self):
        """Test color indicador para estado normal"""
        en_15_dias = date.today() + timedelta(days=15)
        fecha = FechaVencimiento(en_15_dias)
        assert fecha.color_indicador() == "green"
    
    def test_color_indicador_alerta(self):
        """Test color indicador para estado de alerta"""
        en_5_dias = date.today() + timedelta(days=5)
        fecha = FechaVencimiento(en_5_dias)
        assert fecha.color_indicador() == "yellow"
    
    def test_color_indicador_critica(self):
        """Test color indicador para estado crítico"""
        mañana = date.today() + timedelta(days=1)
        fecha = FechaVencimiento(mañana)
        assert fecha.color_indicador() == "orange"
    
    def test_color_indicador_vencida(self):
        """Test color indicador para estado vencido"""
        hace_5_dias = date.today() - timedelta(days=5)
        fecha = FechaVencimiento(hace_5_dias)
        assert fecha.color_indicador() == "red"


class TestFechaVencimientoPorcentaje:
    """Tests para cálculo de porcentajes"""
    
    def test_porcentaje_transcurrido_inicio(self):
        """Test porcentaje transcurrido al inicio del período"""
        hace_10_dias = date.today() - timedelta(days=10)
        en_50_dias = date.today() + timedelta(days=50)
        fecha = FechaVencimiento(en_50_dias)
        
        # Período total: 60 días, transcurrido: 10 días
        porcentaje = fecha.porcentaje_transcurrido(hace_10_dias)
        assert abs(porcentaje - 16.67) < 0.1  # 10/60 * 100 ≈ 16.67%
    
    def test_porcentaje_transcurrido_medio(self):
        """Test porcentaje transcurrido a la mitad del período"""
        hace_30_dias = date.today() - timedelta(days=30)
        en_30_dias = date.today() + timedelta(days=30)
        fecha = FechaVencimiento(en_30_dias)
        
        # Período total: 60 días, transcurrido: 30 días
        porcentaje = fecha.porcentaje_transcurrido(hace_30_dias)
        assert porcentaje == 50.0
    
    def test_porcentaje_transcurrido_completo(self):
        """Test porcentaje transcurrido completo"""
        hace_60_dias = date.today() - timedelta(days=60)
        mañana = date.today() + timedelta(days=1)
        fecha = FechaVencimiento(mañana)
        
        # Período total: 61 días, transcurrido: 60 días
        porcentaje = fecha.porcentaje_transcurrido(hace_60_dias)
        assert porcentaje > 95.0  # Casi 100%
    
    def test_porcentaje_transcurrido_caso_limite(self):
        """Test porcentaje transcurrido casos límite"""
        en_30_dias = date.today() + timedelta(days=30)
        fecha = FechaVencimiento(en_30_dias)
        
        # Inicio en el futuro (no debería pasar, pero probamos)
        mañana = date.today() + timedelta(days=1)
        porcentaje = fecha.porcentaje_transcurrido(mañana)
        assert porcentaje == 0.0


class TestFechaVencimientoExtraccion:
    """Tests para extracción de componentes"""
    
    def test_get_componentes_fecha(self):
        """Test extracción de componentes de fecha"""
        fecha_test = date.today() + timedelta(days=30)
        fecha = FechaVencimiento(fecha_test)
        
        assert fecha.get_year() == fecha_test.year
        assert fecha.get_month() == fecha_test.month
        assert fecha.get_day() == fecha_test.day
    
    def test_get_weekday_y_nombre(self):
        """Test obtención de día de semana"""
        fecha_futura = date.today() + timedelta(days=30)
        fecha = FechaVencimiento(fecha_futura)
        
        weekday = fecha.get_weekday()
        nombre = fecha.get_weekday_name()
        
        assert 0 <= weekday <= 6
        assert nombre in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    
    def test_es_fin_de_semana(self):
        """Test detección de fin de semana"""
        # Encontrar próximo sábado futuro
        fecha_actual = date.today()
        dias_hasta_sabado = (5 - fecha_actual.weekday()) % 7
        if dias_hasta_sabado <= 0:
            dias_hasta_sabado += 7
        sabado_futuro = fecha_actual + timedelta(days=dias_hasta_sabado)
        
        fecha = FechaVencimiento(sabado_futuro)
        assert fecha.es_fin_de_semana() == True
    
    def test_siguiente_dia_laboral_si_fin_de_semana(self):
        """Test siguiente día laboral si vence en fin de semana"""
        # Encontrar próximo sábado futuro
        fecha_actual = date.today()
        dias_hasta_sabado = (5 - fecha_actual.weekday()) % 7
        if dias_hasta_sabado <= 0:
            dias_hasta_sabado += 7
        sabado_futuro = fecha_actual + timedelta(days=dias_hasta_sabado)
        
        fecha = FechaVencimiento(sabado_futuro)
        siguiente_laboral = fecha.siguiente_dia_laboral_si_fin_de_semana()
        
        # Debe ser lunes (día 0)
        assert siguiente_laboral.weekday() == 0


class TestFechaVencimientoFormatos:
    """Tests para formatos de salida"""
    
    def test_formato_legible(self):
        """Test formato legible ISO"""
        en_10_dias = date.today() + timedelta(days=10)
        fecha = FechaVencimiento(en_10_dias)
        assert fecha.formato_legible() == en_10_dias.strftime("%Y-%m-%d")
    
    def test_formato_español(self):
        """Test formato español"""
        en_10_dias = date.today() + timedelta(days=10)
        fecha = FechaVencimiento(en_10_dias)
        assert fecha.formato_español() == en_10_dias.strftime("%d/%m/%Y")
    
    def test_formato_con_urgencia_normal(self):
        """Test formato con urgencia normal"""
        en_15_dias = date.today() + timedelta(days=15)
        fecha = FechaVencimiento(en_15_dias)
        formato = fecha.formato_con_urgencia()
        assert "🟢" in formato
    
    def test_formato_con_urgencia_alerta(self):
        """Test formato con urgencia alerta"""
        en_5_dias = date.today() + timedelta(days=5)
        fecha = FechaVencimiento(en_5_dias)
        formato = fecha.formato_con_urgencia()
        assert "🟡 ALERTA" in formato
    
    def test_formato_con_urgencia_critica(self):
        """Test formato con urgencia crítica"""
        mañana = date.today() + timedelta(days=1)
        fecha = FechaVencimiento(mañana)
        formato = fecha.formato_con_urgencia()
        assert "🔴 CRÍTICA" in formato
    
    def test_formato_con_urgencia_vencida(self):
        """Test formato con urgencia vencida"""
        hace_5_dias = date.today() - timedelta(days=5)
        fecha = FechaVencimiento(hace_5_dias)
        formato = fecha.formato_con_urgencia()
        assert "⚠️ VENCIDA" in formato
    
    def test_formato_con_dias_restantes_varios(self):
        """Test formato con días restantes para varios días"""
        en_5_dias = date.today() + timedelta(days=5)
        fecha = FechaVencimiento(en_5_dias)
        formato = fecha.formato_con_dias_restantes()
        assert "Faltan 5 días" in formato
    
    def test_formato_con_dias_restantes_mañana(self):
        """Test formato con días restantes para mañana"""
        mañana = date.today() + timedelta(days=1)
        fecha = FechaVencimiento(mañana)
        formato = fecha.formato_con_dias_restantes()
        assert "Vence MAÑANA" in formato
    
    def test_formato_con_dias_restantes_vencida(self):
        """Test formato con días restantes para fecha vencida"""
        hace_3_dias = date.today() - timedelta(days=3)
        fecha = FechaVencimiento(hace_3_dias)
        formato = fecha.formato_con_dias_restantes()
        assert "Vencida hace 3 días" in formato
    
    def test_formato_con_dias_restantes_hoy(self):
        """Test formato con días restantes para hoy"""
        hoy = date.today()
        fecha = FechaVencimiento(hoy)
        formato = fecha.formato_con_dias_restantes()
        assert "Vence HOY" in formato
    
    def test_str_representation(self):
        """Test representación string"""
        en_10_dias = date.today() + timedelta(days=10)
        fecha = FechaVencimiento(en_10_dias)
        assert str(fecha) == str(en_10_dias)
    
    def test_repr_representation(self):
        """Test representación repr"""
        en_5_dias = date.today() + timedelta(days=5)
        fecha = FechaVencimiento(en_5_dias)
        expected = f"FechaVencimiento(fecha={en_5_dias}, dias_restantes=5, urgencia=alerta)"
        assert repr(fecha) == expected


class TestFechaVencimientoFactoryMethods:
    """Tests para factory methods"""
    
    def test_calcular_desde_tramite(self):
        """Test calcular vencimiento desde fecha de trámite"""
        fecha_tramite = FechaTramite.crear_hoy()
        fecha_vencimiento = FechaVencimiento.calcular_desde_tramite(fecha_tramite)
        
        fecha_esperada = fecha_tramite.fecha + timedelta(days=60)
        assert fecha_vencimiento.fecha == fecha_esperada
        assert fecha_vencimiento.dias_restantes() == 60
    
    def test_calcular_desde_tramite_pasado(self):
        """Test calcular vencimiento desde trámite pasado"""
        hace_30_dias = date.today() - timedelta(days=30)
        fecha_tramite = FechaTramite(hace_30_dias)
        fecha_vencimiento = FechaVencimiento.calcular_desde_tramite(fecha_tramite)
        
        # Vencimiento debe ser hace_30_dias + 60 = en_30_dias
        assert fecha_vencimiento.dias_restantes() == 30
    
    def test_calcular_desde_fecha_defecto(self):
        """Test calcular desde fecha con días por defecto"""
        hoy = date.today()
        fecha_vencimiento = FechaVencimiento.calcular_desde_fecha(hoy)
        
        fecha_esperada = hoy + timedelta(days=60)
        assert fecha_vencimiento.fecha == fecha_esperada
    
    def test_calcular_desde_fecha_personalizado(self):
        """Test calcular desde fecha con días personalizados"""
        hoy = date.today()
        fecha_vencimiento = FechaVencimiento.calcular_desde_fecha(hoy, dias_vencimiento=30)
        
        fecha_esperada = hoy + timedelta(days=30)
        assert fecha_vencimiento.fecha == fecha_esperada
    
    def test_crear_para_fecha(self):
        """Test crear vencimiento para fecha específica"""
        en_15_dias = date.today() + timedelta(days=15)
        fecha = FechaVencimiento.crear_para_fecha(en_15_dias)
        assert fecha.fecha == en_15_dias
    
    def test_crear_si_valida_exitoso_futuro(self):
        """Test factory method crear_si_valida exitoso con fecha futura"""
        en_10_dias = date.today() + timedelta(days=10)
        fecha = FechaVencimiento.crear_si_valida(en_10_dias)
        assert fecha is not None
        assert fecha.fecha == en_10_dias
    
    def test_crear_si_valida_exitoso_pasado(self):
        """Test factory method crear_si_valida exitoso con fecha pasada"""
        ayer = date.today() - timedelta(days=1)
        fecha = FechaVencimiento.crear_si_valida(ayer)
        assert fecha is not None
        assert fecha.fecha == ayer
        assert fecha.esta_vencida() == True


class TestFechaVencimientoMetodosClase:
    """Tests para métodos de clase (utilidades)"""
    
    def test_obtener_vencimientos_proximos(self):
        """Test obtener vencimientos próximos"""
        vencimientos = [
            FechaVencimiento(date.today() + timedelta(days=5)),   # Próximo
            FechaVencimiento(date.today() + timedelta(days=15)),  # No próximo
            FechaVencimiento(date.today() + timedelta(days=3)),   # Próximo
            FechaVencimiento(date.today() + timedelta(days=20)),  # No próximo
        ]
        
        proximos = FechaVencimiento.obtener_vencimientos_proximos(vencimientos)
        assert len(proximos) == 2
        assert all(v.esta_por_vencer() for v in proximos)
    
    def test_obtener_vencimientos_proximos_personalizado(self):
        """Test obtener vencimientos próximos con días personalizados"""
        vencimientos = [
            FechaVencimiento(date.today() + timedelta(days=5)),   # Próximo con límite 10
            FechaVencimiento(date.today() + timedelta(days=15)),  # No próximo
        ]
        
        proximos = FechaVencimiento.obtener_vencimientos_proximos(vencimientos, dias_alerta=10)
        assert len(proximos) == 1
    
    def test_obtener_vencimientos_criticos(self):
        """Test obtener vencimientos críticos"""
        vencimientos = [
            FechaVencimiento(date.today() + timedelta(days=1)),   # Crítico
            FechaVencimiento(date.today() + timedelta(days=5)),   # No crítico
            FechaVencimiento(date.today() + timedelta(days=2)),   # Crítico
            FechaVencimiento(date.today() + timedelta(days=10)),  # No crítico
        ]
        
        criticos = FechaVencimiento.obtener_vencimientos_criticos(vencimientos)
        assert len(criticos) == 2
        assert all(v.es_critica() for v in criticos)
    
    def test_obtener_vencimientos_por_nivel(self):
        """Test agrupar vencimientos por nivel de urgencia"""
        vencimientos = [
            FechaVencimiento(date.today() + timedelta(days=1)),   # Crítica
            FechaVencimiento(date.today() + timedelta(days=5)),   # Alerta
            FechaVencimiento(date.today() + timedelta(days=15)),  # Normal
            FechaVencimiento(date.today() + timedelta(days=2)),   # Crítica
        ]
        
        grupos = FechaVencimiento.obtener_vencimientos_por_nivel(vencimientos)
        
        assert len(grupos["critica"]) == 2
        assert len(grupos["alerta"]) == 1
        assert len(grupos["normal"]) == 1
        assert len(grupos["vencida"]) == 0
    
    def test_obtener_vencimientos_por_nivel_con_vencidas(self):
        """Test agrupar vencimientos incluyendo vencidas"""
        vencimientos = [
            FechaVencimiento(date.today() + timedelta(days=1)),   # Crítica
            FechaVencimiento(date.today() - timedelta(days=2)),   # Vencida
            FechaVencimiento(date.today() + timedelta(days=15)),  # Normal
            FechaVencimiento(date.today() - timedelta(days=5)),   # Vencida
        ]
        
        grupos = FechaVencimiento.obtener_vencimientos_por_nivel(vencimientos)
        
        assert len(grupos["critica"]) == 1
        assert len(grupos["normal"]) == 1
        assert len(grupos["vencida"]) == 2
        assert len(grupos["alerta"]) == 0
    
    def test_obtener_vencimientos_por_nivel_vacio(self):
        """Test agrupar vencimientos vacío"""
        grupos = FechaVencimiento.obtener_vencimientos_por_nivel([])
        
        assert len(grupos["critica"]) == 0
        assert len(grupos["alerta"]) == 0
        assert len(grupos["normal"]) == 0
        assert len(grupos["vencida"]) == 0


class TestFechaVencimientoInmutabilidad:
    """Tests para inmutabilidad del value object"""
    
    def test_fecha_vencimiento_es_inmutable(self):
        """Test que fecha de vencimiento no se puede modificar"""
        en_10_dias = date.today() + timedelta(days=10)
        fecha = FechaVencimiento(en_10_dias)
        
        with pytest.raises(AttributeError):
            fecha.fecha = date.today() + timedelta(days=20)
    
    def test_fecha_vencimiento_hasheable(self):
        """Test que fecha de vencimiento es hasheable"""
        en_10_dias = date.today() + timedelta(days=10)
        fecha = FechaVencimiento(en_10_dias)
        conjunto = {fecha}
        assert len(conjunto) == 1
        assert fecha in conjunto
    
    def test_igualdad_fechas_vencimiento(self):
        """Test igualdad entre fechas de vencimiento"""
        en_10_dias = date.today() + timedelta(days=10)
        fecha1 = FechaVencimiento(en_10_dias)
        fecha2 = FechaVencimiento.crear_para_fecha(en_10_dias)
        assert fecha1 == fecha2


class TestFechaVencimientoCasosReales:
    """Tests con casos de uso reales del sistema"""
    
    def test_proceso_tramite_completo_60_dias(self):
        """Test proceso completo: trámite hoy → vencimiento en 60 días"""
        fecha_tramite = FechaTramite.crear_hoy()
        fecha_vencimiento = FechaVencimiento.calcular_desde_tramite(fecha_tramite)
        
        assert fecha_vencimiento.dias_restantes() == 60
        assert fecha_vencimiento.nivel_urgencia() == "normal"
        assert fecha_vencimiento.esta_vigente() == True
    
    def test_proceso_tramite_pasado_vencimiento_proximo(self):
        """Test trámite pasado con vencimiento próximo"""
        hace_55_dias = date.today() - timedelta(days=55)
        fecha_tramite = FechaTramite(hace_55_dias)
        fecha_vencimiento = FechaVencimiento.calcular_desde_tramite(fecha_tramite)
        
        # Vence en 5 días (60 - 55)
        assert fecha_vencimiento.dias_restantes() == 5
        assert fecha_vencimiento.nivel_urgencia() == "alerta"
        assert fecha_vencimiento.esta_por_vencer() == True
    
    def test_proceso_tramite_muy_pasado_vencimiento_critico(self):
        """Test trámite muy pasado con vencimiento crítico"""
        hace_59_dias = date.today() - timedelta(days=59)
        fecha_tramite = FechaTramite(hace_59_dias)
        fecha_vencimiento = FechaVencimiento.calcular_desde_tramite(fecha_tramite)
        
        # Vence mañana (60 - 59)
        assert fecha_vencimiento.dias_restantes() == 1
        assert fecha_vencimiento.nivel_urgencia() == "critica"
        assert fecha_vencimiento.es_critica() == True
    