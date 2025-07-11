from dataclasses import dataclass
import re
from typing import Optional
from datetime import datetime


@dataclass(frozen=True)
class Observacion:
    """
    Value Object para observaciones generales en procesos de traslado/radicación.
    
    - Comentarios opcionales ingresados por funcionarios
    - Notas adicionales, aclaraciones o contexto general
    - Más flexible que DescripcionNovedad (puede ser vacía)
    - Normalización automática pero menos restrictiva
    """
    valor: str

    def __post_init__(self):
        if self.valor is None:
            valor_normalizado = ""
        else:
            valor_normalizado = self._normalizar_texto(str(self.valor))

        if not self._es_longitud_valida(valor_normalizado):
            raise ValueError(f"La observación no puede exceder 1000 caracteres. Actual: {len(valor_normalizado)}")

        if valor_normalizado and not self._contiene_solo_caracteres_permitidos(valor_normalizado):
            raise ValueError("La observación contiene caracteres no permitidos")

        if self._contiene_contenido_sospechoso(valor_normalizado):
            raise ValueError("La observación contiene contenido no permitido (HTML, scripts, etc.)")

        object.__setattr__(self, 'valor', valor_normalizado)

    def _normalizar_texto(self, texto: str) -> str:
        """Normaliza el texto de forma más flexible que DescripcionNovedad"""
        if not texto or not texto.strip():
            return ""
        
        texto = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', ' ', texto)

        lineas = texto.split('\n')
        lineas_normalizadas = []
        
        for linea in lineas:
            linea_normalizada = re.sub(r' {2,}', ' ', linea).strip()
            lineas_normalizadas.append(linea_normalizada)

        texto_normalizado = '\n'.join(lineas_normalizadas)
        texto_normalizado = re.sub(r'\n\s*\n', '\n\n', texto_normalizado)
        
        return texto_normalizado.strip()

    def _es_longitud_valida(self, texto: str) -> bool:
        """Valida que no exceda el máximo permitido (sin mínimo obligatorio)"""
        return len(texto) <= 1000

    def _contiene_solo_caracteres_permitidos(self, texto: str) -> bool:
        """Valida que el texto contenga solo caracteres aceptables para observaciones"""
        if not texto:
            return True

        patron = r"""^[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ0-9\s
        \.,;:¿?¡!\-_()\[\]"'°%#@<>\|\/\+\*=\n\r\t&—«»·€$@·´`~^°✓✔️✖️✅⚠️🚫📌📎📍🙂…]*$"""

        return bool(re.match(patron, texto, re.UNICODE | re.VERBOSE))


    def _contiene_contenido_sospechoso(self, texto: str) -> bool:
        """Detecta contenido potencialmente malicioso (similar pero menos estricto)"""
        if not texto:
            return False
            
        patrones_sospechosos = [
            r'<script[^>]*>',   
            r'</script>',   
            r'javascript:', 
            r'on\w+\s*=\s*["\']', 
            r'eval\s*\(',        
            r'document\.write', 
            r'window\.location\s*=', 
        ]
        
        texto_lower = texto.lower()
        return any(re.search(patron, texto_lower) for patron in patrones_sospechosos)

    def esta_vacia(self) -> bool:
        """Verifica si la observación está vacía"""
        return not self.valor or not self.valor.strip()

    def es_multilinea(self) -> bool:
        """Verifica si la observación tiene múltiples líneas"""
        return '\n' in self.valor

    def tiene_longitud_significativa(self) -> bool:
        """Verifica si tiene longitud significativa (más de 20 caracteres)"""
        return len(self.valor.strip()) > 20

    def contiene_palabra_clave(self, palabra: str) -> bool:
        """Verifica si contiene una palabra clave específica (case-insensitive)"""
        if not self.valor:
            return False
        return palabra.lower() in self.valor.lower()

    def get_numero_caracteres(self) -> int:
        """Obtiene el número de caracteres (incluyendo espacios)"""
        return len(self.valor)

    def get_numero_caracteres_sin_espacios(self) -> int:
        """Obtiene el número de caracteres sin contar espacios"""
        return len(re.sub(r'\s', '', self.valor))

    def get_numero_palabras(self) -> int:
        """Cuenta el número de palabras en la observación"""
        if not self.valor.strip():
            return 0
        return len(self.valor.split())

    def get_numero_lineas(self) -> int:
        """Cuenta el número de líneas en la observación"""
        if not self.valor:
            return 0
        return len([linea for linea in self.valor.split('\n') if linea.strip()])

    def get_resumen(self, max_caracteres: int = 150) -> str:
        """Genera un resumen truncado de la observación"""
        if not self.valor:
            return "[Sin observaciones]"

        if self.es_multilinea():
            primera_linea = self.valor.split('\n')[0].strip()
            if len(primera_linea) <= max_caracteres:
                return primera_linea + "..."
            else:
                return primera_linea[:max_caracteres - 3].rstrip() + "..."

        if len(self.valor) <= max_caracteres:
            return self.valor

        resumen = self.valor[:max_caracteres]
        ultimo_espacio = resumen.rfind(' ')
        if ultimo_espacio > max_caracteres * 0.6:
            resumen = resumen[:ultimo_espacio]

        return resumen.rstrip() + "..."

    def get_vista_previa_una_linea(self) -> str:
        """Genera una vista previa en una sola línea para tablas/listas"""
        if not self.valor:
            return ""
        
        una_linea = re.sub(r'\s+', ' ', self.valor.strip())
        
        if len(una_linea) > 100:
            una_linea = una_linea[:97] + "..."
        
        return una_linea

    def agregar_timestamp_automatico(self, funcionario: str) -> 'Observacion':
        """Crea nueva observación agregando timestamp automático"""
        if not funcionario.strip():
            raise ValueError("El funcionario no puede estar vacío")
        
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        if self.esta_vacia():
            nuevo_contenido = f"[{timestamp} - {funcionario}] Sin observaciones adicionales."
        else:
            nuevo_contenido = f"[{timestamp} - {funcionario}] {self.valor}"
        
        return Observacion(nuevo_contenido)

    def es_observacion_sistema(self) -> bool:
        """Detecta si es una observación generada automáticamente por el sistema"""
        patrones_sistema = [
            r'\[\d{2}/\d{2}/\d{4} \d{2}:\d{2} - .+\]', 
            r'Sistema automatico',
            r'Generado automaticamente',
            r'Auto-asignado',
        ]
        
        return any(re.search(patron, self.valor, re.IGNORECASE) for patron in patrones_sistema)

    def extraer_menciones_funcionarios(self) -> list[str]:
        """Extrae menciones a funcionarios (formato @nombre o @nombre.apellido)"""
        if not self.valor:
            return []
        
        patron = r'@([a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]+(?:\.[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]+)?)'
        menciones = re.findall(patron, self.valor)
        return list(set(menciones))  

    def formato_para_reporte(self) -> str:
        """Formatea la observación para reportes oficiales"""
        if self.esta_vacia():
            return "OBSERVACIONES: Sin observaciones registradas."
        
        return f"OBSERVACIONES:\n{self.valor}"

    def formato_para_auditoria(self) -> str:
        """Formatea la observación para auditoría con metadatos"""
        metadata = {
            "caracteres": self.get_numero_caracteres(),
            "palabras": self.get_numero_palabras(),
            "lineas": self.get_numero_lineas(),
            "multilinea": self.es_multilinea(),
            "sistema": self.es_observacion_sistema()
        }
        
        return f"OBSERVACION: {self.valor}\nMETADATA: {metadata}"

    def __str__(self) -> str:
        return self.valor if self.valor else ""

    def __repr__(self) -> str:
        if self.esta_vacia():
            return "Observacion(vacía)"
        
        resumen = self.get_resumen(30)
        stats = f"chars={self.get_numero_caracteres()}, words={self.get_numero_palabras()}"
        return f"Observacion('{resumen}', {stats})"

    @classmethod
    def vacia(cls) -> 'Observacion':
        """Factory method: crea observación vacía"""
        return cls("")

    @classmethod
    def crear_desde_texto(cls, texto: str) -> 'Observacion':
        """Factory method para crear desde texto"""
        return cls(texto)

    @classmethod
    def crear_si_valida(cls, texto: str) -> Optional['Observacion']:
        """Factory method que retorna None si el texto es inválido"""
        try:
            return cls(texto)
        except ValueError:
            return None

    @classmethod
    def crear_con_timestamp(cls, texto: str, funcionario: str) -> 'Observacion':
        """Factory method para crear con timestamp automático"""
        observacion_base = cls(texto) if texto else cls.vacia()
        return observacion_base.agregar_timestamp_automatico(funcionario)

    @classmethod
    def crear_observacion_sistema(cls, mensaje: str, accion: str = "SISTEMA") -> 'Observacion':
        """Factory method para crear observaciones automáticas del sistema"""
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
        contenido = f"[{timestamp} - {accion}] {mensaje}"
        return cls(contenido)

    @classmethod
    def combinar_observaciones(cls, observaciones: list['Observacion'], 
                              separador: str = "\n---\n") -> 'Observacion':
        """Combina múltiples observaciones en una sola"""
        observaciones_validas = [obs for obs in observaciones if not obs.esta_vacia()]
        
        if not observaciones_validas:
            return cls.vacia()
        
        contenido_combinado = separador.join(obs.valor for obs in observaciones_validas)
        return cls(contenido_combinado)

    @classmethod
    def ejemplos_tipicos(cls) -> list['Observacion']:
        """Retorna ejemplos típicos de observaciones para testing/documentación"""
        ejemplos = [
            cls.vacia(),
            cls("Proceso completado sin inconvenientes."),
            cls("Requiere seguimiento especial por parte de supervisión.\nCoordinar con oficina de destino."),
            cls("@juan.perez Por favor revisar documentación antes del envío."),
            cls.crear_observacion_sistema("Expediente asignado automáticamente", "AUTO-ASIGN"),
        ]
        
        return ejemplos

    @classmethod
    def validar_lote_observaciones(cls, observaciones_texto: list[str]) -> dict[str, list[str]]:
        """
        Valida un lote de observaciones y las clasifica
        
        Returns:
            dict con 'validas', 'invalidas' y 'vacias'
        """
        resultado = {"validas": [], "invalidas": [], "vacias": []}
        
        for texto in observaciones_texto:
            try:
                obs = cls(texto)
                if obs.esta_vacia():
                    resultado["vacias"].append(texto)
                else:
                    resultado["validas"].append(texto)
            except ValueError:
                resultado["invalidas"].append(texto)
        
        return resultado