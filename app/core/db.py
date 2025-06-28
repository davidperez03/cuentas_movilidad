from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging
from typing import Generator
from .settings import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

def get_database_url() -> str:
    if settings.debug:
        url = "sqlite:///./database.sqlite"
        logger.info("🔗 Configurando SQLite para desarrollo")
        return url
    else:
        url = settings.database_url_complete
        logger.info("🔗 Configurando PostgreSQL para producción")
        return url

def create_database_engine():
    database_url = get_database_url()
    
    if not database_url:
        logger.warning("⚠️ URL de base de datos no válida, usando SQLite como fallback")
        database_url = "sqlite:///./database.sqlite"
    
    if database_url.startswith("sqlite"):
        engine = create_engine(
            database_url,
            connect_args={
                "check_same_thread": False,
                "timeout": 20, 
            },
            poolclass=StaticPool,
            pool_pre_ping=True,
            echo=settings.debug,
        )
        
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=10000")
            cursor.close()
            
        logger.info("✅ Motor SQLite configurado con optimizaciones")
        
    else:
        engine = create_engine(
            database_url,
            pool_size=5, 
            max_overflow=10, 
            pool_pre_ping=True,
            pool_recycle=3600, 
            echo=settings.debug,  
        )
        logger.info("✅ Motor PostgreSQL configurado con pool de conexiones")
    
    return engine

database_url = get_database_url()
engine = create_database_engine()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False 
)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Error en sesión de base de datos: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tablas de base de datos creadas/verificadas")
    except Exception as e:
        logger.error(f"❌ Error al crear tablas: {str(e)}")
        raise

def get_db_info() -> dict:
    return {
        "url": database_url,
        "type": "SQLite" if database_url.startswith("sqlite") else "PostgreSQL",
        "debug_mode": settings.debug,
        "echo_sql": settings.debug
    }

def test_connection() -> bool:
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"❌ Error de conexión a BD: {str(e)}")
        return False