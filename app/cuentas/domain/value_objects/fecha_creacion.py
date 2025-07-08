from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Optional


@dataclass(frozen=True)
class FechaCreacion:
    """
    Value Object para fechas de creación de cuentas.
    
    - Fecha automática cuando se crea una cuenta
    - Siempre es la fecha actual del sistema
    - Solo puede ser presente o pasada, nunca futura
    - Propósito: Auditoría y trazabilidad
    """
    fecha: date

    def __post_init__(self):
        if not isinstance(self.fecha, date):
            raise ValueError("La fecha de creación debe ser un objeto date válido")
        
        if self.fecha > date.today():
            raise ValueError(f"La fecha de creación no puede ser futura: {self.fecha}")

    def es_de_hoy(self) -> bool:
        """Verifica si la cuenta fue creada hoy"""
        return self.fecha == date.today()

    def es_de_ayer(self) -> bool:
        """Verifica si la cuenta fue creada ayer"""
        return self.fecha == date.today() - timedelta(days=1)

    def dias_desde_creacion(self) -> int:
        """Calcula días transcurridos desde la creación"""
        return (date.today() - self.fecha).days

    def semanas_desde_creacion(self) -> int:
        """Calcula semanas transcurridas desde la creación"""
        return self.dias_desde_creacion() // 7

    def meses_desde_creacion(self) -> int:
        """Calcula meses aproximados desde la creación"""
        return self.dias_desde_creacion() // 30

    def es_antigua(self, dias_limite: int = 365) -> bool:
        """Verifica si la cuenta es antigua (por defecto más de 1 año)"""
        return self.dias_desde_creacion() >= dias_limite

    def es_reciente(self, dias_limite: int = 7) -> bool:
        """Verifica si la cuenta es reciente (por defecto menos de 1 semana)"""
        return self.dias_desde_creacion() <= dias_limite

    def get_year(self) -> int:
        """Obtiene el año de creación"""
        return self.fecha.year

    def get_month(self) -> int:
        """Obtiene el mes de creación"""
        return self.fecha.month

    def get_day(self) -> int:
        """Obtiene el día de creación"""
        return self.fecha.day

    def formato_legible(self) -> str:
        """Retorna formato legible: YYYY-MM-DD"""
        return self.fecha.strftime("%Y-%m-%d")

    def formato_español(self) -> str:
        """Retorna formato en español: DD/MM/YYYY"""
        return self.fecha.strftime("%d/%m/%Y")

    def __str__(self) -> str:
        return str(self.fecha)

    def __repr__(self) -> str:
        return f"FechaCreacion(fecha={self.fecha}, dias_transcurridos={self.dias_desde_creacion()})"

    @classmethod
    def crear_hoy(cls) -> 'FechaCreacion':
        """Factory method: crea fecha de creación para hoy (uso típico)"""
        return cls(date.today())

    @classmethod
    def crear_para_fecha(cls, fecha: date) -> 'FechaCreacion':
        """Factory method: crea fecha de creación para fecha específica"""
        return cls(fecha)

    @classmethod
    def crear_desde_string(cls, fecha_str: str) -> 'FechaCreacion':
        """
        Factory method: crea desde string en formato YYYY-MM-DD
        
        Args:
            fecha_str: Fecha en formato "YYYY-MM-DD" o "DD/MM/YYYY"
        """
        try:
            if '-' in fecha_str:
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            elif '/' in fecha_str:
                fecha = datetime.strptime(fecha_str, "%d/%m/%Y").date()
            else:
                raise ValueError(f"Formato de fecha no válido: {fecha_str}")
            
            return cls(fecha)
        except ValueError as e:
            raise ValueError(f"No se pudo parsear la fecha '{fecha_str}': {e}")

    @classmethod
    def crear_si_valida(cls, fecha: date) -> Optional['FechaCreacion']:
        """Factory method que retorna None si la fecha es inválida"""
        try:
            return cls(fecha)
        except ValueError:
            return None