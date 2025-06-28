# tests/integration/test_postgres.py
import pytest
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from app.core.settings import settings


class TestPostgreSQLConnection:
    """Tests para verificar conexión a PostgreSQL"""
    
    @pytest.mark.postgres
    def test_postgres_url_format(self, postgres_url):
        """Verificar formato de URL de PostgreSQL"""
        assert postgres_url.startswith("postgresql://")
        assert "@" in postgres_url
        assert ":" in postgres_url
        
        # Verificar componentes básicos
        parts = postgres_url.replace("postgresql://", "").split("@")
        assert len(parts) == 2
        
        user_pass = parts[0]
        server_db = parts[1]
        
        assert ":" in user_pass  # usuario:password
        assert "/" in server_db  # servidor:puerto/base_datos
    
    @pytest.mark.postgres
    def test_postgres_connection_basic(self, postgres_engine):
        """Verificar conexión básica a PostgreSQL"""
        with postgres_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1
    
    @pytest.mark.postgres
    def test_postgres_database_info(self, postgres_engine):
        """Verificar información de la base de datos"""
        with postgres_engine.connect() as conn:
            result = conn.execute(text("""
                SELECT current_database(), current_user, version()
            """))
            
            db_info = result.fetchone()
            assert db_info is not None
            assert len(db_info) == 3
            assert db_info[0] is not None  # database name
            assert db_info[1] is not None  # user name
            assert "PostgreSQL" in db_info[2]  # version


class TestPostgreSQLOperations:
    """Tests para operaciones CRUD en PostgreSQL"""
    
    @pytest.mark.postgres
    def test_create_table(self, postgres_engine):
        """Test crear tabla temporal"""
        with postgres_engine.connect() as conn:
            conn.execute(text("""
                CREATE TEMPORARY TABLE test_create (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100)
                )
            """))
            
            # Verificar que existe
            result = conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_name = 'test_create'
            """))
            assert result.fetchone()[0] >= 1
    
    @pytest.mark.postgres
    def test_insert_data(self, postgres_temp_table):
        """Test insertar datos"""
        engine, table_name = postgres_temp_table
        
        with engine.connect() as conn:
            conn.execute(text(f"""
                INSERT INTO {table_name} (name) VALUES 
                ('test1'), ('test2'), ('test3')
            """))
            
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            assert result.fetchone()[0] == 3
    
    @pytest.mark.postgres
    def test_update_data(self, postgres_temp_table):
        """Test actualizar datos"""
        engine, table_name = postgres_temp_table
        
        with engine.connect() as conn:
            # Insertar dato inicial
            conn.execute(text(f"INSERT INTO {table_name} (name) VALUES ('original')"))
            
            # Actualizar
            conn.execute(text(f"UPDATE {table_name} SET name = 'updated' WHERE name = 'original'"))
            
            # Verificar
            result = conn.execute(text(f"SELECT name FROM {table_name}"))
            assert result.fetchone()[0] == 'updated'
    
    @pytest.mark.postgres
    def test_delete_data(self, postgres_temp_table):
        """Test eliminar datos"""
        engine, table_name = postgres_temp_table
        
        with engine.connect() as conn:
            # Insertar datos
            conn.execute(text(f"""
                INSERT INTO {table_name} (name) VALUES ('keep'), ('delete')
            """))
            
            # Eliminar uno
            conn.execute(text(f"DELETE FROM {table_name} WHERE name = 'delete'"))
            
            # Verificar
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            assert result.fetchone()[0] == 1
            
            result = conn.execute(text(f"SELECT name FROM {table_name}"))
            assert result.fetchone()[0] == 'keep'


class TestPostgreSQLFeatures:
    """Tests para características específicas de PostgreSQL"""
    
    @pytest.mark.postgres
    def test_generate_series(self, postgres_engine):
        """Test función GENERATE_SERIES de PostgreSQL"""
        with postgres_engine.connect() as conn:
            result = conn.execute(text("SELECT generate_series(1, 3)"))
            numbers = [row[0] for row in result.fetchall()]
            assert numbers == [1, 2, 3]
    
    @pytest.mark.postgres
    def test_array_type(self, postgres_engine):
        """Test tipo ARRAY de PostgreSQL"""
        with postgres_engine.connect() as conn:
            result = conn.execute(text("SELECT ARRAY[1, 2, 3]"))
            array_result = result.fetchone()[0]
            assert array_result == [1, 2, 3]
    
    @pytest.mark.postgres
    def test_json_type(self, postgres_engine):
        """Test tipo JSON de PostgreSQL"""
        with postgres_engine.connect() as conn:
            result = conn.execute(text("SELECT '{\"key\": \"value\"}'::json"))
            json_result = result.fetchone()[0]
            assert json_result == {"key": "value"}


class TestPostgreSQLConfiguration:
    """Tests para configuración de PostgreSQL"""
    
    @pytest.mark.unit
    def test_postgres_env_variables_exist(self):
        """Verificar que las variables de entorno existen"""
        required_vars = [
            "POSTGRES_USER", "POSTGRES_PASSWORD", 
            "POSTGRES_SERVER", "POSTGRES_PORT", "POSTGRES_DB"
        ]
        
        for var in required_vars:
            value = os.getenv(var)
            if value is None:
                pytest.skip(f"Variable de entorno {var} no configurada")
            assert value != "", f"Variable {var} está vacía"
    
    @pytest.mark.unit
    def test_postgres_port_is_numeric(self):
        """Verificar que POSTGRES_PORT es numérico"""
        port = os.getenv("POSTGRES_PORT", "5432")
        assert port.isdigit(), f"POSTGRES_PORT debe ser numérico: {port}"
        assert 1 <= int(port) <= 65535, f"Puerto fuera de rango: {port}"
    
    @pytest.mark.postgres
    def test_connection_pool_parameters(self, postgres_url):
        """Test configuración de pool de conexiones"""
        engine = create_engine(
            postgres_url,
            pool_size=3,
            max_overflow=5,
            pool_timeout=10,
            pool_recycle=1800
        )
        
        try:
            # Probar múltiples conexiones
            connections = []
            for i in range(3):
                conn = engine.connect()
                result = conn.execute(text("SELECT 1"))
                assert result.fetchone()[0] == 1
                connections.append(conn)
            
            # Cerrar conexiones
            for conn in connections:
                conn.close()
                
        finally:
            engine.dispose()


class TestDatabaseComparison:
    """Tests comparativos entre diferentes bases de datos"""
    
    @pytest.mark.integration
    def test_sqlite_vs_postgres_basic_operations(self, postgres_engine):
        """Comparar operaciones básicas entre SQLite y PostgreSQL"""
        # Test SQLite
        sqlite_engine = create_engine("sqlite:///:memory:")
        
        try:
            with sqlite_engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                assert result.fetchone()[0] == 1
        finally:
            sqlite_engine.dispose()
        
        # Test PostgreSQL  
        with postgres_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1
    
    @pytest.mark.postgres
    def test_sql_dialect_compatibility(self, postgres_engine):
        """Test compatibilidad de dialectos SQL"""
        with postgres_engine.connect() as conn:
            # Funciones estándar SQL que deberían funcionar en ambos
            result = conn.execute(text("SELECT CURRENT_TIMESTAMP"))
            assert result.fetchone()[0] is not None
            
            result = conn.execute(text("SELECT UPPER('test')"))
            assert result.fetchone()[0] == 'TEST'
            
            result = conn.execute(text("SELECT LENGTH('test')"))
            assert result.fetchone()[0] == 4