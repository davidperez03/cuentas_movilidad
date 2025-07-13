import pytest
from app.cuentas.domain.value_objects.enums.tipo_proceso_anterior import TipoProcesoAnterior


class TestTipoProcesoAnteriorEnum:
    """Tests para el enum TipoProcesoAnterior"""
    
    def test_valores_enum_correctos(self):
        """Verificar que los valores del enum son correctos"""
        assert TipoProcesoAnterior.NINGUNO.value == "ninguno"
        assert TipoProcesoAnterior.TRASLADO_COMPLETADO.value == "traslado_completado"
        assert TipoProcesoAnterior.TRASLADO_DEVUELTO.value == "traslado_devuelto"
        assert TipoProcesoAnterior.RADICACION_COMPLETADA.value == "radicacion_completada"
        assert TipoProcesoAnterior.RADICACION_DEVUELTA.value == "radicacion_devuelta"
    
    def test_enum_es_inmutable(self):
        """Verificar que los valores del enum no se pueden cambiar"""
        with pytest.raises(AttributeError):
            TipoProcesoAnterior.NINGUNO.value = "nuevo_valor"
    
    def test_todos_los_tipos_disponibles(self):
        """Verificar que tenemos todos los tipos necesarios"""
        tipos_esperados = [
            "ninguno", "traslado_completado", "traslado_devuelto",
            "radicacion_completada", "radicacion_devuelta"
        ]
        tipos_reales = [tipo.value for tipo in TipoProcesoAnterior]
        assert len(tipos_reales) == 5
        for tipo in tipos_esperados:
            assert tipo in tipos_reales
    
    def test_cobertura_completa_estados(self):
        """Verificar que cubrimos todos los estados posibles del negocio"""
        # Estados de traslado
        assert TipoProcesoAnterior.TRASLADO_COMPLETADO in TipoProcesoAnterior
        assert TipoProcesoAnterior.TRASLADO_DEVUELTO in TipoProcesoAnterior
        
        # Estados de radicación
        assert TipoProcesoAnterior.RADICACION_COMPLETADA in TipoProcesoAnterior
        assert TipoProcesoAnterior.RADICACION_DEVUELTA in TipoProcesoAnterior
        
        # Estado inicial
        assert TipoProcesoAnterior.NINGUNO in TipoProcesoAnterior


class TestPermiteTraslado:
    """Tests para el método permite_traslado()"""
    
    def test_ninguno_permite_traslado(self):
        """Cuenta nueva (NINGUNO) permite traslado"""
        assert TipoProcesoAnterior.NINGUNO.permite_traslado() == True
    
    def test_radicacion_completada_permite_traslado(self):
        """Después de radicación completada permite traslado"""
        assert TipoProcesoAnterior.RADICACION_COMPLETADA.permite_traslado() == True
    
    def test_traslado_devuelto_permite_traslado(self):
        """Traslado devuelto permite reintentar traslado"""
        assert TipoProcesoAnterior.TRASLADO_DEVUELTO.permite_traslado() == True
    
    def test_radicacion_devuelta_permite_traslado(self):
        """Radicación devuelta permite traslado"""
        assert TipoProcesoAnterior.RADICACION_DEVUELTA.permite_traslado() == True
    
    def test_traslado_completado_no_permite_traslado(self):
        """Traslado ya completado NO permite otro traslado"""
        assert TipoProcesoAnterior.TRASLADO_COMPLETADO.permite_traslado() == False
    
    def test_logica_negocio_traslado_completado(self):
        """Verificar lógica de negocio: si enviaste, no puedes enviar de nuevo"""
        # Una placa que ya se trasladó a otro organismo no puede trasladarse de nuevo
        # (lógica de origen/destino del sistema)
        assert TipoProcesoAnterior.TRASLADO_COMPLETADO.permite_traslado() == False


class TestPermiteRadicacion:
    """Tests para el método permite_radicacion()"""
    
    def test_ninguno_permite_radicacion(self):
        """Cuenta nueva (NINGUNO) permite radicación"""
        assert TipoProcesoAnterior.NINGUNO.permite_radicacion() == True
    
    def test_traslado_completado_permite_radicacion(self):
        """Después de traslado completado permite radicación"""
        assert TipoProcesoAnterior.TRASLADO_COMPLETADO.permite_radicacion() == True
    
    def test_traslado_devuelto_permite_radicacion(self):
        """Traslado devuelto permite radicación"""
        assert TipoProcesoAnterior.TRASLADO_DEVUELTO.permite_radicacion() == True
    
    def test_radicacion_devuelta_permite_radicacion(self):
        """Radicación devuelta permite reintentar radicación"""
        assert TipoProcesoAnterior.RADICACION_DEVUELTA.permite_radicacion() == True
    
    def test_radicacion_completada_no_permite_radicacion(self):
        """Radicación ya completada NO permite otra radicación"""
        assert TipoProcesoAnterior.RADICACION_COMPLETADA.permite_radicacion() == False
    
    def test_logica_negocio_radicacion_completada(self):
        """Verificar lógica de negocio: si recibiste, no puedes recibir de nuevo"""
        # Una placa que ya se radicó desde otro organismo no puede radicarse de nuevo
        # (lógica de origen/destino del sistema)
        assert TipoProcesoAnterior.RADICACION_COMPLETADA.permite_radicacion() == False


class TestLogicaOrigenDestino:
    """Tests para la lógica completa de origen/destino"""
    
    def test_exclusividad_mutua_completados(self):
        """Procesos completados son mutuamente excluyentes"""
        # Si completaste traslado, solo puedes radicar
        traslado_completado = TipoProcesoAnterior.TRASLADO_COMPLETADO
        assert traslado_completado.permite_traslado() == False
        assert traslado_completado.permite_radicacion() == True
        
        # Si completaste radicación, solo puedes trasladar
        radicacion_completada = TipoProcesoAnterior.RADICACION_COMPLETADA
        assert radicacion_completada.permite_traslado() == True
        assert radicacion_completada.permite_radicacion() == False
    
    def test_devoluciones_rompen_restriccion(self):
        """Devoluciones permiten ambos procesos (rompen restricción)"""
        devoluciones = [
            TipoProcesoAnterior.TRASLADO_DEVUELTO,
            TipoProcesoAnterior.RADICACION_DEVUELTA
        ]
        
        for tipo in devoluciones:
            assert tipo.permite_traslado() == True
            assert tipo.permite_radicacion() == True
    
    def test_cuenta_nueva_permite_ambos(self):
        """Cuenta nueva permite ambos procesos"""
        ninguno = TipoProcesoAnterior.NINGUNO
        assert ninguno.permite_traslado() == True
        assert ninguno.permite_radicacion() == True
    
    def test_matriz_completa_permisos(self):
        """Test matriz completa de permisos"""
        matriz_esperada = {
            TipoProcesoAnterior.NINGUNO: (True, True),
            TipoProcesoAnterior.TRASLADO_COMPLETADO: (False, True),
            TipoProcesoAnterior.TRASLADO_DEVUELTO: (True, True),
            TipoProcesoAnterior.RADICACION_COMPLETADA: (True, False),
            TipoProcesoAnterior.RADICACION_DEVUELTA: (True, True)
        }
        
        for tipo, (permite_tras, permite_rad) in matriz_esperada.items():
            assert tipo.permite_traslado() == permite_tras, f"{tipo} debería permitir traslado: {permite_tras}"
            assert tipo.permite_radicacion() == permite_rad, f"{tipo} debería permitir radicación: {permite_rad}"


class TestGetDescripcion:
    """Tests para el método get_descripcion()"""
    
    def test_descripciones_legibles(self):
        """Verificar que todas las descripciones son legibles"""
        descripciones_esperadas = {
            TipoProcesoAnterior.NINGUNO: "Sin procesos anteriores",
            TipoProcesoAnterior.TRASLADO_COMPLETADO: "Traslado completado exitosamente",
            TipoProcesoAnterior.TRASLADO_DEVUELTO: "Traslado devuelto por administración",
            TipoProcesoAnterior.RADICACION_COMPLETADA: "Radicación completada exitosamente",
            TipoProcesoAnterior.RADICACION_DEVUELTA: "Radicación devuelta por administración"
        }
        
        for tipo, descripcion_esperada in descripciones_esperadas.items():
            assert tipo.get_descripcion() == descripcion_esperada
    
    def test_descripciones_no_vacias(self):
        """Verificar que ninguna descripción está vacía"""
        for tipo in TipoProcesoAnterior:
            descripcion = tipo.get_descripcion()
            assert descripcion is not None
            assert len(descripcion.strip()) > 0
    
    def test_descripciones_contienen_info_util(self):
        """Verificar que las descripciones contienen información útil"""
        # Descripciones de completados deben mencionar "exitosamente"
        assert "exitosamente" in TipoProcesoAnterior.TRASLADO_COMPLETADO.get_descripcion()
        assert "exitosamente" in TipoProcesoAnterior.RADICACION_COMPLETADA.get_descripcion()
        
        # Descripciones de devueltos deben mencionar "devuelto"
        assert "devuelto" in TipoProcesoAnterior.TRASLADO_DEVUELTO.get_descripcion()
        assert "devuelta" in TipoProcesoAnterior.RADICACION_DEVUELTA.get_descripcion()
        
        # Descripción de ninguno debe indicar falta de procesos
        assert "Sin procesos" in TipoProcesoAnterior.NINGUNO.get_descripcion()


class TestEsCompletadoExitosamente:
    """Tests para el método es_completado_exitosamente()"""
    
    def test_completados_exitosamente_true(self):
        """Procesos completados exitosamente retornan True"""
        completados = [
            TipoProcesoAnterior.TRASLADO_COMPLETADO,
            TipoProcesoAnterior.RADICACION_COMPLETADA
        ]
        
        for tipo in completados:
            assert tipo.es_completado_exitosamente() == True
    
    def test_no_completados_exitosamente_false(self):
        """Procesos no completados exitosamente retornan False"""
        no_completados = [
            TipoProcesoAnterior.NINGUNO,
            TipoProcesoAnterior.TRASLADO_DEVUELTO,
            TipoProcesoAnterior.RADICACION_DEVUELTA
        ]
        
        for tipo in no_completados:
            assert tipo.es_completado_exitosamente() == False
    
    def test_completados_vs_devueltos_mutuamente_excluyentes(self):
        """Completados y devueltos son mutuamente excluyentes"""
        for tipo in TipoProcesoAnterior:
            es_completado = tipo.es_completado_exitosamente()
            es_devuelto = tipo.es_devuelto()
            
            # No puede ser ambos a la vez (excepto NINGUNO que no es ninguno)
            if tipo != TipoProcesoAnterior.NINGUNO:
                assert not (es_completado and es_devuelto), f"{tipo} no puede ser completado Y devuelto"


class TestEsDevuelto:
    """Tests para el método es_devuelto()"""
    
    def test_devueltos_true(self):
        """Procesos devueltos retornan True"""
        devueltos = [
            TipoProcesoAnterior.TRASLADO_DEVUELTO,
            TipoProcesoAnterior.RADICACION_DEVUELTA
        ]
        
        for tipo in devueltos:
            assert tipo.es_devuelto() == True
    
    def test_no_devueltos_false(self):
        """Procesos no devueltos retornan False"""
        no_devueltos = [
            TipoProcesoAnterior.NINGUNO,
            TipoProcesoAnterior.TRASLADO_COMPLETADO,
            TipoProcesoAnterior.RADICACION_COMPLETADA
        ]
        
        for tipo in no_devueltos:
            assert tipo.es_devuelto() == False
    
    def test_logica_devolucion_permite_reintentos(self):
        """Lógica de negocio: devueltos permiten reintentar ambos procesos"""
        for tipo in TipoProcesoAnterior:
            if tipo.es_devuelto():
                assert tipo.permite_traslado() == True
                assert tipo.permite_radicacion() == True


class TestGetProcesoContrarioPermitido:
    """Tests para el método get_proceso_contrario_permitido()"""
    
    def test_traslado_completado_permite_radicacion(self):
        """Traslado completado permite radicación como proceso contrario"""
        tipo = TipoProcesoAnterior.TRASLADO_COMPLETADO
        assert tipo.get_proceso_contrario_permitido() == "radicacion"
    
    def test_radicacion_completada_permite_traslado(self):
        """Radicación completada permite traslado como proceso contrario"""
        tipo = TipoProcesoAnterior.RADICACION_COMPLETADA
        assert tipo.get_proceso_contrario_permitido() == "traslado"
    
    def test_devueltos_permiten_ambos(self):
        """Procesos devueltos permiten ambos como proceso contrario"""
        devueltos = [
            TipoProcesoAnterior.TRASLADO_DEVUELTO,
            TipoProcesoAnterior.RADICACION_DEVUELTA
        ]
        
        for tipo in devueltos:
            assert tipo.get_proceso_contrario_permitido() == "ambos"
    
    def test_ninguno_permite_ambos(self):
        """NINGUNO permite ambos como proceso contrario"""
        assert TipoProcesoAnterior.NINGUNO.get_proceso_contrario_permitido() == "ambos"
    
    def test_consistencia_con_metodos_permite(self):
        """Verificar consistencia con métodos permite_traslado/permite_radicacion"""
        for tipo in TipoProcesoAnterior:
            proceso_contrario = tipo.get_proceso_contrario_permitido()
            permite_traslado = tipo.permite_traslado()
            permite_radicacion = tipo.permite_radicacion()
            
            if proceso_contrario == "traslado":
                assert permite_traslado == True
                assert permite_radicacion == False
            elif proceso_contrario == "radicacion":
                assert permite_traslado == False
                assert permite_radicacion == True
            elif proceso_contrario == "ambos":
                assert permite_traslado == True
                assert permite_radicacion == True
            elif proceso_contrario == "ninguno":
                assert permite_traslado == False
                assert permite_radicacion == False
    
    def test_valores_retorno_validos(self):
        """Verificar que solo retorna valores válidos"""
        valores_validos = {"traslado", "radicacion", "ambos", "ninguno"}
        
        for tipo in TipoProcesoAnterior:
            resultado = tipo.get_proceso_contrario_permitido()
            assert resultado in valores_validos, f"{tipo} retornó valor inválido: {resultado}"


class TestCasosRealesNegocio:
    """Tests con casos de uso reales del sistema"""
    
    def test_flujo_traslado_exitoso(self):
        """Test flujo completo: cuenta nueva → traslado exitoso → solo puede radicar"""
        # Cuenta nueva
        cuenta_nueva = TipoProcesoAnterior.NINGUNO
        assert cuenta_nueva.permite_traslado() == True
        assert cuenta_nueva.permite_radicacion() == True
        assert cuenta_nueva.get_proceso_contrario_permitido() == "ambos"
        
        # Después de traslado exitoso
        traslado_exitoso = TipoProcesoAnterior.TRASLADO_COMPLETADO
        assert traslado_exitoso.permite_traslado() == False  # Ya se trasladó
        assert traslado_exitoso.permite_radicacion() == True  # Ahora debe venir de vuelta
        assert traslado_exitoso.get_proceso_contrario_permitido() == "radicacion"
    
    def test_flujo_radicacion_exitosa(self):
        """Test flujo completo: cuenta nueva → radicación exitosa → solo puede trasladar"""
        # Después de radicación exitosa
        radicacion_exitosa = TipoProcesoAnterior.RADICACION_COMPLETADA
        assert radicacion_exitosa.permite_traslado() == True  # Ahora debe irse
        assert radicacion_exitosa.permite_radicacion() == False  # Ya se radicó
        assert radicacion_exitosa.get_proceso_contrario_permitido() == "traslado"
    
    def test_flujo_devolucion_administrativa(self):
        """Test flujo: intento → devolución admin → puede reintentar cualquiera"""
        devoluciones = [
            TipoProcesoAnterior.TRASLADO_DEVUELTO,
            TipoProcesoAnterior.RADICACION_DEVUELTA
        ]
        
        for devolucion in devoluciones:
            # Después de devolución puede hacer cualquier proceso
            assert devolucion.permite_traslado() == True
            assert devolucion.permite_radicacion() == True
            assert devolucion.get_proceso_contrario_permitido() == "ambos"
            assert devolucion.es_devuelto() == True
            assert devolucion.es_completado_exitosamente() == False
    
    def test_casos_restriccion_origen_destino(self):
        """Test casos específicos de restricción origen/destino"""
        # Caso 1: Placa vino de Bogotá (radicación completada) → solo puede ir a otro lado (traslado)
        placa_de_bogota = TipoProcesoAnterior.RADICACION_COMPLETADA
        assert placa_de_bogota.permite_traslado() == True
        assert placa_de_bogota.permite_radicacion() == False
        
        # Caso 2: Placa se envió a Medellín (traslado completado) → solo puede venir de vuelta (radicación)
        placa_enviada_medellin = TipoProcesoAnterior.TRASLADO_COMPLETADO
        assert placa_enviada_medellin.permite_traslado() == False
        assert placa_enviada_medellin.permite_radicacion() == True
        
        # Caso 3: Proceso devuelto por admin → se "resetea" la restricción
        proceso_devuelto = TipoProcesoAnterior.TRASLADO_DEVUELTO
        assert proceso_devuelto.permite_traslado() == True
        assert proceso_devuelto.permite_radicacion() == True
    
    def test_validacion_reglas_negocio_completas(self):
        """Test validación completa de reglas de negocio del sistema"""
        # Regla 1: Una placa no puede tener traslado Y radicación simultáneamente
        # (esto se refleja en que los completados son mutuamente excluyentes)
        
        # Regla 2: Si una placa llegó de otro organismo → Solo puede irse
        radicacion_completada = TipoProcesoAnterior.RADICACION_COMPLETADA
        assert radicacion_completada.permite_traslado() == True
        assert radicacion_completada.permite_radicacion() == False
        
        # Regla 3: Si una placa se envió a otro organismo → Solo puede regresar
        traslado_completado = TipoProcesoAnterior.TRASLADO_COMPLETADO
        assert traslado_completado.permite_traslado() == False
        assert traslado_completado.permite_radicacion() == True
        
        # Regla 4: Excepción - Si el proceso fue DEVUELTO → Puede hacer el contrario
        for devuelto in [TipoProcesoAnterior.TRASLADO_DEVUELTO, TipoProcesoAnterior.RADICACION_DEVUELTA]:
            assert devuelto.permite_traslado() == True
            assert devuelto.permite_radicacion() == True


class TestComportamientoGeneralEnum:
    """Tests de comportamiento general del enum"""
    
    def test_enum_es_hasheable(self):
        """Test que el enum se puede usar como clave de diccionario"""
        dict_test = {
            TipoProcesoAnterior.NINGUNO: "cuenta_nueva",
            TipoProcesoAnterior.TRASLADO_COMPLETADO: "solo_radicacion",
            TipoProcesoAnterior.RADICACION_COMPLETADA: "solo_traslado"
        }
        
        assert dict_test[TipoProcesoAnterior.NINGUNO] == "cuenta_nueva"
        assert dict_test[TipoProcesoAnterior.TRASLADO_COMPLETADO] == "solo_radicacion"
    
    def test_enum_string_representation(self):
        """Test representación string del enum"""
        assert str(TipoProcesoAnterior.NINGUNO) == "TipoProcesoAnterior.NINGUNO"
        assert repr(TipoProcesoAnterior.TRASLADO_COMPLETADO) == "<TipoProcesoAnterior.TRASLADO_COMPLETADO: 'traslado_completado'>"
    
    def test_enum_equality(self):
        """Test igualdad del enum"""
        assert TipoProcesoAnterior.NINGUNO == TipoProcesoAnterior.NINGUNO
        assert TipoProcesoAnterior.NINGUNO != TipoProcesoAnterior.TRASLADO_COMPLETADO
    
    def test_enum_membership(self):
        """Test pertenencia al enum"""
        assert TipoProcesoAnterior.NINGUNO in TipoProcesoAnterior
        
        # Test en listas
        completados = [TipoProcesoAnterior.TRASLADO_COMPLETADO, TipoProcesoAnterior.RADICACION_COMPLETADA]
        assert TipoProcesoAnterior.TRASLADO_COMPLETADO in completados
        assert TipoProcesoAnterior.NINGUNO not in completados
    
    def test_iteracion_sobre_enum(self):
        """Test iteración sobre todos los valores del enum"""
        valores_esperados = [
            "ninguno", "traslado_completado", "traslado_devuelto",
            "radicacion_completada", "radicacion_devuelta"
        ]
        valores_reales = [tipo.value for tipo in TipoProcesoAnterior]
        
        assert len(valores_reales) == 5
        for valor in valores_esperados:
            assert valor in valores_reales
    
    def test_acceso_por_nombre(self):
        """Test acceso al enum por nombre"""
        assert TipoProcesoAnterior["NINGUNO"] == TipoProcesoAnterior.NINGUNO
        assert TipoProcesoAnterior["TRASLADO_COMPLETADO"] == TipoProcesoAnterior.TRASLADO_COMPLETADO
        
        with pytest.raises(KeyError):
            TipoProcesoAnterior["NO_EXISTE"]