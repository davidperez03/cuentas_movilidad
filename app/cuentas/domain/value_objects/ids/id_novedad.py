from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional
import uuid
import re


@dataclass(frozen=True)
class IdentificadorNovedad:
    """
    Value Object para identificadores únicos de novedades.
    
    Controla la trazabilidad y numeración secuencial de novedades
    en procesos de traslado y radicación.
    """
    codigo: str  
    fecha_creacion: date  
    consecutivo: int 
    uuid_interno: str  

    def __post_init__(self):
        if not self.codigo or not self.codigo.strip():
            raise ValueError("El código de novedad no puede estar vacío")
        
        if not self._es_formato_valido(self.codigo):
            raise ValueError(f"Formato de código inválido: {self.codigo}")
        
        if not isinstance(self.fecha_creacion, date):
            raise ValueError("La fecha de creación debe ser un objeto date")
        
        if self.consecutivo < 1 or self.consecutivo > 9999:
            raise ValueError("El consecutivo debe estar entre 1 y 9999")
        
        if not self._es_uuid_valido(self.uuid_interno):
            raise ValueError("UUID interno inválido")

    def _es_formato_valido(self, codigo: str) -> bool:
        """Valida formato NOV-YYYYMMDD-NNNN"""
        patron = r'^NOV-\d{8}-\d{4}$'
        return bool(re.match(patron, codigo))

    def _es_uuid_valido(self, uuid_str: str) -> bool:
        """Valida que sea un UUID válido"""
        try:
            uuid.UUID(uuid_str)
            return True
        except ValueError:
            return False

    def get_fecha_string(self) -> str:
        """Retorna fecha en formato YYYYMMDD"""
        return self.fecha_creacion.strftime("%Y%m%d")

    def get_year(self) -> int:
        """Retorna el año de creación"""
        return self.fecha_creacion.year

    def get_month(self) -> int:
        """Retorna el mes de creación"""
        return self.fecha_creacion.month

    def get_day(self) -> int:
        """Retorna el día de creación"""
        return self.fecha_creacion.day

    def es_de_hoy(self) -> bool:
        """Verifica si la novedad fue creada hoy"""
        return self.fecha_creacion == date.today()

    def es_de_fecha(self, fecha: date) -> bool:
        """Verifica si la novedad es de una fecha específica"""
        return self.fecha_creacion == fecha

    def dias_desde_creacion(self) -> int:
        """Calcula días transcurridos desde la creación"""
        return (date.today() - self.fecha_creacion).days

    def formato_display(self) -> str:
        """Formato para mostrar en UI: NOV-2024/12/04-0001"""
        fecha_display = self.fecha_creacion.strftime("%Y/%m/%d")
        return f"NOV-{fecha_display}-{self.consecutivo:04d}"

    def formato_corto(self) -> str:
        """Formato corto: NOV-1204-0001"""
        fecha_corta = self.fecha_creacion.strftime("%m%d")
        return f"NOV-{fecha_corta}-{self.consecutivo:04d}"

    def __str__(self) -> str:
        return self.codigo

    def __repr__(self) -> str:
        return f"IdentificadorNovedad(codigo='{self.codigo}', fecha={self.fecha_creacion}, consecutivo={self.consecutivo})"

    @classmethod
    def generar_para_hoy(cls, consecutivo: int) -> 'IdentificadorNovedad':
        """Genera identificador para hoy con consecutivo específico"""
        hoy = date.today()
        return cls.generar_para_fecha(hoy, consecutivo)

    @classmethod
    def generar_para_fecha(cls, fecha: date, consecutivo: int) -> 'IdentificadorNovedad':
        """Genera identificador para fecha específica"""
        if not isinstance(fecha, date):
            raise ValueError("La fecha debe ser un objeto date")
        
        if consecutivo < 1 or consecutivo > 9999:
            raise ValueError("El consecutivo debe estar entre 1 y 9999")
        
        fecha_str = fecha.strftime("%Y%m%d")
        codigo = f"NOV-{fecha_str}-{consecutivo:04d}"
        uuid_interno = str(uuid.uuid4())
        
        return cls(
            codigo=codigo,
            fecha_creacion=fecha,
            consecutivo=consecutivo,
            uuid_interno=uuid_interno
        )

    @classmethod
    def crear_desde_codigo(cls, codigo: str) -> 'IdentificadorNovedad':
        """Crea identificador desde código existente"""
        if not re.match(r'^NOV-\d{8}-\d{4}$', codigo):
            raise ValueError(f"Formato de código inválido: {codigo}")
        
        partes = codigo.split('-')
        fecha_str = partes[1]
        consecutivo = int(partes[2])
        
        year = int(fecha_str[:4])
        month = int(fecha_str[4:6])
        day = int(fecha_str[6:8])
        fecha = date(year, month, day)
        
        uuid_interno = str(uuid.uuid4())
        
        return cls(
            codigo=codigo,
            fecha_creacion=fecha,
            consecutivo=consecutivo,
            uuid_interno=uuid_interno
        )

    @classmethod
    def crear_si_valido(cls, codigo: str) -> Optional['IdentificadorNovedad']:
        """Factory method que retorna None si el código es inválido"""
        try:
            return cls.crear_desde_codigo(codigo)
        except ValueError:
            return None

    @classmethod
    def proximo_consecutivo_para_hoy(cls, identificadores_existentes: list['IdentificadorNovedad']) -> int:
        """Calcula el próximo consecutivo para hoy"""
        hoy = date.today()
        consecutivos_hoy = [
            ident.consecutivo
            for ident in identificadores_existentes
            if ident.es_de_fecha(hoy)
        ]
        
        if not consecutivos_hoy:
            return 1
        
        return max(consecutivos_hoy) + 1

    @classmethod
    def obtener_por_fecha(cls, identificadores: list['IdentificadorNovedad'], 
                         fecha: date) -> list['IdentificadorNovedad']:
        """Filtra identificadores por fecha específica"""
        return [ident for ident in identificadores if ident.es_de_fecha(fecha)]

    @classmethod
    def obtener_del_mes(cls, identificadores: list['IdentificadorNovedad'], 
                       year: int, month: int) -> list['IdentificadorNovedad']:
        """Filtra identificadores por año y mes"""
        return [
            ident for ident in identificadores 
            if ident.get_year() == year and ident.get_month() == month
        ]


@dataclass(frozen=True)
class ReporteNovedad:
    """
    Value Object para información básica de reporte de novedades.
    
    Complementa el IdentificadorNovedad con datos de quién y cuándo reporta.
    """
    identificador: IdentificadorNovedad
    funcionario_reporta: str 
    timestamp_reporte: datetime  
    descripcion_corta: str 

    def __post_init__(self):
        if not self.funcionario_reporta or not self.funcionario_reporta.strip():
            raise ValueError("El funcionario que reporta no puede estar vacío")
        
        if not self.descripcion_corta or not self.descripcion_corta.strip():
            raise ValueError("La descripción no puede estar vacía")
        
        if len(self.descripcion_corta.strip()) > 200:
            raise ValueError("La descripción no puede exceder 200 caracteres")
        
        if not isinstance(self.timestamp_reporte, datetime):
            raise ValueError("El timestamp debe ser un objeto datetime")

        object.__setattr__(self, 'funcionario_reporta', self.funcionario_reporta.strip().upper())
        object.__setattr__(self, 'descripcion_corta', self.descripcion_corta.strip())

    def get_fecha_reporte(self) -> date:
        """Retorna la fecha del reporte (sin hora)"""
        return self.timestamp_reporte.date()

    def get_hora_reporte(self) -> str:
        """Retorna la hora del reporte en formato HH:MM"""
        return self.timestamp_reporte.strftime("%H:%M")

    def get_timestamp_display(self) -> str:
        """Formato completo: DD/MM/YYYY HH:MM"""
        return self.timestamp_reporte.strftime("%d/%m/%Y %H:%M")

    def es_reporte_reciente(self, horas: int = 24) -> bool:
        """Verifica si el reporte es reciente (últimas N horas)"""
        ahora = datetime.now()
        diferencia = ahora - self.timestamp_reporte
        return diferencia.total_seconds() <= (horas * 3600)

    def get_codigo_novedad(self) -> str:
        """Retorna el código de la novedad"""
        return self.identificador.codigo

    def get_info_completa(self) -> str:
        """Información completa para logs"""
        return f"{self.identificador.codigo} | {self.funcionario_reporta} | {self.get_timestamp_display()}"

    def __str__(self) -> str:
        return f"{self.identificador.codigo} - {self.descripcion_corta}"

    def __repr__(self) -> str:
        return f"ReporteNovedad(codigo='{self.identificador.codigo}', funcionario='{self.funcionario_reporta}')"

    @classmethod
    def crear_nuevo(cls, funcionario_id: str, descripcion: str, 
                   consecutivo_novedad: int) -> 'ReporteNovedad':
        """Factory method para crear nuevo reporte"""
        identificador = IdentificadorNovedad.generar_para_hoy(consecutivo_novedad)
        timestamp = datetime.now()
        
        return cls(
            identificador=identificador,
            funcionario_reporta=funcionario_id,
            timestamp_reporte=timestamp,
            descripcion_corta=descripcion
        )

    @classmethod
    def crear_desde_existente(cls, identificador: IdentificadorNovedad,
                             funcionario_id: str, descripcion: str,
                             timestamp: Optional[datetime] = None) -> 'ReporteNovedad':
        """Factory method desde identificador existente"""
        if timestamp is None:
            timestamp = datetime.now()
        
        return cls(
            identificador=identificador,
            funcionario_reporta=funcionario_id,
            timestamp_reporte=timestamp,
            descripcion_corta=descripcion
        )