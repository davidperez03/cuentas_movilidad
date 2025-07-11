from dataclasses import dataclass
import re
import unicodedata
from typing import Optional


@dataclass(frozen=True)
class DescripcionNovedad:
    """
    Value Object para descripciones de novedades en procesos de traslado/radicación.
    
    - Texto descriptivo ingresado por funcionarios
    - Explica el detalle específico de la novedad encontrada
    - Validación estricta de contenido y longitud
    - Normalización automática de formato
    """
    valor: str

    def __post_init__(self):
        if not self.valor or not str(self.valor).strip():
            raise ValueError("La descripción de la novedad no puede estar vacía")

        normalizada = self._normalizar_texto(str(self.valor))

        if not self._es_longitud_valida(normalizada):
            raise ValueError(f"La descripción debe tener entre 10 y 500 caracteres. Actual: {len(normalizada)}")

        if self._contiene_contenido_sospechoso(normalizada):
            raise ValueError("La descripción contiene contenido no permitido (HTML, scripts, etc.)")
        
        if not self._contiene_solo_caracteres_permitidos(normalizada):
            raise ValueError("La descripción contiene caracteres no permitidos")

        object.__setattr__(self, 'valor', normalizada)

    def _normalizar_texto(self, texto: str) -> str:
        """Normaliza el texto eliminando espacios extra y caracteres de control"""
        texto = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', ' ', texto)
        
        texto = re.sub(r'\s+', ' ', texto)

        texto = texto.strip()
        
        oraciones = texto.split('. ')
        oraciones_capitalizadas = [
            oracion.strip().capitalize() if oracion.strip() else oracion
            for oracion in oraciones
        ]
        return '. '.join(oraciones_capitalizadas)
    
    def _normalizar_para_busqueda(self, texto: str) -> str:
        """
        Convierte texto a minúsculas y sin tildes (para comparación robusta de palabras clave).
        Ej: "vehículo" → "vehiculo"
        """
        texto = texto.lower()
        return ''.join(
            c for c in unicodedata.normalize('NFD', texto)
            if unicodedata.category(c) != 'Mn'
        )


    def _es_longitud_valida(self, texto: str) -> bool:
        """Valida que la longitud esté en el rango permitido"""
        return 10 <= len(texto) <= 500

    def _contiene_solo_caracteres_permitidos(self, texto: str) -> bool:
        """Valida que solo contenga caracteres alfanuméricos, espacios y puntuación básica"""
        patron = r'^[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ0-9\s\.,;:¿?¡!\-_()\[\]"\'°%#\/\+\*\=$]+$'
        return bool(re.match(patron, texto))

    def _contiene_contenido_sospechoso(self, texto: str) -> bool:
        """Detecta contenido potencialmente malicioso"""
        patrones_sospechosos = [
            r'<[^>]*>',           
            r'javascript:',        
            r'on\w+\s*=',       
            r'<script',       
            r'</script>',       
            r'eval\s*\(',      
            r'document\.',    
            r'window\.',        
            r'alert\s*\(', 
            r'prompt\s*\(',    
            r'confirm\s*\(',   
        ]
        
        texto_lower = texto.lower()
        return any(re.search(patron, texto_lower) for patron in patrones_sospechosos)

    def es_corta(self) -> bool:
        """Verifica si la descripción es corta (menos de 50 caracteres)"""
        return len(self.valor) < 50

    def es_detallada(self) -> bool:
        """Verifica si la descripción es detallada (más de 200 caracteres)"""
        return len(self.valor) > 200

    def contiene_palabra_clave(self, palabra: str) -> bool:
        """Verifica si contiene una palabra clave específica (insensible a tildes y mayúsculas)"""
        valor_norm = self._normalizar_para_busqueda(self.valor)
        palabra_norm = self._normalizar_para_busqueda(palabra)
        return palabra_norm in valor_norm


    def get_numero_palabras(self) -> int:
        """Cuenta el número de palabras en la descripción"""
        return len(self.valor.split())

    def get_numero_oraciones(self) -> int:
        """Cuenta el número de oraciones (basado en puntos)"""
        return len([s for s in self.valor.split('.') if s.strip()])

    def get_resumen(self, max_caracteres: int = 100) -> str:
        """Genera un resumen truncado de la descripción"""
        if len(self.valor) <= max_caracteres:
            return self.valor

        resumen = self.valor[:max_caracteres]
        ultimo_espacio = resumen.rfind(' ')
        
        if ultimo_espacio > max_caracteres * 0.8:  
            resumen = resumen[:ultimo_espacio]
        
        return resumen + "..."

    def es_similar_a(self, otra_descripcion: 'DescripcionNovedad', umbral_similitud: float = 0.8) -> bool:
        """
        Verifica si es similar a otra descripción usando similitud básica de palabras
        
        Args:
            otra_descripcion: Otra descripción para comparar
            umbral_similitud: Umbral de similitud (0.0 a 1.0)
        """
        palabras_esta = set(self.valor.lower().split())
        palabras_otra = set(otra_descripcion.valor.lower().split())
        
        if not palabras_esta or not palabras_otra:
            return False
        
        interseccion = palabras_esta.intersection(palabras_otra)
        union = palabras_esta.union(palabras_otra)
        
        similitud = len(interseccion) / len(union)
        return similitud >= umbral_similitud

    def formato_para_reporte(self) -> str:
        """Formatea la descripción para reportes oficiales"""
        return f"DESCRIPCIÓN: {self.valor}"

    def __str__(self) -> str:
        return self.valor

    def __repr__(self) -> str:
        resumen = self.get_resumen(50)
        return f"DescripcionNovedad('{resumen}', palabras={self.get_numero_palabras()})"

    @classmethod
    def crear_desde_texto(cls, texto: str) -> 'DescripcionNovedad':
        """Factory method para crear desde texto"""
        return cls(texto)

    @classmethod
    def crear_si_valida(cls, texto: str) -> Optional['DescripcionNovedad']:
        """Factory method que retorna None si el texto es inválido"""
        try:
            return cls(texto)
        except ValueError:
            return None

    @classmethod
    def crear_con_prefijo_tipo(cls, tipo_novedad: str, descripcion: str) -> 'DescripcionNovedad':
        """
        Factory method para crear con prefijo del tipo de novedad
        
        Args:
            tipo_novedad: Tipo de novedad (ej: "DOCUMENTO_FALTANTE")
            descripcion: Descripción específica
        """
        texto_completo = f"{tipo_novedad.replace('_', ' ').title()}: {descripcion}"
        return cls(texto_completo)

    @classmethod
    def ejemplos_validos(cls) -> list['DescripcionNovedad']:
        """Retorna ejemplos de descripciones válidas para testing/documentación"""
        ejemplos = [
            "El documento de identificación del propietario no se encuentra adjunto al expediente.",
            "La firma en el documento de traspaso no coincide con la registrada en la cédula de ciudadanía.",
            "Falta el certificado de tradición y libertad con vigencia no mayor a 30 días.",
            "Los datos del vehículo en el RUNT no coinciden con los datos físicos verificados.",
            "La póliza SOAT se encuentra vencida desde hace 45 días según verificación en FASECOLDA.",
        ]
        
        return [cls(ejemplo) for ejemplo in ejemplos]

    @classmethod
    def validar_grupo_descripciones(cls, descripciones: list[str]) -> dict[str, list[str]]:
        """
        Valida un grupo de descripciones y las clasifica en válidas e inválidas
        
        Returns:
            dict con 'validas' e 'invalidas', cada una con lista de descripciones
        """
        resultado = {"validas": [], "invalidas": []}
        
        for desc in descripciones:
            try:
                cls(desc)
                resultado["validas"].append(desc)
            except ValueError:
                resultado["invalidas"].append(desc)
        
        return resultado