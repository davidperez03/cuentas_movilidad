from pydantic_settings import BaseSettings
from pydantic import ConfigDict, AnyUrl, EmailStr, AnyHttpUrl
from typing import Optional

class Settings(BaseSettings):
    """Configuración básica"""
    app_name: str
    debug: bool
    secret_key: str
    algorithm: str
    app_base_url: AnyHttpUrl
    
    """Configuración de base de datos"""
    database_url: Optional[str] = None
    
    """PostgreSQL específico (para producción)"""
    postgres_server: Optional[str] = None
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None
    postgres_db: Optional[str] = None
    postgres_port: Optional[int] = 5432

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
    )

    timezone: str = "America/Bogota"
    
    @property
    def database_url_complete(self) -> str:
        """
        Construye la URL completa de PostgreSQL si no está definida
        """
        if self.database_url:
            return self.database_url
        elif not self.debug and self.postgres_server:
            return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"
        else:
            return "sqlite:///./database.sqlite"

settings = Settings()