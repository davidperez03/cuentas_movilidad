import pytest
from app.cuentas.domain.value_objects.observacion import Observacion


class TestObservacionCreacionBasica:
    """Tests para creación básica de observaciones"""
    
    def test_crear_observacion_vacia_permitida(self):
        """Test que observación vacía es permitida (diferencia con DescripcionNovedad)"""
        obs = Observacion("")
        assert obs.valor == ""
        assert obs.esta_vacia() == True
    
    def test_crear_observacion_none_permitida(self):
        """Test que observación None se convierte a vacía"""
        obs = Observacion(None)
        assert obs.valor == ""
        assert obs.esta_vacia() == True
    
    def test_crear_observacion_solo_espacios(self):
        """Test que solo espacios se normaliza a vacía"""
        obs = Observacion("   ")
        assert obs.valor == ""
        assert obs.esta_vacia() == True
    
    def test_crear_observacion_valida_simple(self):
        """Test crear observación válida simple"""
        obs = Observacion("Proceso completado sin inconvenientes")
        assert obs.valor == "Proceso completado sin inconvenientes"
        assert obs.esta_vacia() == False
        assert obs.get_numero_palabras() == 4
    
    def test_crear_observacion_multilinea(self):
        """Test crear observación multilínea"""
        texto = "Primera línea de observación.\nSegunda línea con más detalles."
        obs = Observacion(texto)
        assert obs.valor == texto
        assert obs.es_multilinea() == True
        assert obs.get_numero_lineas() == 2


class TestObservacionValidacionLongitud:
    """Tests para validación de longitud"""
    
    def test_observacion_longitud_maxima_valida(self):
        """Test observación en el límite máximo (1000 caracteres)"""
        texto_largo = "x" * 1000
        obs = Observacion(texto_largo)
        assert len(obs.valor) == 1000
    
    def test_observacion_muy_larga_error(self):
        """Test que observación muy larga genera error"""
        texto_muy_largo = "x" * 1001
        with pytest.raises(ValueError, match="no puede exceder 1000 caracteres"):
            Observacion(texto_muy_largo)
    
    def test_observacion_corta_valida(self):
        """Test que observación corta es válida (sin mínimo obligatorio)"""
        obs = Observacion("Ok")
        assert obs.valor == "Ok"
        assert obs.get_numero_caracteres() == 2


class TestObservacionNormalizacion:
    """Tests para normalización de texto"""
    
    def test_normalizar_espacios_simples(self):
        """Test normalización de espacios múltiples"""
        obs = Observacion("Proceso    completado   sin    inconvenientes")
        assert obs.valor == "Proceso completado sin inconvenientes"
    
    def test_normalizar_espacios_inicio_fin(self):
        """Test eliminación de espacios al inicio y final"""
        obs = Observacion("   Proceso completado   ")
        assert obs.valor == "Proceso completado"
    
    def test_preservar_saltos_linea(self):
        """Test que preserva saltos de línea (diferencia con DescripcionNovedad)"""
        texto = "Primera línea\nSegunda línea\nTercera línea"
        obs = Observacion(texto)
        assert "Primera línea\nSegunda línea\nTercera línea" == obs.valor
    
    def test_normalizar_lineas_vacias_multiples(self):
        """Test normalización de líneas vacías múltiples"""
        texto = "Primera línea\n\n\n\nSegunda línea"
        obs = Observacion(texto)
        assert obs.valor == "Primera línea\n\nSegunda línea"
    
    def test_normalizar_espacios_en_lineas(self):
        """Test normalización de espacios dentro de cada línea"""
        texto = "Primera   línea  con  espacios\nSegunda    línea    también"
        obs = Observacion(texto)
        assert obs.valor == "Primera línea con espacios\nSegunda línea también"
    
    def test_eliminar_caracteres_control(self):
        """Test eliminación de caracteres de control"""
        texto_con_control = "Proceso\x00completado\x7F"
        obs = Observacion(texto_con_control)
        assert obs.valor == "Proceso completado"


class TestObservacionCaracteresPermitidos:
    """Tests para validación de caracteres permitidos"""
    
    def test_caracteres_especiales_adicionales_validos(self):
        """Test que acepta caracteres adicionales permitidos en observaciones"""
        obs = Observacion("Contactar a funcionario@email.com para seguimiento del caso.")
        assert "@" in obs.valor
        assert obs.contiene_palabra_clave("email")
    
    def test_caracteres_españoles_y_basicos(self):
        """Test caracteres del español y básicos"""
        obs = Observacion("Revisión técnica: 100% completada, ñoño verificó documentación.")
        assert "ñ" in obs.valor
        assert "%" in obs.valor
        assert ":" in obs.valor
    
    def test_caracteres_no_latinos_error(self):
        """Test que rechaza caracteres no latinos"""
        with pytest.raises(ValueError, match="caracteres no permitidos"):
            Observacion("Observación con caracteres 中文 inválidos")
    
    def test_tabs_permitidos(self):
        """Test que acepta tabs (más permisivo que DescripcionNovedad)"""
        obs = Observacion("Proceso\tcompletado\tsin\tinconvenientes")
        assert "\t" in obs.valor


class TestObservacionSeguridadContenido:
    """Tests para validación de contenido sospechoso"""
    
    def test_script_tags_completos_error(self):
        """Test que rechaza script tags completos"""
        with pytest.raises(ValueError, match="contenido no permitido"):
            Observacion("Observación con <script>alert('hack')</script> malicioso")
    
    def test_javascript_url_error(self):
        """Test que rechaza JavaScript URLs"""
        with pytest.raises(ValueError, match="contenido no permitido"):
            Observacion("Ver en javascript:alert('hack') para más detalles")
    
    def test_event_handlers_con_comillas_error(self):
        """Test que rechaza event handlers con comillas"""
        with pytest.raises(ValueError, match="contenido no permitido"):
            Observacion("Revisar onclick='malicious()' en el documento")
    
    def test_html_simple_permitido(self):
        """Test que permite HTML simple/tags incompletos (más permisivo)"""
        # Menos estricto que DescripcionNovedad
        obs = Observacion("Revisar documento <pendiente> para verificación")
        assert "<pendiente>" in obs.valor


class TestObservacionMetodosEstado:
    """Tests para métodos de estado"""
    
    def test_esta_vacia_true(self):
        """Test esta_vacia para observación vacía"""
        obs_vacia = Observacion("")
        obs_espacios = Observacion("   ")
        assert obs_vacia.esta_vacia() == True
        assert obs_espacios.esta_vacia() == True
    
    def test_esta_vacia_false(self):
        """Test esta_vacia para observación con contenido"""
        obs = Observacion("Algún contenido")
        assert obs.esta_vacia() == False
    
    def test_es_multilinea_true(self):
        """Test es_multilinea para texto con saltos de línea"""
        obs = Observacion("Primera línea\nSegunda línea")
        assert obs.es_multilinea() == True
    
    def test_es_multilinea_false(self):
        """Test es_multilinea para texto de una línea"""
        obs = Observacion("Solo una línea")
        assert obs.es_multilinea() == False
    
    def test_tiene_longitud_significativa_true(self):
        """Test longitud significativa para texto largo"""
        obs = Observacion("Esta observación tiene suficiente longitud para ser considerada significativa")
        assert obs.tiene_longitud_significativa() == True
    
    def test_tiene_longitud_significativa_false(self):
        """Test longitud significativa para texto corto"""
        obs = Observacion("Corto")
        assert obs.tiene_longitud_significativa() == False
    
    def test_contiene_palabra_clave_case_insensitive(self):
        """Test búsqueda de palabra clave insensible a mayúsculas"""
        obs = Observacion("Proceso COMPLETADO exitosamente")
        assert obs.contiene_palabra_clave("completado") == True
        assert obs.contiene_palabra_clave("PROCESO") == True
        assert obs.contiene_palabra_clave("inexistente") == False


class TestObservacionContadores:
    """Tests para métodos de conteo"""
    
    def test_get_numero_caracteres(self):
        """Test conteo de caracteres incluyendo espacios"""
        obs = Observacion("Hola mundo")
        assert obs.get_numero_caracteres() == 10  # Incluye el espacio
    
    def test_get_numero_caracteres_sin_espacios(self):
        """Test conteo de caracteres sin espacios"""
        obs = Observacion("Hola mundo")
        assert obs.get_numero_caracteres_sin_espacios() == 9  # Sin el espacio
    
    def test_get_numero_palabras_vacia(self):
        """Test conteo de palabras en observación vacía"""
        obs = Observacion("")
        assert obs.get_numero_palabras() == 0
    
    def test_get_numero_palabras_normal(self):
        """Test conteo de palabras en observación normal"""
        obs = Observacion("Esta observación tiene cinco palabras")
        assert obs.get_numero_palabras() == 5
    
    def test_get_numero_lineas_vacia(self):
        """Test conteo de líneas en observación vacía"""
        obs = Observacion("")
        assert obs.get_numero_lineas() == 0
    
    def test_get_numero_lineas_multilinea(self):
        """Test conteo de líneas en observación multilínea"""
        obs = Observacion("Primera línea\nSegunda línea\n\nCuarta línea")
        assert obs.get_numero_lineas() == 3  # Solo líneas con contenido
    
    def test_get_numero_lineas_una_linea(self):
        """Test conteo de líneas en observación de una línea"""
        obs = Observacion("Solo una línea")
        assert obs.get_numero_lineas() == 1


class TestObservacionResumenes:
    """Tests para generación de resúmenes"""
    
    def test_get_resumen_observacion_vacia(self):
        """Test resumen de observación vacía"""
        obs = Observacion("")
        resumen = obs.get_resumen()
        assert resumen == "[Sin observaciones]"
    
    def test_get_resumen_texto_corto(self):
        """Test resumen de texto que no necesita truncar"""
        obs = Observacion("Proceso completado")
        resumen = obs.get_resumen(150)
        assert resumen == "Proceso completado"
        assert not resumen.endswith("...")
    
    def test_get_resumen_texto_largo(self):
        """Test resumen de texto largo que necesita truncar"""
        texto_largo = "Esta es una observación muy larga que necesita ser truncada porque supera el límite de caracteres especificado para el resumen automático"
        obs = Observacion(texto_largo)
        resumen = obs.get_resumen(50)
        
        assert len(resumen) <= 53  
        assert resumen.endswith("...")
    
    def test_get_resumen_multilinea_primera_linea(self):
        """Test resumen de texto multilínea usando primera línea"""
        obs = Observacion("Primera línea significativa con buen contenido\nSegunda línea también importante\nTercera línea")
        resumen = obs.get_resumen(100)
        
        assert resumen == "Primera línea significativa con buen contenido..."
        assert "Segunda línea" not in resumen
    
    def test_get_vista_previa_una_linea_vacia(self):
        """Test vista previa de observación vacía"""
        obs = Observacion("")
        vista = obs.get_vista_previa_una_linea()
        assert vista == ""
    
    def test_get_vista_previa_una_linea_multilinea(self):
        """Test vista previa convertir multilínea a una línea"""
        obs = Observacion("Primera línea\nSegunda línea\nTercera línea")
        vista = obs.get_vista_previa_una_linea()
        assert vista == "Primera línea Segunda línea Tercera línea"
        assert "\n" not in vista
    
    def test_get_vista_previa_una_linea_truncada(self):
        """Test vista previa truncada para texto muy largo"""
        texto_largo = "x" * 150
        obs = Observacion(texto_largo)
        vista = obs.get_vista_previa_una_linea()
        
        assert len(vista) <= 100
        assert vista.endswith("...")


class TestObservacionTimestamp:
    """Tests para funcionalidad de timestamp"""
    
    def test_agregar_timestamp_automatico_observacion_vacia(self):
        """Test agregar timestamp a observación vacía"""
        obs = Observacion("")
        obs_con_timestamp = obs.agregar_timestamp_automatico("Juan Pérez")
        
        assert "Juan Pérez" in obs_con_timestamp.valor
        assert "Sin observaciones adicionales" in obs_con_timestamp.valor
        assert "[" in obs_con_timestamp.valor  
    
    def test_agregar_timestamp_automatico_con_contenido(self):
        """Test agregar timestamp a observación con contenido"""
        obs = Observacion("Proceso completado exitosamente")
        obs_con_timestamp = obs.agregar_timestamp_automatico("María García")
        
        assert "María García" in obs_con_timestamp.valor
        assert "Proceso completado exitosamente" in obs_con_timestamp.valor
        assert obs_con_timestamp.valor.startswith("[")
    
    def test_agregar_timestamp_funcionario_vacio_error(self):
        """Test que funcionario vacío genera error"""
        obs = Observacion("Algún contenido")
        with pytest.raises(ValueError, match="funcionario no puede estar vacío"):
            obs.agregar_timestamp_automatico("")
    
    def test_es_observacion_sistema_true(self):
        """Test detección de observación del sistema"""
        obs_sistema = Observacion("[04/12/2024 10:30 - SISTEMA] Expediente asignado automáticamente")
        assert obs_sistema.es_observacion_sistema() == True
    
    def test_es_observacion_sistema_false(self):
        """Test observación manual no es del sistema"""
        obs_manual = Observacion("Observación ingresada manualmente por funcionario")
        assert obs_manual.es_observacion_sistema() == False


class TestObservacionMenciones:
    """Tests para extracción de menciones"""
    
    def test_extraer_menciones_funcionarios_simples(self):
        """Test extracción de menciones simples"""
        obs = Observacion("@juan revisar documentación y coordinar con @maria para seguimiento")
        menciones = obs.extraer_menciones_funcionarios()
        
        assert "juan" in menciones
        assert "maria" in menciones
        assert len(menciones) == 2
    
    def test_extraer_menciones_funcionarios_con_apellido(self):
        """Test extracción de menciones con apellido"""
        obs = Observacion("@juan.perez por favor verificar con @maria.garcia los documentos")
        menciones = obs.extraer_menciones_funcionarios()
        
        assert "juan.perez" in menciones
        assert "maria.garcia" in menciones
        assert len(menciones) == 2
    
    def test_extraer_menciones_sin_menciones(self):
        """Test extracción cuando no hay menciones"""
        obs = Observacion("Proceso completado sin menciones a funcionarios")
        menciones = obs.extraer_menciones_funcionarios()
        assert menciones == []
    
    def test_extraer_menciones_duplicadas(self):
        """Test que elimina menciones duplicadas"""
        obs = Observacion("@juan revisar y luego @juan confirmar proceso con @juan")
        menciones = obs.extraer_menciones_funcionarios()
        
        assert menciones == ["juan"]
        assert len(menciones) == 1
    
    def test_extraer_menciones_caracteres_especiales(self):
        """Test menciones con caracteres especiales españoles"""
        obs = Observacion("@josé.niño y @maría coordinar el proceso")
        menciones = obs.extraer_menciones_funcionarios()
        
        assert "josé.niño" in menciones
        assert "maría" in menciones


class TestObservacionFormatos:
    """Tests para formatos de salida"""
    
    def test_formato_para_reporte_vacia(self):
        """Test formato para reporte de observación vacía"""
        obs = Observacion("")
        formato = obs.formato_para_reporte()
        assert formato == "OBSERVACIONES: Sin observaciones registradas."
    
    def test_formato_para_reporte_con_contenido(self):
        """Test formato para reporte con contenido"""
        obs = Observacion("Proceso completado exitosamente")
        formato = obs.formato_para_reporte()
        assert formato == "OBSERVACIONES:\nProceso completado exitosamente"
    
    def test_formato_para_auditoria(self):
        """Test formato para auditoría con metadata"""
        obs = Observacion("Proceso completado\nSin inconvenientes")
        formato = obs.formato_para_auditoria()
        
        assert "OBSERVACION:" in formato
        assert "METADATA:" in formato
        assert "caracteres" in formato
        assert "multilinea" in formato
    
    def test_str_representation_vacia(self):
        """Test representación string de observación vacía"""
        obs = Observacion("")
        assert str(obs) == ""
    
    def test_str_representation_con_contenido(self):
        """Test representación string con contenido"""
        obs = Observacion("Algún contenido")
        assert str(obs) == "Algún contenido"
    
    def test_repr_representation_vacia(self):
        """Test representación repr de observación vacía"""
        obs = Observacion("")
        assert repr(obs) == "Observacion(vacía)"
    
    def test_repr_representation_con_contenido(self):
        """Test representación repr con contenido"""
        obs = Observacion("Proceso completado exitosamente")
        repr_str = repr(obs)
        
        assert "Observacion" in repr_str
        assert "chars=" in repr_str
        assert "words=" in repr_str


class TestObservacionFactoryMethods:
    """Tests para factory methods"""
    
    def test_vacia_factory_method(self):
        """Test factory method para observación vacía"""
        obs = Observacion.vacia()
        assert obs.esta_vacia() == True
        assert obs.valor == ""
    
    def test_crear_desde_texto(self):
        """Test factory method crear_desde_texto"""
        obs = Observacion.crear_desde_texto("Algún contenido")
        assert obs.valor == "Algún contenido"
    
    def test_crear_si_valida_exitoso(self):
        """Test factory method crear_si_valida exitoso"""
        obs = Observacion.crear_si_valida("Contenido válido")
        assert obs is not None
        assert obs.valor == "Contenido válido"
    
    def test_crear_si_valida_fallido(self):
        """Test factory method crear_si_valida fallido"""
        texto_muy_largo = "x" * 1001
        obs = Observacion.crear_si_valida(texto_muy_largo)
        assert obs is None
    
    def test_crear_con_timestamp(self):
        """Test factory method con timestamp"""
        obs = Observacion.crear_con_timestamp("Proceso completado", "Juan Pérez")
        
        assert "Juan Pérez" in obs.valor
        assert "Proceso completado" in obs.valor
        assert "[" in obs.valor
    
    def test_crear_observacion_sistema(self):
        """Test factory method para observaciones del sistema"""
        obs = Observacion.crear_observacion_sistema("Expediente asignado", "AUTO-ASIGN")
        
        assert "AUTO-ASIGN" in obs.valor
        assert "Expediente asignado" in obs.valor
        assert obs.es_observacion_sistema() == True
    
    def test_combinar_observaciones_vacias(self):
        """Test combinar observaciones cuando todas están vacías"""
        obs1 = Observacion.vacia()
        obs2 = Observacion("")
        obs3 = Observacion("   ")
        
        combinada = Observacion.combinar_observaciones([obs1, obs2, obs3])
        assert combinada.esta_vacia() == True
    
    def test_combinar_observaciones_mixtas(self):
        """Test combinar observaciones mixtas (vacías y con contenido)"""
        obs1 = Observacion("Primera observación")
        obs2 = Observacion.vacia()
        obs3 = Observacion("Tercera observación")
        
        combinada = Observacion.combinar_observaciones([obs1, obs2, obs3])
        
        assert "Primera observación" in combinada.valor
        assert "Tercera observación" in combinada.valor
        assert "---" in combinada.valor  # Separador por defecto
    
    def test_combinar_observaciones_separador_personalizado(self):
        """Test combinar observaciones con separador personalizado"""
        obs1 = Observacion("Primera")
        obs2 = Observacion("Segunda")
        
        combinada = Observacion.combinar_observaciones([obs1, obs2], separador=" | ")
        assert "Primera | Segunda" == combinada.valor
    
    def test_ejemplos_tipicos(self):
        """Test factory method para ejemplos típicos"""
        ejemplos = Observacion.ejemplos_tipicos()
        
        assert len(ejemplos) == 5
        assert any(ej.esta_vacia() for ej in ejemplos)
        assert any(ej.es_multilinea() for ej in ejemplos)
        assert any(ej.es_observacion_sistema() for ej in ejemplos)
        assert any("@" in ej.valor for ej in ejemplos)  # Menciones
    
    def test_validar_lote_observaciones(self):
        """Test validación de lote de observaciones"""
        observaciones = [
            "Observación válida normal",
            "",  # Vacía
            "x" * 1001,  # Inválida (muy larga)
            "   ",  # Vacía (solo espacios)
            "Otra observación válida",
        ]
        
        resultado = Observacion.validar_lote_observaciones(observaciones)
        
        assert len(resultado["validas"]) == 2
        assert len(resultado["vacias"]) == 2
        assert len(resultado["invalidas"]) == 1


class TestObservacionInmutabilidad:
    """Tests para inmutabilidad del value object"""
    
    def test_observacion_es_inmutable(self):
        """Test que observación no se puede modificar"""
        obs = Observacion("Contenido original")
        
        with pytest.raises(AttributeError):
            obs.valor = "Nuevo contenido"
    
    def test_observacion_hasheable(self):
        """Test que observación es hasheable"""
        obs = Observacion("Algún contenido")
        conjunto = {obs}
        assert len(conjunto) == 1
        assert obs in conjunto
    
    def test_igualdad_observaciones(self):
        """Test igualdad entre observaciones"""
        obs1 = Observacion("Proceso completado")
        obs2 = Observacion("Proceso    completado")  # Normalización
        assert obs1 == obs2


class TestObservacionCasosReales:
    """Tests con casos de uso reales del sistema"""
    
    def test_observacion_traslado_completado(self):
        """Test observación típica de traslado completado"""
        obs = Observacion("Expediente trasladado exitosamente a Sogamoso. Todos los documentos verificados y completos.")
        
        assert obs.contiene_palabra_clave("trasladado")
        assert obs.contiene_palabra_clave("Sogamoso")
        assert not obs.es_multilinea()
        assert obs.tiene_longitud_significativa()
    
    def test_observacion_con_seguimiento_multilinea(self):
        """Test observación con seguimiento en múltiples líneas"""
        obs = Observacion("""Requiere seguimiento especial por documentación incompleta.
Coordinar con oficina de destino para verificación adicional.
Notificar al propietario sobre documentos faltantes.""")
        
        assert obs.es_multilinea()
        assert obs.get_numero_lineas() == 3
        assert obs.contiene_palabra_clave("seguimiento")
        assert obs.contiene_palabra_clave("propietario")
    
    def test_observacion_con_menciones_funcionarios(self):
        """Test observación con menciones a funcionarios"""
        obs = Observacion("@supervisor.general revisar expediente antes del envío. @juan.lopez coordinar con destino.")
        
        menciones = obs.extraer_menciones_funcionarios()
        assert "supervisor.general" in menciones
        assert "juan.lopez" in menciones
        assert len(menciones) == 2
    
    def test_observacion_sistema_automatica(self):
        """Test observación generada automáticamente por el sistema"""
        obs = Observacion.crear_observacion_sistema("Expediente reasignado por vencimiento de plazo", "AUTO-REASIGN")
        
        assert obs.es_observacion_sistema()
        assert "AUTO-REASIGN" in obs.valor
        assert "vencimiento" in obs.valor
    
    def test_observacion_vacia_proceso_rutinario(self):
        """Test observación vacía para procesos rutinarios"""
        obs = Observacion.vacia()
        
        assert obs.esta_vacia()
        resumen = obs.get_resumen()
        assert resumen == "[Sin observaciones]"
        
        # Para reportes
        formato_reporte = obs.formato_para_reporte()
        assert "Sin observaciones registradas" in formato_reporte
    
    def test_historial_observaciones_combinadas(self):
        """Test combinación de observaciones para historial"""
        obs1 = Observacion.crear_con_timestamp("Expediente recibido", "María García")
        obs2 = Observacion.crear_con_timestamp("Documentos verificados", "Juan Pérez")
        obs3 = Observacion.crear_observacion_sistema("Proceso completado automáticamente")
        
        historial = Observacion.combinar_observaciones([obs1, obs2, obs3])
        
        assert "María García" in historial.valor
        assert "Juan Pérez" in historial.valor
        assert "Expediente recibido" in historial.valor
        assert "Documentos verificados" in historial.valor
        assert "completado automáticamente" in historial.valor
    
    def test_observacion_con_referencias_tecnicas(self):
        """Test observación con referencias técnicas del sistema"""
        obs = Observacion("Expediente #2024120400123 procesado. Ver RUNT para verificación de placa ABC123.")
        
        assert obs.contiene_palabra_clave("RUNT")
        assert "#2024120400123" in obs.valor
        assert "ABC123" in obs.valor
        assert obs.tiene_longitud_significativa()
    
    def test_observacion_urgente_con_formato(self):
        """Test observación urgente con formato especial"""
        obs = Observacion("⚠️ URGENTE: Documentación vencida requiere acción inmediata. Contactar propietario antes del viernes.")
        
        assert "⚠️" in obs.valor
        assert obs.contiene_palabra_clave("URGENTE")
        assert obs.contiene_palabra_clave("viernes")
        
        vista = obs.get_vista_previa_una_linea()
        assert "⚠️ URGENTE" in vista