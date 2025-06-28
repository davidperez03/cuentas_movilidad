# tests/conftest.py
import pytest
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from app.core.settings import settings


# Fixtures para PostgreSQL
@pytest.fixture(scope="session")
def postgres_url():
    """URL de PostgreSQL desde variables de entorno"""
    if settings.database_url.startswith("postgresql://"):
        return settings.database_url
    
    # Construir desde variables individuales si no está en DATABASE_URL
    postgres_user = os.getenv("POSTGRES_USER", "postgres")
    postgres_password = os.getenv("POSTGRES_PASSWORD", "12345678")
    postgres_server = os.getenv("POSTGRES_SERVER", "localhost")
    postgres_port = os.getenv("POSTGRES_PORT", "5432")
    postgres_db = os.getenv("POSTGRES_DB", "pruebas_db")
    
    return f"postgresql://{postgres_user}:{postgres_password}@{postgres_server}:{postgres_port}/{postgres_db}"


@pytest.fixture(scope="session")
def postgres_available(postgres_url):
    """Verificar si PostgreSQL está disponible"""
    try:
        engine = create_engine(postgres_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine.dispose()
        return True
    except OperationalError:
        return False


@pytest.fixture
def postgres_engine(postgres_url, postgres_available):
    """Engine de PostgreSQL con cleanup automático"""
    if not postgres_available:
        pytest.skip("PostgreSQL no disponible")
    
    engine = create_engine(postgres_url)
    yield engine
    engine.dispose()


@pytest.fixture
def postgres_temp_table(postgres_engine):
    """Tabla temporal de PostgreSQL con cleanup automático"""
    table_name = "test_temp_table"
    
    with postgres_engine.connect() as conn:
        # Crear tabla temporal
        conn.execute(text(f"""
            CREATE TEMPORARY TABLE {table_name} (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.commit()
    
    yield postgres_engine, table_name
    
    # Cleanup automático (las tablas TEMPORARY se eliminan automáticamente)


# Configuración de markers
def pytest_configure(config):
    """Configuración automática de markers"""
    config.addinivalue_line("markers", "unit: Tests unitarios")
    config.addinivalue_line("markers", "integration: Tests de integración")
    config.addinivalue_line("markers", "postgres: Tests que requieren PostgreSQL")
    config.addinivalue_line("markers", "slow: Tests que tardan más de 30 segundos")


def pytest_collection_modifyitems(config, items):
    """Modificar items de test automáticamente"""
    for item in items:
        # Auto-skip tests de PostgreSQL si no está disponible
        if "postgres" in item.keywords:
            if not settings.database_url.startswith("postgresql://"):
                item.add_marker(pytest.mark.skip(
                    reason="PostgreSQL no configurado en DATABASE_URL"
                ))
        
        # Auto-marcar tests por directorio
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)