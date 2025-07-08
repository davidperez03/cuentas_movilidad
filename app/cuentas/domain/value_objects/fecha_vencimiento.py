from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional
from .fecha_tramite import FechaTramite


@dataclass(frozen=True)
class FechaVencimiento:
    """
    Value Object para fechas de vencimiento calculadas automáticamente.
    
    - Calculada como: fecha_tramite + 60 días (regla global del sistema)
    - Permite fechas pasadas (para trámites retroactivos que ya vencieron)
    - Control de plazos para traslados y radicaciones
    - Alertas automáticas por vencimiento
    """
    fecha: date

    def __post_init__(self):
        if not isinstance(self.fecha, date):
            raise ValueError("La fecha de vencimiento debe ser un objeto date válido")

    def esta_vencida(self) -> bool:
        """Verifica si la fecha de vencimiento ya pasó"""
        return self.fecha < date.today()

    def esta_vigente(self) -> bool:
        """Verifica si la fecha de vencimiento aún está vigente (incluye hoy)"""
        return self.fecha >= date.today()

    def es_hoy(self) -> bool:
        """Verifica si la fecha de vencimiento es hoy (último día válido)"""
        return self.fecha == date.today()

    def dias_restantes(self) -> int:
        """
        Calcula días restantes hasta el vencimiento
        
        Returns:
            int: Días restantes (negativo si ya venció)
        """
        return (self.fecha - date.today()).days

    def semanas_restantes(self) -> int:
        """Calcula semanas restantes hasta el vencimiento"""
        dias = self.dias_restantes()
        return dias // 7 if dias > 0 else 0

    def esta_por_vencer(self, dias_alerta: int = 7) -> bool:
        """
        Verifica si está por vencer (dentro del período de alerta)
        
        Args:
            dias_alerta: Días de anticipación para alerta (por defecto 7)
        """
        dias_restantes = self.dias_restantes()
        return 0 <= dias_restantes <= dias_alerta

    def es_critica(self, dias_criticos: int = 3) -> bool:
        """
        Verifica si está en período crítico (muy cerca del vencimiento)
        
        Args:
            dias_criticos: Días considerados críticos (por defecto 3)
        """
        dias_restantes = self.dias_restantes()
        return 0 <= dias_restantes <= dias_criticos

    def nivel_urgencia(self) -> str:
        """
        Determina el nivel de urgencia basado en días restantes
        
        Returns:
            str: "vencida", "critica", "alerta", "normal"
        """
        dias = self.dias_restantes()
        
        if dias < 0:
            return "vencida"
        elif dias <= 3:
            return "critica"
        elif dias <= 7:
            return "alerta"
        else:
            return "normal"

    def color_indicador(self) -> str:
        """
        Retorna color para indicadores visuales según urgencia
        
        Returns:
            str: Código de color ("red", "orange", "yellow", "green")
        """
        nivel = self.nivel_urgencia()
        colores = {
            "vencida": "red",
            "critica": "orange", 
            "alerta": "yellow",
            "normal": "green"
        }
        return colores[nivel]

    def porcentaje_transcurrido(self, fecha_inicio: date) -> float:
        """
        Calcula porcentaje del período transcurrido
        
        Args:
            fecha_inicio: Fecha de inicio del período (fecha_tramite)
            
        Returns:
            float: Porcentaje transcurrido (0-100)
        """
        if fecha_inicio >= self.fecha:
            return 100.0
        
        periodo_total = (self.fecha - fecha_inicio).days
        periodo_transcurrido = (date.today() - fecha_inicio).days
        
        if periodo_transcurrido <= 0:
            return 0.0
        elif periodo_transcurrido >= periodo_total:
            return 100.0
        else:
            return (periodo_transcurrido / periodo_total) * 100

    def get_year(self) -> int:
        """Obtiene el año de vencimiento"""
        return self.fecha.year

    def get_month(self) -> int:
        """Obtiene el mes de vencimiento"""
        return self.fecha.month

    def get_day(self) -> int:
        """Obtiene el día de vencimiento"""
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

    def es_fin_de_semana(self) -> bool:
        """Verifica si el vencimiento cae en fin de semana"""
        return self.fecha.weekday() >= 5

    def siguiente_dia_laboral_si_fin_de_semana(self) -> date:
        """
        Retorna el siguiente día laboral si el vencimiento cae en fin de semana
        (útil para sistemas que no operan fines de semana)
        """
        if not self.es_fin_de_semana():
            return self.fecha
        
        fecha_temp = self.fecha
        while fecha_temp.weekday() >= 5:
            fecha_temp += timedelta(days=1)
        return fecha_temp

    def formato_legible(self) -> str:
        """Retorna formato legible: YYYY-MM-DD"""
        return self.fecha.strftime("%Y-%m-%d")

    def formato_español(self) -> str:
        """Retorna formato en español: DD/MM/YYYY"""
        return self.fecha.strftime("%d/%m/%Y")

    def formato_con_urgencia(self) -> str:
        """Retorna formato con indicador de urgencia"""
        base = self.formato_español()
        nivel = self.nivel_urgencia()
        
        indicadores = {
            "vencida": f"{base} ⚠️ VENCIDA",
            "critica": f"{base} 🔴 CRÍTICA",
            "alerta": f"{base} 🟡 ALERTA",
            "normal": f"{base} 🟢"
        }
        return indicadores[nivel]

    def formato_con_dias_restantes(self) -> str:
        """Retorna formato con días restantes"""
        dias = self.dias_restantes()
        base = self.formato_español()
        
        if dias < 0:
            return f"{base} (Vencida hace {abs(dias)} días)"
        elif dias == 0:
            return f"{base} (Vence HOY)"
        elif dias == 1:
            return f"{base} (Vence MAÑANA)"
        else:
            return f"{base} (Faltan {dias} días)"

    def __str__(self) -> str:
        return str(self.fecha)

    def __repr__(self) -> str:
        dias = self.dias_restantes()
        nivel = self.nivel_urgencia()
        return f"FechaVencimiento(fecha={self.fecha}, dias_restantes={dias}, urgencia={nivel})"

    @classmethod
    def calcular_desde_tramite(cls, fecha_tramite: FechaTramite) -> 'FechaVencimiento':
        """
        Factory method: calcula vencimiento desde fecha de trámite
        
        Args:
            fecha_tramite: Fecha de trámite base
            
        Returns:
            FechaVencimiento: fecha_tramite + 60 días
        """
        fecha_vencimiento = fecha_tramite.fecha + timedelta(days=60)
        return cls(fecha_vencimiento)

    @classmethod
    def calcular_desde_fecha(cls, fecha_tramite: date, dias_vencimiento: int = 60) -> 'FechaVencimiento':
        """
        Factory method: calcula vencimiento desde fecha específica
        
        Args:
            fecha_tramite: Fecha base
            dias_vencimiento: Días a agregar (por defecto 60)
        """
        fecha_vencimiento = fecha_tramite + timedelta(days=dias_vencimiento)
        return cls(fecha_vencimiento)

    @classmethod
    def crear_para_fecha(cls, fecha: date) -> 'FechaVencimiento':
        """Factory method: crea vencimiento para fecha específica"""
        return cls(fecha)

    @classmethod
    def crear_si_valida(cls, fecha: date) -> Optional['FechaVencimiento']:
        """Factory method que retorna None si la fecha es inválida"""
        try:
            return cls(fecha)
        except ValueError:
            return None

    @classmethod
    def obtener_vencimientos_proximos(cls, vencimientos: list['FechaVencimiento'], 
                                    dias_alerta: int = 7) -> list['FechaVencimiento']:
        """
        Filtra vencimientos próximos dentro del período de alerta
        
        Args:
            vencimientos: Lista de fechas de vencimiento
            dias_alerta: Días de anticipación para considerar "próximo"
            
        Returns:
            list: Vencimientos que están por vencer
        """
        return [v for v in vencimientos if v.esta_por_vencer(dias_alerta)]

    @classmethod
    def obtener_vencimientos_criticos(cls, vencimientos: list['FechaVencimiento']) -> list['FechaVencimiento']:
        """
        Filtra vencimientos en estado crítico (3 días o menos)
        
        Args:
            vencimientos: Lista de fechas de vencimiento
            
        Returns:
            list: Vencimientos críticos
        """
        return [v for v in vencimientos if v.es_critica()]

    @classmethod  
    def obtener_vencimientos_por_nivel(cls, vencimientos: list['FechaVencimiento']) -> dict[str, list['FechaVencimiento']]:
        """
        Agrupa vencimientos por nivel de urgencia
        
        Args:
            vencimientos: Lista de fechas de vencimiento
            
        Returns:
            dict: Vencimientos agrupados por nivel
        """
        grupos = {"vencida": [], "critica": [], "alerta": [], "normal": []}
        
        for vencimiento in vencimientos:
            nivel = vencimiento.nivel_urgencia()
            grupos[nivel].append(vencimiento)
        
        return grupos