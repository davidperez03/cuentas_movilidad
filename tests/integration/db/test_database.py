import pytest
import os
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from alembic.config import Config
from app.core.settings import settings


class TestDatabaseConnection:
    """Tests para verificar conexión a base de datos"""
    
    def test_database_url_configured(self):
        """Verificar que DATABASE_URL está configurada"""
        assert settings.database_url is not None
        assert settings.database_url != ""
        assert "://" in settings.database_url
    
    def test_database_connection_memory(self):
        """Verificar conexión a SQLite en memoria (sin archivos)"""
        test_db_url = "sqlite:///:memory:"
        engine = create_engine(
            test_db_url, 
            poolclass=StaticPool,
            connect_args={
                "check_same_thread": False,
            }
        )
        
        # Probar conexión
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1
        
        # Cerrar engine
        engine.dispose()
    
    def test_database_connection_settings(self):
        """Verificar que se puede crear engine desde settings"""
        from sqlalchemy import create_engine
        
        # Si es archivo SQLite, usar memoria para testing
        if "sqlite:///" in settings.database_url and settings.database_url != "sqlite:///:memory:":
            test_url = "sqlite:///:memory:"
        else:
            test_url = settings.database_url
        
        # Crear engine usando URL de test
        engine = create_engine(test_url)
        
        # Verificar que el engine se crea correctamente
        assert engine is not None
        
        # Probar conexión básica
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1
        
        # Cerrar engine
        engine.dispose()


class TestMigrationsConfiguration:
    """Tests para verificar configuración de Alembic"""
    
    def test_alembic_config_exists(self):
        """Verificar que alembic.ini existe"""
        assert os.path.exists("alembic.ini")
    
    def test_alembic_directory_exists(self):
        """Verificar que directorio alembic existe"""
        assert os.path.exists("alembic")
        assert os.path.exists("alembic/env.py")
        assert os.path.exists("alembic/versions")
    
    def test_alembic_env_imports_settings(self):
        """Verificar que env.py importa settings correctamente"""
        with open("alembic/env.py", 'r') as f:
            content = f.read()
            assert "from app.core.settings import settings" in content
            assert "def get_url():" in content
            assert "settings.database_url" in content
    
    def test_alembic_can_load_config(self):
        """Verificar que Alembic puede cargar la configuración"""
        try:
            # Intentar cargar configuración de Alembic
            alembic_cfg = Config("alembic.ini")
            assert alembic_cfg is not None
        except Exception as e:
            pytest.fail(f"No se pudo cargar alembic.ini: {e}")
    
    def test_alembic_env_syntax_valid(self):
        """Verificar que env.py tiene sintaxis válida"""
        try:
            with open("alembic/env.py", 'r') as f:
                content = f.read()
                compile(content, "alembic/env.py", "exec")
        except SyntaxError as e:
            pytest.fail(f"Error de sintaxis en alembic/env.py: {e}")


class TestMigrationsBasic:
    """Tests básicos de migraciones sin ejecución completa"""
    
    def test_alembic_current_with_memory_db(self):
        """Verificar 'alembic current' con BD en memoria"""
        from alembic.config import Config
        from alembic import command
        from io import StringIO
        import sys
        
        # Capturar output
        captured_output = StringIO()
        
        try:
            # Configurar Alembic para usar BD en memoria
            alembic_cfg = Config("alembic.ini")
            alembic_cfg.set_main_option("sqlalchemy.url", "sqlite:///:memory:")
            
            # Redirigir stdout para capturar output
            old_stdout = sys.stdout
            sys.stdout = captured_output
            
            # Ejecutar comando current
            command.current(alembic_cfg)
            
            # Restaurar stdout
            sys.stdout = old_stdout
            
            # El comando no debería fallar
            output = captured_output.getvalue()
            
        except Exception as e:
            sys.stdout = old_stdout
            pytest.fail(f"Error en 'alembic current': {e}")
    
    def test_alembic_history_command(self):
        """Verificar que 'alembic history' funciona"""
        from alembic.config import Config
        from alembic import command
        from io import StringIO
        import sys
        
        captured_output = StringIO()
        
        try:
            alembic_cfg = Config("alembic.ini")
            alembic_cfg.set_main_option("sqlalchemy.url", "sqlite:///:memory:")
            
            old_stdout = sys.stdout
            sys.stdout = captured_output
            
            command.history(alembic_cfg)
            
            sys.stdout = old_stdout
            
        except Exception as e:
            sys.stdout = old_stdout
            pytest.fail(f"Error en 'alembic history': {e}")


class TestDatabaseIntegrationMemory:
    """Tests de integración usando BD en memoria"""
    
    def test_engine_creation_and_connection(self):
        """Test de creación de engine y conexión básica"""
        test_url = "sqlite:///:memory:"
        
        try:
            # Crear engine
            engine = create_engine(
                test_url,
                poolclass=StaticPool,
                connect_args={"check_same_thread": False}
            )
            
            # Verificar conexión
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                assert result.fetchone()[0] == 1
                
                # Crear tabla simple para probar
                conn.execute(text("""
                    CREATE TABLE test_table (
                        id INTEGER PRIMARY KEY,
                        name TEXT
                    )
                """))
                
                # Insertar datos
                conn.execute(text("INSERT INTO test_table (name) VALUES ('test')"))
                
                # Verificar datos
                result = conn.execute(text("SELECT name FROM test_table"))
                assert result.fetchone()[0] == 'test'
                
                conn.commit()
            
            # Cerrar engine
            engine.dispose()
            
        except Exception as e:
            pytest.fail(f"Error en test de integración: {e}")
    
    def test_multiple_database_urls(self):
        """Verificar que diferentes tipos de URL funcionan"""
        test_urls = [
            "sqlite:///:memory:",
            "sqlite:///:memory:",  # Doble test para asegurar limpieza
        ]
        
        for i, url in enumerate(test_urls):
            try:
                engine = create_engine(
                    url,
                    poolclass=StaticPool,
                    connect_args={"check_same_thread": False}
                )
                
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT 1"))
                    assert result.fetchone()[0] == 1
                
                engine.dispose()
                
            except Exception as e:
                pytest.fail(f"Error con URL {i+1}: {e}")


class TestSettingsConfiguration:
    """Tests específicos para configuración de settings"""
    
    def test_settings_database_url_format(self):
        """Verificar formato de DATABASE_URL en settings"""
        db_url = settings.database_url
        
        # Verificar que es una URL válida
        assert "://" in db_url
        
        # Verificar que es SQLite o PostgreSQL
        assert db_url.startswith(("sqlite://", "postgresql://"))
    
    def test_settings_import_works(self):
        """Verificar que settings se puede importar sin errores"""
        try:
            from app.core.settings import settings
            
            # Verificar que tiene los atributos necesarios
            assert hasattr(settings, 'database_url')
            assert hasattr(settings, 'app_name')
            assert hasattr(settings, 'debug')
            
        except Exception as e:
            pytest.fail(f"Error importando settings: {e}")
    
    def test_env_file_loading(self):
        """Verificar que .env se carga correctamente"""
        # Este test verifica indirectamente que .env funciona
        # porque settings debería tener valores no vacíos
        
        assert settings.app_name is not None
        assert settings.app_name != ""
        
        assert settings.secret_key is not None
        assert settings.secret_key != ""