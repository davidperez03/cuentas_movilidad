from dataclasses import dataclass
import re
from typing import Optional


@dataclass(frozen=True)
class Placa:
    valor: str

    def __post_init__(self):
        if not self.valor or not self.valor.strip():
            raise ValueError("La placa no puede estar vacía")

        normalizada = re.sub(r"\s+", "", self.valor).upper()

        if self.contiene_letras_invalidas(normalizada):
            raise ValueError(f"La placa contiene letras no válidas: {self.valor}")

        if not self.es_formato_valido(normalizada):
            raise ValueError(f"Formato de placa inválido: {self.valor}")

        object.__setattr__(self, 'valor', normalizada)

    def es_formato_valido(self, placa: str) -> bool:
        return any([
            re.match(r'^[A-Z]{3}[0-9]{3}$', placa),        
            re.match(r'^[A-Z]{3}[0-9]{2}[A-Z]$', placa),   
            re.match(r'^[A-Z]{3}[0-9]{2}$', placa),       
            re.match(r'^[0-9]{3}[A-Z]{3}$', placa),       
        ])

    def contiene_letras_invalidas(self, placa: str) -> bool:
        return bool(re.search(r'[^A-Z0-9]', placa))

    def get_tipo_vehiculo(self) -> str:
        if re.match(r'^[A-Z]{3}[0-9]{3}$', self.valor):
            return "CARRO"
        elif re.match(r'^[A-Z]{3}[0-9]{2}[A-Z]$', self.valor):
            return "MOTO"
        elif re.match(r'^[A-Z]{3}[0-9]{2}$', self.valor):
            return "MOTO"
        elif re.match(r'^[0-9]{3}[A-Z]{3}$', self.valor):
            return "MOTOCARRO"
        return "DESCONOCIDO"

    def es_carro(self) -> bool:
        return self.get_tipo_vehiculo() == "CARRO"

    def es_moto(self) -> bool:
        return self.get_tipo_vehiculo() == "MOTO"

    def es_motocarro(self) -> bool:
        return self.get_tipo_vehiculo() == "MOTOCARRO"

    def __str__(self) -> str:
        return self.valor

    def __repr__(self) -> str:
        return f"Placa('{self.valor}', tipo={self.get_tipo_vehiculo()})"

    @classmethod
    def crear_desde_string(cls, valor: str) -> 'Placa':
        return cls(valor)

    @classmethod
    def crear_si_valida(cls, valor: str) -> Optional['Placa']:
        try:
            return cls(valor)
        except ValueError:
            return None