import pytest
from app.cuentas.domain.value_objects.descripcion_novedad import DescripcionNovedad


class TestDescripcionNovedadCreacion:
    """Tests para creación básica de descripciones"""
    
    def test_crear_descripcion_valida_minima(self):
        """Test crear descripción con longitud mínima válida"""
        desc = DescripcionNovedad("Documento faltante en expediente")
        assert desc.valor == "Documento faltante en expediente"
        assert desc.get_numero_palabras() == 4
    
    def test_crear_descripcion_valida_normal(self):
        """Test crear descripción normal"""
        texto = "La firma en el documento de traspaso no coincide con la registrada en la cédula de ciudadanía del propietario."
        desc = DescripcionNovedad(texto)
        assert desc.valor == texto
        assert desc.get_numero_palabras() == 19
    
    def test_crear_descripcion_valida_maxima(self):
        """Test crear descripción con longitud máxima"""
        texto = "x" * 500
        desc = DescripcionNovedad(texto)
        assert len(desc.valor) == 500
    
    def test_descripcion_vacia_error(self):
        """Test que descripción vacía genera error"""
        with pytest.raises(ValueError, match="no puede estar vacía"):
            DescripcionNovedad("")
    
    def test_descripcion_none_error(self):
        """Test que descripción None genera error"""
        with pytest.raises(ValueError, match="no puede estar vacía"):
            DescripcionNovedad(None)
    
    def test_descripcion_solo_espacios_error(self):
        """Test que solo espacios genera error"""
        with pytest.raises(ValueError, match="no puede estar vacía"):
            DescripcionNovedad("   ")


class TestDescripcionNovedadValidacionLongitud:
    """Tests para validación de longitud"""
    
    def test_descripcion_muy_corta_error(self):
        """Test que descripción muy corta genera error"""
        with pytest.raises(ValueError, match="debe tener entre 10 y 500 caracteres"):
            DescripcionNovedad("Muy corto") 
    
    def test_descripcion_muy_larga_error(self):
        """Test que descripción muy larga genera error"""
        texto_largo = "x" * 501
        with pytest.raises(ValueError, match="debe tener entre 10 y 500 caracteres"):
            DescripcionNovedad(texto_largo)
    
    def test_longitud_limite_inferior_valida(self):
        """Test longitud en límite inferior (10 caracteres)"""
        desc = DescripcionNovedad("Documento.") 
        assert len(desc.valor) == 10
    
    def test_longitud_limite_superior_valida(self):
        """Test longitud en límite superior (500 caracteres)"""
        texto = "x" * 500
        desc = DescripcionNovedad(texto)
        assert len(desc.valor) == 500


class TestDescripcionNovedadNormalizacion:
    """Tests para normalización de texto"""
    
    def test_normalizar_espacios_multiples(self):
        """Test normalización de espacios múltiples"""
        desc = DescripcionNovedad("Documento    faltante   en     expediente")
        assert desc.valor == "Documento faltante en expediente"
    
    def test_normalizar_espacios_inicio_fin(self):
        """Test eliminación de espacios al inicio y final"""
        desc = DescripcionNovedad("   Documento faltante en expediente   ")
        assert desc.valor == "Documento faltante en expediente"
    
    def test_normalizar_capitalizacion_oraciones(self):
        """Test capitalización de oraciones"""
        desc = DescripcionNovedad("documento faltante. firma incorrecta. datos inconsistentes.")
        assert desc.valor == "Documento faltante. Firma incorrecta. Datos inconsistentes."
    
    def test_normalizar_caracteres_control(self):
        """Test eliminación de caracteres de control"""
        texto_con_control = "Documento\x00faltante\x7Fen\x1Fexpediente"
        desc = DescripcionNovedad(texto_con_control)
        assert desc.valor == "Documento faltante en expediente"


class TestDescripcionNovedadCaracteresPermitidos:
    """Tests para validación de caracteres permitidos"""
    
    def test_caracteres_españoles_validos(self):
        """Test que acepta caracteres del español"""
        desc = DescripcionNovedad("Documentación faltante: cédula, póliza SOAT y certificación médica vigente.")
        assert "ó" in desc.valor
        assert "é" in desc.valor
    
    def test_numeros_y_simbolos_basicos_validos(self):
        """Test que acepta números y símbolos básicos"""
        desc = DescripcionNovedad("Placa ABC-123: documento vencido hace 30 días (verificado 15/11/2024).")
        assert "123" in desc.valor
        assert "-" in desc.valor
        assert "/" in desc.valor
        assert "(" in desc.valor
    
    def test_caracteres_especiales_validos(self):
        """Test caracteres especiales permitidos"""
        desc = DescripcionNovedad("Faltan: 50% documentos, $500.000 multa, 25°C temperatura, #123 expediente.")
        assert "%" in desc.valor
        assert "$" in desc.valor
        assert "°" in desc.valor
        assert "#" in desc.valor
    
    def test_caracteres_no_latinos_error(self):
        """Test que rechaza caracteres no latinos"""
        with pytest.raises(ValueError, match="caracteres no permitidos"):
            DescripcionNovedad("Documento con caracteres 中文 inválidos")
    
    def test_caracteres_especiales_raros_error(self):
        """Test que rechaza caracteres especiales raros"""
        with pytest.raises(ValueError, match="caracteres no permitidos"):
            DescripcionNovedad("Documento con símbolos ™®© inválidos")


class TestDescripcionNovedadSeguridadContenido:
    """Tests para validación de contenido sospechoso"""
    
    def test_html_tags_error(self):
        """Test que rechaza tags HTML"""
        with pytest.raises(ValueError, match="contenido no permitido"):
            DescripcionNovedad("Documento <script>alert('hack')</script> faltante")
    
    def test_javascript_error(self):
        """Test que rechaza JavaScript"""
        with pytest.raises(ValueError, match="contenido no permitido"):
            DescripcionNovedad("Documento javascript:alert('hack') faltante")
    
    def test_event_handlers_error(self):
        """Test que rechaza event handlers"""
        with pytest.raises(ValueError, match="contenido no permitido"):
            DescripcionNovedad("Documento onclick=malicious() faltante")
    
    def test_funciones_peligrosas_error(self):
        """Test que rechaza funciones peligrosas"""
        funciones_peligrosas = [
            "Documento eval(code) faltante",
            "Documento document.write(hack) faltante", 
            "Documento window.location=hack faltante",
            "Documento alert(hack) faltante"
        ]
        
        for funcion in funciones_peligrosas:
            with pytest.raises(ValueError, match="contenido no permitido"):
                DescripcionNovedad(funcion)


class TestDescripcionNovedadMetodosAnalisis:
    """Tests para métodos de análisis de texto"""
    
    def test_es_corta_true(self):
        """Test es_corta para descripción corta"""
        desc = DescripcionNovedad("Documento faltante en expediente completo")  # < 50 caracteres
        assert desc.es_corta() == True
    
    def test_es_corta_false(self):
        """Test es_corta para descripción no corta"""
        desc = DescripcionNovedad("Esta es una descripción mucho más larga que supera fácilmente los cincuenta caracteres requeridos")
        assert desc.es_corta() == False
    
    def test_es_detallada_true(self):
        """Test es_detallada para descripción larga"""
        texto_largo = "Esta es una descripción extremadamente detallada que incluye múltiples aspectos del problema encontrado en el expediente, con explicaciones específicas sobre cada documento faltante, las inconsistencias detectadas y las acciones requeridas para la corrección."
        desc = DescripcionNovedad(texto_largo)
        assert desc.es_detallada() == True
        assert len(desc.valor) > 200
    
    def test_es_detallada_false(self):
        """Test es_detallada para descripción no tan larga"""
        desc = DescripcionNovedad("Documento faltante en expediente")
        assert desc.es_detallada() == False
    
    def test_contiene_palabra_clave_true(self):
        """Test búsqueda de palabra clave exitosa"""
        desc = DescripcionNovedad("La documentación del vehículo presenta inconsistencias importantes")
        assert desc.contiene_palabra_clave("vehículo") == True
        assert desc.contiene_palabra_clave("VEHICULO") == True  
    
    def test_contiene_palabra_clave_false(self):
        """Test búsqueda de palabra clave fallida"""
        desc = DescripcionNovedad("Documento faltante en expediente")
        assert desc.contiene_palabra_clave("motocicleta") == False
    
    def test_get_numero_palabras(self):
        """Test conteo de palabras"""
        desc = DescripcionNovedad("La documentación del vehículo presenta inconsistencias")
        assert desc.get_numero_palabras() == 6
    
    def test_get_numero_oraciones(self):
        """Test conteo de oraciones"""
        desc = DescripcionNovedad("Documento faltante. Firma incorrecta. Datos inconsistentes.")
        assert desc.get_numero_oraciones() == 3
    
    def test_get_numero_oraciones_sin_punto_final(self):
        """Test conteo de oraciones sin punto final"""
        desc = DescripcionNovedad("Documento faltante. Firma incorrecta")
        assert desc.get_numero_oraciones() == 2


class TestDescripcionNovedadResumen:
    """Tests para generación de resúmenes"""
    
    def test_get_resumen_texto_corto(self):
        """Test resumen de texto que no necesita truncar"""
        desc = DescripcionNovedad("Documento faltante")
        resumen = desc.get_resumen(100)
        assert resumen == "Documento faltante"
        assert not resumen.endswith("...")
    
    def test_get_resumen_texto_largo(self):
        """Test resumen de texto largo que necesita truncar"""
        texto_largo = "Esta es una descripción muy larga que necesita ser truncada porque supera el límite de caracteres especificado para el resumen"
        desc = DescripcionNovedad(texto_largo)
        resumen = desc.get_resumen(50)
        
        assert len(resumen) <= 53  # 50 + "..."
        assert resumen.endswith("...")
        assert not resumen[:-3].endswith(" ")  # No debe terminar en espacio antes de "..."
    
    def test_get_resumen_longitud_personalizada(self):
        """Test resumen con longitud personalizada"""
        desc = DescripcionNovedad("Esta es una descripción de longitud media que permite testing")
        resumen = desc.get_resumen(30)
        assert len(resumen) <= 33  # 30 + "..."


class TestDescripcionNovedadSimilitud:
    """Tests para comparación de similitud"""
    
    def test_es_similar_a_identicas(self):
        """Test similitud entre descripciones idénticas"""
        desc1 = DescripcionNovedad("Documento faltante en expediente")
        desc2 = DescripcionNovedad("Documento faltante en expediente")
        assert desc1.es_similar_a(desc2) == True
    
    def test_es_similar_a_muy_parecidas(self):
        """Test similitud entre descripciones muy parecidas"""
        desc1 = DescripcionNovedad("Documento faltante en expediente completo")
        desc2 = DescripcionNovedad("Expediente completo con documento faltante")
        assert desc1.es_similar_a(desc2, umbral_similitud=0.6) == True
    
    def test_es_similar_a_diferentes(self):
        """Test similitud entre descripciones diferentes"""
        desc1 = DescripcionNovedad("Documento faltante en expediente")
        desc2 = DescripcionNovedad("Firma incorrecta en certificado médico vigente")
        assert desc1.es_similar_a(desc2) == False
    
    def test_es_similar_a_umbral_personalizado(self):
        """Test similitud con umbral personalizado"""
        desc1 = DescripcionNovedad("Documento principal faltante")
        desc2 = DescripcionNovedad("Documento secundario presente")
        
        assert desc1.es_similar_a(desc2, umbral_similitud=0.2) == True  
        assert desc1.es_similar_a(desc2, umbral_similitud=0.8) == False  


class TestDescripcionNovedadFormatos:
    """Tests para formatos de salida"""
    
    def test_formato_para_reporte(self):
        """Test formato para reportes oficiales"""
        desc = DescripcionNovedad("Documento faltante en expediente")
        formato = desc.formato_para_reporte()
        assert formato == "DESCRIPCIÓN: Documento faltante en expediente"
    
    def test_str_representation(self):
        """Test representación string"""
        desc = DescripcionNovedad("Documento faltante en expediente")
        assert str(desc) == "Documento faltante en expediente"
    
    def test_repr_representation(self):
        """Test representación repr"""
        desc = DescripcionNovedad("Documento faltante en expediente")
        repr_str = repr(desc)
        assert "DescripcionNovedad" in repr_str
        assert "palabras=4" in repr_str
    
    def test_repr_con_resumen_largo(self):
        """Test repr con descripción que necesita resumen"""
        texto_largo = "Esta es una descripción muy larga que será truncada en la representación repr"
        desc = DescripcionNovedad(texto_largo)
        repr_str = repr(desc)
        assert "..." in repr_str


class TestDescripcionNovedadFactoryMethods:
    """Tests para factory methods"""
    
    def test_crear_desde_texto_valido(self):
        """Test factory method crear_desde_texto"""
        desc = DescripcionNovedad.crear_desde_texto("Documento faltante en expediente")
        assert desc.valor == "Documento faltante en expediente"
    
    def test_crear_desde_texto_invalido(self):
        """Test factory method con texto inválido"""
        with pytest.raises(ValueError):
            DescripcionNovedad.crear_desde_texto("Corto")
    
    def test_crear_si_valida_exitoso(self):
        """Test factory method crear_si_valida exitoso"""
        desc = DescripcionNovedad.crear_si_valida("Documento faltante en expediente")
        assert desc is not None
        assert desc.valor == "Documento faltante en expediente"
    
    def test_crear_si_valida_fallido(self):
        """Test factory method crear_si_valida fallido"""
        desc = DescripcionNovedad.crear_si_valida("Corto")
        assert desc is None
    
    def test_crear_con_prefijo_tipo(self):
        """Test factory method con prefijo de tipo"""
        desc = DescripcionNovedad.crear_con_prefijo_tipo(
            "DOCUMENTO_FALTANTE", 
            "cedula de ciudadania del propietario"
        )
        assert desc.valor == "Documento faltante: cedula de ciudadania del propietario"
    
    def test_ejemplos_validos(self):
        """Test factory method para ejemplos válidos"""
        ejemplos = DescripcionNovedad.ejemplos_validos()
        assert len(ejemplos) == 5
        assert all(isinstance(ej, DescripcionNovedad) for ej in ejemplos)
        assert all(len(ej.valor) >= 10 for ej in ejemplos)
    
    def test_validar_grupo_descripciones(self):
        """Test validación de grupo de descripciones"""
        descripciones = [
            "Documento faltante en expediente completo",  # Válida
            "Corto",  # Inválida (muy corta)
            "Firma incorrecta en certificado médico vigente actualizado",  # Válida
            "",  # Inválida (vacía)
        ]
        
        resultado = DescripcionNovedad.validar_grupo_descripciones(descripciones)
        
        assert len(resultado["validas"]) == 2
        assert len(resultado["invalidas"]) == 2
        assert "Documento faltante en expediente completo" in resultado["validas"]
        assert "Corto" in resultado["invalidas"]


class TestDescripcionNovedadInmutabilidad:
    """Tests para inmutabilidad del value object"""
    
    def test_descripcion_es_inmutable(self):
        """Test que descripción no se puede modificar"""
        desc = DescripcionNovedad("Documento faltante en expediente")
        
        with pytest.raises(AttributeError):
            desc.valor = "Nuevo valor"
    
    def test_descripcion_hasheable(self):
        """Test que descripción es hasheable"""
        desc = DescripcionNovedad("Documento faltante en expediente")
        conjunto = {desc}
        assert len(conjunto) == 1
        assert desc in conjunto
    
    def test_igualdad_descripciones(self):
        """Test igualdad entre descripciones"""
        desc1 = DescripcionNovedad("Documento faltante en expediente")
        desc2 = DescripcionNovedad("documento   faltante en  expediente")  # Normalización
        assert desc1 == desc2


class TestDescripcionNovedadCasosReales:
    """Tests con casos de uso reales del sistema"""
    
    def test_descripcion_documento_faltante(self):
        """Test descripción típica de documento faltante"""
        desc = DescripcionNovedad("La cédula de ciudadanía del propietario no se encuentra adjunta al expediente según verificación realizada.")
        
        assert desc.contiene_palabra_clave("cédula")
        assert desc.contiene_palabra_clave("propietario")
        assert desc.get_numero_palabras() == 15
        assert not desc.es_corta()
    
    def test_descripcion_firma_incorrecta(self):
        """Test descripción de firma incorrecta"""
        desc = DescripcionNovedad("La firma registrada en el documento de traspaso no coincide con la firma de la cédula de ciudadanía.")
        
        assert desc.contiene_palabra_clave("firma")
        assert desc.contiene_palabra_clave("traspaso")
        assert desc.es_detallada() == False
        assert desc.get_numero_oraciones() == 1
    
    def test_descripcion_soat_vencido(self):
        """Test descripción de SOAT vencido"""
        desc = DescripcionNovedad("La póliza SOAT se encuentra vencida desde el 15/03/2024 según consulta en plataforma FASECOLDA.")
        
        assert desc.contiene_palabra_clave("SOAT")
        assert desc.contiene_palabra_clave("vencida")
        assert "15/03/2024" in desc.valor
        
    def test_descripcion_datos_inconsistentes(self):
        """Test descripción de datos inconsistentes"""
        desc = DescripcionNovedad("Los datos del vehículo registrados en RUNT no coinciden con la información física verificada en el automotor.")
        
        assert desc.contiene_palabra_clave("RUNT")
        assert desc.contiene_palabra_clave("vehículo")
        assert desc.get_numero_palabras() > 10
    
    def test_multiples_descripciones_similares(self):
        """Test detección de descripciones similares en lote"""
        descripciones = [
            DescripcionNovedad("Documento de identidad faltante en expediente principal"),
            DescripcionNovedad("Expediente principal sin documento de identidad"),
            DescripcionNovedad("Certificado médico vencido hace tres meses"),
        ]

        assert descripciones[0].es_similar_a(descripciones[1], 0.6) == True
        assert descripciones[0].es_similar_a(descripciones[2], 0.6) == False