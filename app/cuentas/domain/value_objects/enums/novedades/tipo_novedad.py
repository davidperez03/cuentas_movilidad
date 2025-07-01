from enum import Enum


class TipoNovedad(Enum):
    DOCUMENTO_FALTANTE = "documento_faltante"
    DOCUMENTO_INCORRECTO = "documento_incorrecto"
    INFORMACION_INCONSISTENTE = "informacion_inconsistente"
    FIRMA_FALTANTE = "firma_faltante"
    FECHA_INCORRECTA = "fecha_incorrecta"
    DATOS_PROPIETARIO_INCOMPLETOS = "datos_propietario_incompletos"
    SOAT_VENCIDO = "soat_vencido"
    TECNICOMECANICA_VENCIDA = "tecnicomecanica_vencida"
    OTRO = "otro"