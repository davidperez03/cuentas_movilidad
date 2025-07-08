from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Optional


@dataclass(frozen=True)
class FechaTramite:
    """
    Value Object para fechas de trámite ingresadas por el usuario.
    
    - Fecha manual ingresada en formularios de Trasladar/Radicar
    - Base para calcular fecha de vencimiento (+60 días)
    - Puede ser presente, pasada o ligeramente futura (validación flexible)
    - Propósito: Control de fechas de inicio de procesos
    """
    fecha: date

    def __post_init__(self):
        if not isinstance(self.fecha, date):
            raise ValueError("La fecha de trámite debe ser un objeto date válido")
        
        if self.fecha > date.today() + timedelta(days=30):
            raise ValueError(f"La fecha de trámite no puede ser más de 30 días en el futuro: {self.fecha}")
        
        if self.fecha < date.today() - timedelta(days=365):
            raise ValueError(f"La fecha de trámite no puede ser más de 1 año en el pasado: {self.fecha}")

    def es_de_hoy(self) -> bool:
        """Verifica si el trámite es para hoy"""
        return self.fecha == date.today()

    def es_futuro(self) -> bool:
        """Verifica si el trámite es para una fecha futura"""
        return self.fecha > date.today()

    def es_pasado(self) -> bool:
        """Verifica si el trámite es para una fecha pasada"""
        return self.fecha < date.today()

    def dias_desde_hoy(self) -> int:
        """
        Calcula días desde hoy (positivo = pasado, negativo = futuro)
        
        Returns:
            int: Días transcurridos desde hoy
                 > 0: fecha en el pasado
                 = 0: fecha de hoy  
                 < 0: fecha en el futuro
        """
        return (date.today() - self.fecha).days

    def dias_hasta_tramite(self) -> int:
        """
        Calcula días hasta el trámite (solo para fechas futuras)
        
        Returns:
            int: Días hasta el trámite (0 si es hoy o pasado)
        """
        if self.es_futuro():
            return (self.fecha - date.today()).days
        return 0

    def esta_en_rango_permitido(self) -> bool:
        """Verifica si la fecha está en el rango permitido del sistema"""
        hoy = date.today()
        limite_futuro = hoy + timedelta(days=30)
        limite_pasado = hoy - timedelta(days=365)
        
        return limite_pasado <= self.fecha <= limite_futuro

    def es_fin_de_semana(self) -> bool:
        """Verifica si la fecha de trámite cae en fin de semana"""
        return self.fecha.weekday() >= 5  

    def es_dia_laboral(self) -> bool:
        """Verifica si la fecha de trámite es día laboral (lunes a viernes)"""
        return not self.es_fin_de_semana()

    def siguiente_dia_laboral(self) -> date:
        """Obtiene el siguiente día laboral desde la fecha de trámite"""
        fecha_temp = self.fecha
        while fecha_temp.weekday() >= 5:  
            fecha_temp += timedelta(days=1)
        return fecha_temp

    def get_year(self) -> int:
        """Obtiene el año del trámite"""
        return self.fecha.year

    def get_month(self) -> int:
        """Obtiene el mes del trámite"""
        return self.fecha.month

    def get_day(self) -> int:
        """Obtiene el día del trámite"""
        return self.fecha.day

    def get_weekday(self) -> int:
        """Obtiene el día de la semana (0=Lunes, 6=Domingo)"""
        return self.fecha.weekday()

    def get_weekday_name(self) -> str:
        """Obtiene el nombre del día de la semana en español"""
        nombres = [
            "Lunes", "Martes", "Miércoles", "Jueves", 
            "Viernes", "Sábado", "Domingo"
        ]
        return nombres[self.fecha.weekday()]

    def formato_legible(self) -> str:
        """Retorna formato legible: YYYY-MM-DD"""
        return self.fecha.strftime("%Y-%m-%d")

    def formato_español(self) -> str:
        """Retorna formato en español: DD/MM/YYYY"""
        return self.fecha.strftime("%d/%m/%Y")

    def formato_completo(self) -> str:
        """Retorna formato completo con día de la semana"""
        return f"{self.get_weekday_name()}, {self.formato_español()}"

    def __str__(self) -> str:
        return str(self.fecha)

    def __repr__(self) -> str:
        estado = "hoy" if self.es_de_hoy() else ("futuro" if self.es_futuro() else "pasado")
        return f"FechaTramite(fecha={self.fecha}, estado={estado}, dias_desde_hoy={self.dias_desde_hoy()})"

    @classmethod
    def crear_hoy(cls) -> 'FechaTramite':
        """Factory method: crea fecha de trámite para hoy"""
        return cls(date.today())

    @classmethod
    def crear_para_fecha(cls, fecha: date) -> 'FechaTramite':
        """Factory method: crea fecha de trámite para fecha específica"""
        return cls(fecha)

    @classmethod
    def crear_desde_string(cls, fecha_str: str) -> 'FechaTramite':
        """
        Factory method: crea desde string en formato YYYY-MM-DD o DD/MM/YYYY
        
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
    def crear_si_valida(cls, fecha: date) -> Optional['FechaTramite']:
        """Factory method que retorna None si la fecha es inválida"""
        try:
            return cls(fecha)
        except ValueError:
            return None

    @classmethod
    def crear_siguiente_dia_laboral(cls) -> 'FechaTramite':
        """Factory method: crea fecha de trámite para el siguiente día laboral"""
        fecha_actual = date.today()
        
        if fecha_actual.weekday() < 5:
            return cls(fecha_actual)
        
        dias_hasta_lunes = 7 - fecha_actual.weekday()
        siguiente_lunes = fecha_actual + timedelta(days=dias_hasta_lunes)
        return cls(siguiente_lunes)

    @classmethod
    def crear_con_validacion_laboral(cls, fecha: date, solo_dias_laborales: bool = False) -> 'FechaTramite':
        """
        Factory method: crea fecha con opción de validar días laborales
        
        Args:
            fecha: Fecha deseada
            solo_dias_laborales: Si True, ajusta automáticamente a día laboral
        """
        if not solo_dias_laborales:
            return cls(fecha)
        
        while fecha.weekday() >= 5:  # Mientras sea fin de semana
            fecha += timedelta(days=1)
        
        return cls(fecha)