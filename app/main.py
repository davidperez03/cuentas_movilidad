from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
import uvicorn
import logging
from typing import Dict, Any
from contextlib import asynccontextmanager

from .core.db import get_db, database_url
from .core.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestión del ciclo de vida de la aplicación
    """
    # Startup
    logger.info(f"🚀 Iniciando {settings.app_name}")
    logger.info(f"🔧 Entorno: {'Desarrollo' if settings.debug else 'Producción'}")
    logger.info(f"🗄️ Base de datos: {'SQLite' if database_url.startswith('sqlite') else 'PostgreSQL'}")
    
    yield  # La aplicación está corriendo
    
    # Shutdown
    logger.info("🛑 Cerrando aplicación...")

# Configuración de la aplicación con lifespan
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Sistema de Gestión de Cuentas - API para traslados y radicación de cuentas administrativas",
    docs_url="/docs" if settings.debug else None,  # Solo mostrar docs en desarrollo
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
    debug=settings.debug,
    lifespan=lifespan  # ← Nueva sintaxis
)

@app.get(
    "/salud", 
    summary="Health Check", 
    description="Verifica el estado de la aplicación y la conexión a la base de datos",
    tags=["Sistema"],
    response_model=Dict[str, Any]
)
async def health_check(db: Session = Depends(get_db)):
    """
    Endpoint para verificar la salud del sistema
    
    Returns:
        Dict con el estado del sistema y la base de datos
    """
    try:
        # Verificar conexión a base de datos
        db.execute(text("SELECT 1"))
        db_status = "healthy"
        db_message = "Base de datos conectada correctamente"
    except Exception as e:
        logger.error(f"Error de conexión a BD: {str(e)}")
        db_status = "unhealthy"
        db_message = f"Error de conexión: {str(e)}"
        # En producción, no exponer detalles del error
        if not settings.debug:
            db_message = "Error de conexión a base de datos"
    
    # Determinar tipo de base de datos
    database_type = "SQLite" if database_url.startswith("sqlite") else "PostgreSQL"
    
    response_data = {
        "status": "ok" if db_status == "healthy" else "error",
        "timestamp": None,  # Se puede agregar timestamp si se necesita
        "version": "1.0.0",
        "environment": "development" if settings.debug else "production",
        "database": {
            "status": db_status,
            "type": database_type,
            "message": db_message
        }
    }
    
    if settings.debug:
        response_data["debug_info"] = {
            "database_url": database_url,
            "debug_mode": settings.debug
        }
    
    status_code = 200 if db_status == "healthy" else 503
    return JSONResponse(content=response_data, status_code=status_code)

if settings.debug:
    @app.get(
        "/info", 
        summary="Información del Sistema", 
        description="Información detallada del sistema (solo disponible en desarrollo)",
        tags=["Desarrollo"]
    )
    async def system_info():
        """
        Información detallada del sistema para desarrollo
        """
        from .core.db import get_database_url
        
        return {
            "application": {
                "name": settings.app_name,
                "version": "1.0.0",
                "debug_mode": settings.debug,
                "timezone": settings.timezone
            },
            "database": {
                "current_url": database_url,
                "configured_url": get_database_url(),
                "type": "SQLite" if database_url.startswith("sqlite") else "PostgreSQL",
                "is_consistent": database_url == get_database_url()
            },
            "environment": {
                "postgres_server": settings.postgres_server,
                "postgres_db": settings.postgres_db,
                "postgres_user": settings.postgres_user,
                "postgres_port": settings.postgres_port
            }
        }

# Endpoint raíz
@app.get(
    "/", 
    summary="Página Principal",
    description="Endpoint raíz de la aplicación",
    tags=["Sistema"]
)
async def root():
    """
    Endpoint raíz de la aplicación
    """
    return {
        "message": f"Bienvenido a {settings.app_name}",
        "version": "1.0.0",
        "docs": "/docs" if settings.debug else "Documentación no disponible en producción",
        "health": "/salud"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=settings.debug,
        log_level="info"
    )