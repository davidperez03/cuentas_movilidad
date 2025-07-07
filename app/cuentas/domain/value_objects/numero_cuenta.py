from dataclasses import dataclass
from datetime import date
import re
from typing import Optional


@dataclass(frozen=True)
class NumeroCuenta:
    """
    Value Object para números de cuenta con formato YYYYMMDDNNNNN.
    
    Formato: YYYYMMDDNNNNN (13 dígitos)
    - YYYY: Año (4 dígitos)
    - MM: Mes (2 dígitos, 01-12)
    - DD: Día (2 dígitos, 01-31)
    - NNNNN: Consecutivo diario (5 dígitos, 00001-99999)
    
    """
    valor: str

    def __post_init__(self):
        if not self.valor:
            raise ValueError("El número de cuenta no puede estar vacío")

        normalizado = re.sub(r'[^0-9]', '', str(self.valor))

        if not self._es_formato_valido(normalizado):
            raise ValueError(f"Formato de número de cuenta inválido: {self.valor}")

        if not self._es_fecha_valida(normalizado):
            raise ValueError(f"La fecha en el número de cuenta es inválida: {self.valor}")

        if not self._es_consecutivo_valido(normalizado):
            raise ValueError(f"El consecutivo en el número de cuenta es inválido: {self.valor}")

        object.__setattr__(self, 'valor', normalizado)

        if self.get_fecha() > date.today():
            raise ValueError(f"La fecha del número de cuenta no puede ser futura: {self.get_fecha()}")


    def _es_formato_valido(self, numero: str) -> bool:
        """Verifica que tenga exactamente 13 dígitos"""
        return bool(re.match(r'^[0-9]{13}$', numero))

    def _es_fecha_valida(self, numero: str) -> bool:
        """Verifica que la parte de fecha sea válida"""
        try:
            year = int(numero[0:4])
            month = int(numero[4:6])
            day = int(numero[6:8])
            
            if year < 1900 or year > 2100:
                return False

            date(year, month, day)  
            return True
        except (ValueError, IndexError):
            return False

    def _es_consecutivo_valido(self, numero: str) -> bool:
        """Verifica que el consecutivo esté en rango válido"""
        try:
            consecutivo = int(numero[8:13])
            return 1 <= consecutivo <= 99999
        except (ValueError, IndexError):
            return False

    def get_fecha(self) -> date:
        """Extrae la fecha del número de cuenta"""
        year = int(self.valor[0:4])
        month = int(self.valor[4:6])
        day = int(self.valor[6:8])
        return date(year, month, day)

    def get_consecutivo(self) -> int:
        """Extrae el consecutivo del número de cuenta"""
        return int(self.valor[8:13])

    def get_year(self) -> int:
        """Extrae el año del número de cuenta"""
        return int(self.valor[0:4])

    def get_month(self) -> int:
        """Extrae el mes del número de cuenta"""
        return int(self.valor[4:6])

    def get_day(self) -> int:
        """Extrae el día del número de cuenta"""
        return int(self.valor[6:8])

    def es_de_hoy(self) -> bool:
        """Verifica si el número de cuenta es de la fecha actual"""
        return self.get_fecha() == date.today()

    def es_de_fecha(self, fecha: date) -> bool:
        """Verifica si el número de cuenta es de una fecha específica"""
        return self.get_fecha() == fecha

    def es_anterior_a(self, fecha: date) -> bool:
        """Verifica si el número de cuenta es anterior a una fecha"""
        return self.get_fecha() < fecha

    def es_posterior_a(self, fecha: date) -> bool:
        """Verifica si el número de cuenta es posterior a una fecha"""
        return self.get_fecha() > fecha

    def formato_legible(self) -> str:
        """Retorna formato legible: YYYY-MM-DD-NNNNN"""
        return f"{self.valor[0:4]}-{self.valor[4:6]}-{self.valor[6:8]}-{self.valor[8:13]}"

    def __str__(self) -> str:
        return self.valor

    def __repr__(self) -> str:
        return f"NumeroCuenta('{self.valor}', fecha={self.get_fecha()}, consecutivo={self.get_consecutivo()})"

    @classmethod
    def generar_para_hoy(cls, consecutivo: int) -> 'NumeroCuenta':
        """Genera un número de cuenta para la fecha actual"""
        if not isinstance(consecutivo, int) or consecutivo < 1 or consecutivo > 99999:
            raise ValueError("El consecutivo debe ser un entero entre 1 y 99999")
            
        hoy = date.today()
        fecha_str = hoy.strftime("%Y%m%d")
        consecutivo_str = f"{consecutivo:05d}"
        numero = fecha_str + consecutivo_str
        
        return cls(numero)

    @classmethod
    def generar_para_fecha(cls, fecha: date, consecutivo: int) -> 'NumeroCuenta':
        """Genera un número de cuenta para una fecha específica"""
        if not isinstance(fecha, date):
            raise ValueError("La fecha debe ser un objeto date")
        if not isinstance(consecutivo, int) or consecutivo < 1 or consecutivo > 99999:
            raise ValueError("El consecutivo debe ser un entero entre 1 y 99999")
            
        fecha_str = fecha.strftime("%Y%m%d")
        consecutivo_str = f"{consecutivo:05d}"
        numero = fecha_str + consecutivo_str
        
        return cls(numero)

    @classmethod
    def crear_desde_string(cls, valor: str) -> 'NumeroCuenta':
        """Factory method para crear desde string"""
        return cls(valor)

    @classmethod
    def crear_si_valido(cls, valor: str) -> Optional['NumeroCuenta']:
        """Factory method que retorna None si el número es inválido"""
        try:
            return cls(valor)
        except ValueError:
            return None

    @classmethod
    def proximo_consecutivo_para_hoy(cls, numeros_existentes: list['NumeroCuenta']) -> int:
        """Calcula el próximo consecutivo para hoy basado en números existentes."""
        hoy = date.today()
        consecutivos_hoy = [
            num.get_consecutivo() 
            for num in numeros_existentes 
            if num.es_de_fecha(hoy)
        ]
        
        if not consecutivos_hoy:
            return 1
            
        return max(consecutivos_hoy) + 1