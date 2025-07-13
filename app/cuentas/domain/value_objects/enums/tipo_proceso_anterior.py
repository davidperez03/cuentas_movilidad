from enum import Enum


class TipoProcesoAnterior(Enum):
    """
    Enum para tipos de procesos anteriores completados en una cuenta.
    
    Controla la lógica origen/destino:
    - Si fue TRASLADO_COMPLETADO: solo puede hacer radicación
    - Si fue RADICACION_COMPLETADA: solo puede hacer traslado  
    - Si fue DEVUELTO: puede hacer cualquiera (rompe restricción)
    - NINGUNO: cuenta nueva, puede hacer cualquiera
    """
    NINGUNO = "ninguno"
    TRASLADO_COMPLETADO = "traslado_completado"
    TRASLADO_DEVUELTO = "traslado_devuelto"
    RADICACION_COMPLETADA = "radicacion_completada"
    RADICACION_DEVUELTA = "radicacion_devuelta"
    
    def permite_traslado(self) -> bool:
        """Verifica si este proceso anterior permite iniciar traslado"""
        return self in [
            TipoProcesoAnterior.NINGUNO,
            TipoProcesoAnterior.RADICACION_COMPLETADA, 
            TipoProcesoAnterior.TRASLADO_DEVUELTO,     
            TipoProcesoAnterior.RADICACION_DEVUELTA    
        ]
    
    def permite_radicacion(self) -> bool:
        """Verifica si este proceso anterior permite iniciar radicación"""
        return self in [
            TipoProcesoAnterior.NINGUNO,
            TipoProcesoAnterior.TRASLADO_COMPLETADO,  
            TipoProcesoAnterior.TRASLADO_DEVUELTO,      
            TipoProcesoAnterior.RADICACION_DEVUELTA    
        ]
    
    def get_descripcion(self) -> str:
        """Retorna descripción legible del proceso anterior"""
        descripciones = {
            TipoProcesoAnterior.NINGUNO: "Sin procesos anteriores",
            TipoProcesoAnterior.TRASLADO_COMPLETADO: "Traslado completado exitosamente",
            TipoProcesoAnterior.TRASLADO_DEVUELTO: "Traslado devuelto por administración",
            TipoProcesoAnterior.RADICACION_COMPLETADA: "Radicación completada exitosamente", 
            TipoProcesoAnterior.RADICACION_DEVUELTA: "Radicación devuelta por administración"
        }
        return descripciones[self]
    
    def es_completado_exitosamente(self) -> bool:
        """Verifica si el proceso anterior fue completado exitosamente"""
        return self in [
            TipoProcesoAnterior.TRASLADO_COMPLETADO,
            TipoProcesoAnterior.RADICACION_COMPLETADA
        ]
    
    def es_devuelto(self) -> bool:
        """Verifica si el proceso anterior fue devuelto"""
        return self in [
            TipoProcesoAnterior.TRASLADO_DEVUELTO,
            TipoProcesoAnterior.RADICACION_DEVUELTA
        ]
    
    def get_proceso_contrario_permitido(self) -> str:
        """Retorna el tipo de proceso que está permitido después de este"""
        if self == TipoProcesoAnterior.TRASLADO_COMPLETADO:
            return "radicacion"
        elif self == TipoProcesoAnterior.RADICACION_COMPLETADA:
            return "traslado"
        elif self.es_devuelto() or self == TipoProcesoAnterior.NINGUNO:
            return "ambos"
        else:
            return "ninguno"