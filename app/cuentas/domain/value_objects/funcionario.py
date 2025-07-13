from dataclasses import dataclass
from typing import Optional
import re
from enum import Enum


class CargoFuncionario(Enum):
    """Cargos/roles de funcionarios en el sistema"""
    FUNCIONARIO = "funcionario"
    SUPERVISOR = "supervisor"
    ADMINISTRADOR = "administrador"


@dataclass(frozen=True)
class Funcionario:
    """
    Value Object temporal para funcionarios del sistema.

    Será reemplazado por datos del módulo AUTH cuando esté implementado.
    Maneja información básica de funcionarios para trazabilidad.
    """
    id_funcionario: str
    nombre_completo: str
    cargo: CargoFuncionario
    email: Optional[str] = None
    activo: bool = True

    def __post_init__(self):
        if not self.id_funcionario or not self.id_funcionario.strip():
            raise ValueError("El ID del funcionario no puede estar vacío")

        if not self.nombre_completo or not self.nombre_completo.strip():
            raise ValueError("El nombre completo no puede estar vacío")

        if len(self.nombre_completo.strip()) < 3:
            raise ValueError("El nombre completo debe tener al menos 3 caracteres")

        id_normalizado = re.sub(r'\s+', '', self.id_funcionario.strip().upper())
        object.__setattr__(self, 'id_funcionario', id_normalizado)

        nombre_normalizado = ' '.join(word.capitalize() for word in self.nombre_completo.strip().split())
        object.__setattr__(self, 'nombre_completo', nombre_normalizado)

        if self.email:
            email_normalizado = self.email.strip().lower()
            if not self._es_email_valido(email_normalizado):
                raise ValueError(f"Email inválido: {self.email}")
            object.__setattr__(self, 'email', email_normalizado)

    def _es_email_valido(self, email: str) -> bool:
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(patron, email.strip()))

    def get_nombre_corto(self) -> str:
        partes = self.nombre_completo.split()
        if len(partes) >= 2:
            return f"{partes[0]} {partes[1]}"
        return partes[0] if partes else self.nombre_completo

    def get_iniciales(self) -> str:
        return ''.join(word[0].upper() for word in self.nombre_completo.split() if word)

    def get_cargo_display(self) -> str:
        return self.cargo.value.title()

    def get_nombre_con_cargo(self) -> str:
        return f"{self.nombre_completo} ({self.get_cargo_display()})"

    def es_supervisor_o_superior(self) -> bool:
        return self.cargo in {CargoFuncionario.SUPERVISOR, CargoFuncionario.ADMINISTRADOR}

    def puede_aprobar_procesos(self) -> bool:
        return self.cargo == CargoFuncionario.ADMINISTRADOR

    def es_administrador(self) -> bool:
        return self.cargo == CargoFuncionario.ADMINISTRADOR

    def esta_activo(self) -> bool:
        return self.activo

    def __str__(self) -> str:
        return self.nombre_completo

    def __repr__(self) -> str:
        estado = "activo" if self.activo else "inactivo"
        return f"Funcionario(id='{self.id_funcionario}', nombre='{self.nombre_completo}', cargo='{self.cargo.value}', estado='{estado}')"

    def to_dict(self) -> dict:
        return {
            "id": self.id_funcionario,
            "nombre": self.nombre_completo,
            "cargo": self.cargo.value,
            "email": self.email,
            "activo": self.activo
        }

    @classmethod
    def crear_funcionario_basico(cls, id_funcionario: str, nombre: str) -> 'Funcionario':
        return cls(
            id_funcionario=id_funcionario,
            nombre_completo=nombre,
            cargo=CargoFuncionario.FUNCIONARIO
        )

    @classmethod
    def crear_desde_auth(cls, datos_auth: dict) -> 'Funcionario':
        try:
            role_mapping = {
                'funcionario': CargoFuncionario.FUNCIONARIO,
                'supervisor': CargoFuncionario.SUPERVISOR,
                'admin': CargoFuncionario.ADMINISTRADOR,
                'administrador': CargoFuncionario.ADMINISTRADOR
            }
            cargo = role_mapping.get(
                datos_auth.get('role', '').lower(),
                CargoFuncionario.FUNCIONARIO
            )
            return cls(
                id_funcionario=datos_auth['user_id'],
                nombre_completo=datos_auth['full_name'],
                cargo=cargo,
                email=datos_auth.get('email'),
                activo=datos_auth.get('is_active', True)
            )
        except (KeyError, ValueError) as e:
            raise ValueError(f"Error procesando datos de AUTH: {e}")

    @classmethod
    def crear_si_valido(cls, id_funcionario: str, nombre: str, cargo: str) -> Optional['Funcionario']:
        try:
            cargo_enum = CargoFuncionario(cargo.lower())
            return cls(
                id_funcionario=id_funcionario,
                nombre_completo=nombre,
                cargo=cargo_enum
            )
        except (ValueError, TypeError):
            return None


class FuncionariosPredefinidos:
    """Funcionarios conocidos del sistema para pruebas"""

    LUIS_MURCIA = Funcionario(
        id_funcionario="LMURCIA001",
        nombre_completo="Luis Fabian Murcia Salinas",
        cargo=CargoFuncionario.FUNCIONARIO,
        email="luis.murcia@organismo.gov.co"
    )

    ANA_RODRIGUEZ = Funcionario(
        id_funcionario="ARODRIGUEZ002",
        nombre_completo="Ana Maria Rodriguez Gomez",
        cargo=CargoFuncionario.SUPERVISOR,
        email="ana.rodriguez@organismo.gov.co"
    )

    CARLOS_LOPEZ = Funcionario(
        id_funcionario="CLOPEZ003",
        nombre_completo="Carlos Eduardo Lopez Perez",
        cargo=CargoFuncionario.SUPERVISOR,
        email="carlos.lopez@organismo.gov.co"
    )

    MARIA_GARCIA = Funcionario(
        id_funcionario="MGARCIA004",
        nombre_completo="Maria Elena Garcia Torres",
        cargo=CargoFuncionario.SUPERVISOR,
        email="maria.garcia@organismo.gov.co"
    )

    ADMIN_SISTEMA = Funcionario(
        id_funcionario="ADMIN001",
        nombre_completo="Administrador del Sistema",
        cargo=CargoFuncionario.ADMINISTRADOR,
        email="admin@organismo.gov.co"
    )

    @classmethod
    def obtener_todos(cls) -> list[Funcionario]:
        return [
            cls.LUIS_MURCIA,
            cls.ANA_RODRIGUEZ,
            cls.CARLOS_LOPEZ,
            cls.MARIA_GARCIA,
            cls.ADMIN_SISTEMA
        ]

    @classmethod
    def obtener_por_id(cls, id_funcionario: str) -> Optional[Funcionario]:
        id_normalizado = id_funcionario.upper().replace(' ', '')
        for funcionario in cls.obtener_todos():
            if funcionario.id_funcionario == id_normalizado:
                return funcionario
        return None

    @classmethod
    def obtener_por_cargo(cls, cargo: CargoFuncionario) -> list[Funcionario]:
        return [f for f in cls.obtener_todos() if f.cargo == cargo]

    @classmethod
    def obtener_supervisores_activos(cls) -> list[Funcionario]:
        return [
            f for f in cls.obtener_todos()
            if f.es_supervisor_o_superior() and f.esta_activo()
        ]
