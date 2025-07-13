from dataclasses import dataclass
from typing import Optional, Dict, Any
import re


@dataclass(frozen=True)
class Ubicacion:
    """
    Value Object para ubicaciones/organismos de tránsito.
    
    Compatible con estructura de web scraping futuro y datos actuales.
    Maneja organismos destino para traslados y origen para radicaciones.
    """
    codigo: str 
    nombre_completo: str  
    municipio: str
    departamento: str  
    direccion: Optional[str] = None 
    telefono: Optional[str] = None 

    def __post_init__(self):
        if not self.codigo or not self.codigo.strip():
            raise ValueError("El código de ubicación no puede estar vacío")
        
        if not self.nombre_completo or not self.nombre_completo.strip():
            raise ValueError("El nombre completo no puede estar vacío")
        
        if not self.municipio or not self.municipio.strip():
            raise ValueError("El municipio no puede estar vacío")
        
        if not self.departamento or not self.departamento.strip():
            raise ValueError("El departamento no puede estar vacío")
      
        codigo_normalizado = re.sub(r'\s+', '_', self.codigo.strip().upper())
        object.__setattr__(self, 'codigo', codigo_normalizado)
        
        object.__setattr__(self, 'nombre_completo', self.nombre_completo.strip())
        object.__setattr__(self, 'municipio', self.municipio.strip())
        object.__setattr__(self, 'departamento', self.departamento.strip())

    def get_nombre_corto(self) -> str:
        """Retorna nombre corto para mostrar en interfaces"""
        return self.codigo.replace('_', ' ').title()

    def get_descripcion_completa(self) -> str:
        """Retorna descripción completa: Municipio - Departamento"""
        return f"{self.municipio} - {self.departamento}"

    def get_ubicacion_display(self) -> str:
        """Formato para mostrar en UI: Nombre Corto (Municipio - Depto)"""
        return f"{self.get_nombre_corto()} ({self.get_descripcion_completa()})"

    def es_mismo_departamento(self, otra_ubicacion: 'Ubicacion') -> bool:
        """Verifica si está en el mismo departamento"""
        return self.departamento.upper() == otra_ubicacion.departamento.upper()

    def es_mismo_municipio(self, otra_ubicacion: 'Ubicacion') -> bool:
        """Verifica si está en el mismo municipio"""
        return (self.municipio.upper() == otra_ubicacion.municipio.upper() and 
                self.es_mismo_departamento(otra_ubicacion))

    def tiene_contacto_completo(self) -> bool:
        """Verifica si tiene información de contacto completa"""
        return bool(self.direccion and self.telefono)

    def __str__(self) -> str:
        return self.get_nombre_corto()

    def __repr__(self) -> str:
        return f"Ubicacion(codigo='{self.codigo}', municipio='{self.municipio}', departamento='{self.departamento}')"

    @classmethod
    def crear_desde_web_scraping(cls, datos_scraping: Dict[str, Any]) -> 'Ubicacion':
        """Factory method para crear desde datos de web scraping futuro"""
        try:
            municipio_completo = datos_scraping['municipio']
            if ' - ' in municipio_completo:
                municipio, _ = municipio_completo.split(' - ', 1)
            else:
                municipio = municipio_completo
            
            nombre = datos_scraping['nombre']
            codigo = cls._generar_codigo_desde_nombre(nombre)
            
            direccion = cls._limpiar_direccion(datos_scraping.get('direccion', ''))
            telefono = cls._limpiar_telefono(datos_scraping.get('telefono', ''))
            
            return cls(
                codigo=codigo,
                nombre_completo=nombre,
                municipio=municipio,
                departamento=datos_scraping['departamento'],
                direccion=direccion if direccion else None,
                telefono=telefono if telefono else None
            )
        except (KeyError, ValueError) as e:
            raise ValueError(f"Error procesando datos de web scraping: {e}")

    @classmethod
    def _generar_codigo_desde_nombre(cls, nombre: str) -> str:
        """Genera código interno desde nombre del organismo"""
        nombre_upper = nombre.upper()

        mapeos = {
            'AGUAZUL': 'AGUAZUL',
            'SAN ANDRES': 'SAN_ANDRES', 
            'MANZANARES': 'MANZANARES',
            'BARBOSA': 'BARBOSA',
            'CASANARE': 'CASANARE',
            'PUTUMAYO': 'PUTUMAYO'
        }
        
        for palabra, codigo in mapeos.items():
            if palabra in nombre_upper:
                return codigo
        
        palabras = [p for p in nombre.split() if len(p) > 2]
        if palabras:
            return '_'.join(p[:4].upper() for p in palabras[:2])
        
        return 'ORGANISMO'

    @classmethod
    def _limpiar_direccion(cls, direccion: str) -> str:
        """Limpia dirección removiendo prefijos como 'Dirección'"""
        if not direccion:
            return ""
        return re.sub(r'^Dirección\s*', '', direccion).strip()

    @classmethod
    def _limpiar_telefono(cls, telefono: str) -> str:
        """Limpia teléfono removiendo prefijos como 'Teléfono'"""
        if not telefono:
            return ""
        return re.sub(r'^Teléfono\s*', '', telefono).strip()

    @classmethod
    def crear_basica(cls, codigo: str, municipio: str, departamento: str) -> 'Ubicacion':
        """Factory method para crear ubicación básica sin datos de contacto"""
        nombre_completo = f"Organismo de Tránsito de {municipio}"
        return cls(
            codigo=codigo,
            nombre_completo=nombre_completo,
            municipio=municipio,
            departamento=departamento
        )
    
class UbicacionesPredefinidas:
    """Ubicaciones conocidas del sistema"""
    
    SOGAMOSO = Ubicacion(
        codigo="SOGAMOSO",
        nombre_completo="Organismo de Tránsito de Sogamoso",
        municipio="Sogamoso",
        departamento="Boyacá"
    )
    
    MEDELLIN = Ubicacion(
        codigo="MEDELLIN", 
        nombre_completo="Secretaría de Movilidad de Medellín",
        municipio="Medellín",
        departamento="Antioquia"
    )
    
    BOGOTA_DC = Ubicacion(
        codigo="BOGOTA_DC",
        nombre_completo="Secretaría Distrital de Movilidad de Bogotá",
        municipio="Bogotá D.C.",
        departamento="Cundinamarca"
    )
    
    FUNZA = Ubicacion(
        codigo="FUNZA",
        nombre_completo="Organismo de Tránsito de Funza", 
        municipio="Funza",
        departamento="Cundinamarca"
    )
    
    MARIQUITA = Ubicacion(
        codigo="MARIQUITA",
        nombre_completo="Organismo de Tránsito de Mariquita",
        municipio="Mariquita", 
        departamento="Tolima"
    )
    
    CALI = Ubicacion(
        codigo="CALI",
        nombre_completo="Secretaría de Movilidad de Cali",
        municipio="Cali",
        departamento="Valle del Cauca"
    )
    
    MANIZALES = Ubicacion(
        codigo="MANIZALES",
        nombre_completo="Organismo de Tránsito de Manizales",
        municipio="Manizales",
        departamento="Caldas"
    )
    
    @classmethod
    def obtener_todas(cls) -> list[Ubicacion]:
        """Retorna todas las ubicaciones predefinidas"""
        return [
            cls.SOGAMOSO, cls.MEDELLIN, cls.BOGOTA_DC, 
            cls.FUNZA, cls.MARIQUITA, cls.CALI, cls.MANIZALES
        ]
    
    @classmethod
    def obtener_por_codigo(cls, codigo: str) -> Optional[Ubicacion]:
        """Busca ubicación por código"""
        codigo_normalizado = codigo.upper().replace(' ', '_')
        for ubicacion in cls.obtener_todas():
            if ubicacion.codigo == codigo_normalizado:
                return ubicacion
        return None
    
    @classmethod
    def obtener_por_municipio(cls, municipio: str) -> list[Ubicacion]:
        """Busca ubicaciones por municipio"""
        municipio_normalizado = municipio.upper()
        return [
            ub for ub in cls.obtener_todas() 
            if municipio_normalizado in ub.municipio.upper()
        ]