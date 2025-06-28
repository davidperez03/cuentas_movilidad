# 🧪 Documentación de Testing

> Guía completa para ejecutar y mantener tests en el Sistema de Gestión de Cuentas

---

## 📋 Tipos de Tests

### 🚀 Tests Unitarios
Prueban funciones individuales sin dependencias externas.
- **Ubicación:** `tests/unit/`
- **Velocidad:** ⚡ Muy rápida (< 1 segundo)
- **Dependencias:** ❌ Ninguna
- **Cuándo ejecutar:** En cada commit, durante desarrollo

### 🔄 Tests de Integración  
Prueban interacción con servicios externos (BD, APIs).
- **Ubicación:** `tests/integration/`
- **Velocidad:** 🐌 Lenta (5-30 segundos)
- **Dependencias:** ✅ Base de datos, servicios
- **Cuándo ejecutar:** Antes de PR, en CI/CD

### 🎯 Tests End-to-End (E2E)
Prueban flujos completos de usuario.
- **Ubicación:** `tests/e2e/`
- **Velocidad:** 🐌🐌 Muy lenta (30+ segundos)
- **Dependencias:** ✅ Stack completo
- **Cuándo ejecutar:** Antes de releases

### ⚡ Tests de Performance
Prueban rendimiento y tiempos de respuesta.
- **Ubicación:** `tests/performance/`
- **Velocidad:** 🐌 Variable (según carga)
- **Dependencias:** ✅ Datos de prueba, métricas
- **Cuándo ejecutar:** Antes de releases, cambios críticos

### 🐌 Tests Lentos (Slow)
Tests que requieren mucho tiempo o recursos.
- **Marcador:** `@pytest.mark.slow`
- **Velocidad:** 🐌🐌 Muy lenta (30+ segundos)
- **Dependencias:** ✅ Recursos intensivos
- **Cuándo ejecutar:** En CI/CD nocturno, antes de releases

---

## 📁 Estructura de Archivos

```
tests/
├── unit/                          # Tests unitarios
│   ├── test_database_config.py   # Configuración BD sin conexión
│   ├── test_settings.py          # Tests de configuración
│   └── test_helpers.py           # Funciones auxiliares
├── integration/                   # Tests de integración
│   ├── test_database.py          # Conexiones reales a BD
│   ├── test_postgres.py          # Tests específicos PostgreSQL
│   └── test_migrations.py        # Tests de Alembic
├── e2e/                          # Tests end-to-end
│   ├── test_user_journey.py      # Flujos completos de usuario
│   └── test_scenarios.py         # Escenarios de negocio
├── performance/                   # Tests de rendimiento
│   ├── test_database_performance.py
│   └── test_api_performance.py
├── slow/                         # Tests que requieren mucho tiempo
│   ├── test_stress.py            # Tests de estrés
│   └── test_load.py              # Tests de carga
├── fixtures/                     # Datos de prueba
│   ├── database/                 # Datos para BD
│   └── api/                      # Respuestas de ejemplo
└── conftest.py                   # Configuración global
```

---

## ⚡ Comandos de Ejecución

### Ejecutar por Tipo

```bash
# Tests de configuración (verificar archivos y settings)
pytest tests/unit/test_settings.py -v
pytest -m config -v

# Solo tests unitarios (rápidos)
pytest tests/unit/ -v

# Solo tests de integración
pytest tests/integration/ -v

# Tests end-to-end
pytest tests/e2e/ -v

# Tests de rendimiento
pytest tests/performance/ -v

# Tests lentos (ejecutar con tiempo)
pytest tests/slow/ -v
```

### Ejecutar por Marcadores

```bash
# Tests rápidos solamente (excluir lentos)
pytest -m "not slow" -v

# Tests de configuración específicamente
pytest -m config -v

# Tests de base de datos
pytest -m database -v

# Tests que requieren PostgreSQL
pytest -m postgres -v

# Tests unitarios únicamente
pytest -m unit -v

# Tests de rendimiento
pytest -m performance -v
```

### Ejecutar con Cobertura

```bash
# Cobertura completa
pytest --cov=app --cov-report=html

# Cobertura solo unitarios
pytest tests/unit/ --cov=app --cov-report=term

# Cobertura con detalles
pytest --cov=app --cov-report=term-missing
```

---

## 🔧 Instalación y Configuración de Pytest

### 📦 Instalación

#### Opción 1: Instalación Básica
```bash
# Activar entorno virtual
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Instalar pytest
pip install pytest
```

#### Opción 2: Instalación Completa (Recomendada)
```bash
# Instalar pytest con todas las extensiones necesarias
pip install pytest pytest-cov pytest-mock pytest-xdist

# O desde requirements.txt (ya incluido en el proyecto)
pip install -r requirements.txt
```

#### Opción 3: Instalación de Desarrollo
```bash
# Para desarrollo completo con herramientas adicionales
pip install pytest pytest-cov pytest-mock pytest-xdist pytest-html pytest-json-report
```

### ⚙️ Configuración de pytest.ini

El archivo `pytest.ini` en la raíz del proyecto configura el comportamiento de pytest:

```ini
[pytest]
# Directorios donde buscar tests
testpaths = tests

# Patrones de archivos de tests
python_files = test_*.py *_test.py

# Patrones de clases de tests
python_classes = Test*

# Patrones de funciones de tests
python_functions = test_*

# Opciones por defecto
addopts = 
    --strict-markers        # Requiere declarar todos los markers
    --tb=short             # Traceback corto para errores
    --cov=app              # Cobertura del módulo app
    --cov-report=term-missing  # Mostrar líneas faltantes
    --cov-report=html      # Generar reporte HTML
    --cov-config=.coveragerc   # Configuración de cobertura
    -ra                    # Mostrar resumen de todos los tests
    -q                     # Modo silencioso

# Markers personalizados del proyecto
markers =
    unit: Pruebas unitarias (rápidas, sin dependencias externas)
    integration: Pruebas de integración (requieren servicios externos)
    e2e: Pruebas end-to-end (flujos completos)
    performance: Pruebas de rendimiento y carga
    slow: Pruebas que requieren mucho tiempo (>30 segundos)
    config: Pruebas de configuración (archivos, variables, settings)
    database: Pruebas relacionadas con base de datos
    migrations: Pruebas de migraciones de Alembic
    postgres: Pruebas que requieren PostgreSQL
    sqlite: Pruebas que requieren SQLite
    memory_only: Pruebas solo con base de datos en memoria
```

### 📊 Configuración de Cobertura (.coveragerc)

El archivo `.coveragerc` configura la medición de cobertura de código:

```ini
[run]
# Medir cobertura de ramas (if/else)
branch = True

# Módulos a incluir en cobertura
source = app

[report]
# Líneas a excluir del reporte
exclude_lines =
    pragma: no cover           # Líneas marcadas para excluir
    if __name__ == .__main__.: # Bloques de ejecución principal
    @abstractmethod            # Métodos abstractos
    raise NotImplementedError  # Métodos no implementados

[html]
# Directorio para reporte HTML
directory = htmlcov
```

### 🗂️ Estructura de Configuración Completa

```
proyecto/
├── pytest.ini              # ← Configuración principal de pytest
├── .coveragerc             # ← Configuración de cobertura
├── requirements.txt        # ← Incluye pytest y extensiones
├── tests/
│   ├── conftest.py        # ← Fixtures y configuración global
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   ├── performance/
│   └── slow/
└── app/                   # ← Código fuente a probar
```

### 🧪 Verificar Instalación

```bash
# Verificar que pytest está instalado
pytest --version

# Verificar configuración
pytest --markers

# Verificar que puede encontrar tests
pytest --collect-only

# Ejecutar test simple
pytest --version && echo "✅ Pytest configurado correctamente"
```

### 🚀 Configuración de conftest.py

El archivo `tests/conftest.py` contiene fixtures compartidas:

```python
# tests/conftest.py
import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture(scope="session")
def test_database():
    """Fixture de sesión para base de datos de testing"""
    db_url = "sqlite:///:memory:"
    yield db_url


@pytest.fixture
def memory_engine(test_database):
    """Fixture para engine de BD en memoria"""
    engine = create_engine(
        test_database,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False}
    )
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(memory_engine):
    """Fixture para sesión de base de datos"""
    SessionLocal = sessionmaker(bind=memory_engine)
    session = SessionLocal()
    yield session
    session.close()


# Configuración de markers automática
def pytest_configure(config):
    """Configuración automática de markers"""
    config.addinivalue_line("markers", "unit: Tests unitarios")
    config.addinivalue_line("markers", "integration: Tests de integración")
    config.addinivalue_line("markers", "slow: Tests lentos")


def pytest_collection_modifyitems(config, items):
    """Modificar items de test automáticamente"""
    for item in items:
        # Auto-marcar tests por directorio
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "slow" in str(item.fspath):
            item.add_marker(pytest.mark.slow)
```

---

## 🔧 Configuración de Entorno

### Prerrequisitos

```bash
# 1. Activar entorno virtual
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# 2. Verificar que pytest está instalado
pytest --version
# Si no está instalado:
pip install pytest pytest-cov

# 3. Verificar configuración del proyecto
pytest --markers
pytest --collect-only

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con configuración de test
```

### Variables de Entorno para Testing

```env
# Base de datos de testing
DATABASE_URL=sqlite:///:memory:
# O para tests de integración con PostgreSQL:
# DATABASE_URL=postgresql://postgres:password@localhost:5432/test_db

# Configuración de testing
DEBUG=true
SECRET_KEY=test-secret-key-for-testing-only
APP_NAME=Sistema de Gestión de Cuentas - Testing
ALGORITHM=HS256
APP_BASE_URL=http://localhost:8000
```

### 🎯 Comandos de Verificación Inicial

```bash
# Verificar que toda la configuración funciona
pytest --version                    # Versión de pytest
pytest --markers                    # Markers disponibles
pytest --collect-only              # Tests encontrados
pytest tests/unit/ --collect-only  # Tests unitarios encontrados

# Test rápido de configuración
pytest tests/unit/test_settings.py -v  # Si existe
```

---

## ⚙️ Tests de Configuración

### Verificar Archivos de Configuración

```bash
# Tests de archivos de configuración
pytest tests/unit/test_settings.py -v

# Verificar que todos los archivos existen
pytest -k "config" -v
```

**Qué prueban:**
- ✅ Existencia de archivos (`.env.example`, `alembic.ini`, etc.)
- ✅ Formato correcto de variables de entorno
- ✅ Valores por defecto en `settings.py`
- ✅ Importación correcta de módulos
- ✅ Configuración de pytest, alembic, coverage

## 🗄️ Tests de Base de Datos

### Tests Unitarios de BD

```bash
# Tests de configuración (sin conexión real)
pytest tests/unit/test_database_config.py -v

# Tests de validación de URLs
pytest tests/unit/test_url_validation.py -v
```

**Qué prueban:**
- ✅ Formato de URLs de conexión
- ✅ Validación de parámetros
- ✅ Parsing de configuración
- ✅ Funciones auxiliares

### Tests de Integración de BD

```bash
# Tests con base de datos real
pytest tests/integration/test_database.py -v

# Tests específicos de PostgreSQL
pytest tests/integration/test_postgres.py -v

# Tests de migraciones
pytest tests/integration/test_migrations.py -v
```

**Qué prueban:**
- ✅ Conexión real a SQLite
- ✅ Conexión real a PostgreSQL
- ✅ Operaciones CRUD
- ✅ Ejecución de migraciones
- ✅ Pool de conexiones

### Configuración por Base de Datos

#### SQLite (Desarrollo/Testing)
```bash
# Usar BD en memoria para tests unitarios
DATABASE_URL=sqlite:///:memory:

# Usar archivo temporal para tests de integración
DATABASE_URL=sqlite:///./test.db
```

#### PostgreSQL (Staging/Producción)
```bash
# Configurar BD de testing
DATABASE_URL=postgresql://postgres:password@localhost:5432/test_db

# Crear BD de testing
createdb test_db
```

---

## 🧪 Tests de Migraciones

### Verificar Configuración de Alembic

```bash
# Test de configuración
pytest tests/integration/test_migrations.py::TestMigrationsConfiguration -v

# Verificar que Alembic funciona
alembic check
```

### Tests de Ejecución de Migraciones

```bash
# Tests básicos de migración
pytest tests/integration/test_migrations.py::TestMigrationsExecution -v

# Test de ciclo completo
pytest tests/integration/test_migrations.py::TestDatabaseIntegration -v
```

**Qué prueban:**
- ✅ Configuración de `alembic.ini`
- ✅ Configuración de `alembic/env.py`
- ✅ Comandos básicos de Alembic
- ✅ Creación y aplicación de migraciones

---

## 📊 Cobertura de Tests

### Ejecutar Reporte de Cobertura

```bash
# Generar reporte HTML
pytest --cov=app --cov-report=html

# Ver reporte en navegador
open htmlcov/index.html  # Mac
start htmlcov/index.html # Windows
```

### Interpretar Métricas

| Métrica | Bueno | Excelente | Descripción |
|---------|-------|-----------|-------------|
| **Líneas** | > 80% | > 90% | Porcentaje de líneas ejecutadas |
| **Branches** | > 70% | > 85% | Porcentaje de ramas cubiertas |
| **Funciones** | > 85% | > 95% | Porcentaje de funciones probadas |

### Excluir del Reporte

```python
# En el código, excluir líneas específicas
if __name__ == "__main__":  # pragma: no cover
    main()

# En .coveragerc, excluir archivos completos
[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
```

---

## 🚨 Solución de Problemas

### Error: "No tests collected"

```bash
# Verificar estructura de archivos
ls tests/
ls tests/unit/
ls tests/integration/

# Verificar que archivos empiecen con test_
pytest --collect-only

# Verificar configuración
pytest --markers
```

### Error: "Database connection failed"

```bash
# Verificar configuración de BD
python -c "from app.core.settings import settings; print(settings.database_url)"

# Para PostgreSQL, verificar que esté corriendo
pg_isready -h localhost -p 5432

# Para SQLite, verificar permisos
touch test.db && rm test.db
```

### Error: "Import failed"

```bash
# Verificar PYTHONPATH
echo $PYTHONPATH

# Ejecutar desde directorio raíz
cd /ruta/del/proyecto
pytest tests/

# Verificar estructura de módulos
python -c "import app.core.settings"
```

### Tests Lentos

```bash
# Ejecutar solo tests rápidos
pytest -m "not slow" -v

# Usar paralelización (requiere pytest-xdist)
pip install pytest-xdist
pytest -n 4  # 4 procesos paralelos

# Ejecutar tests específicos
pytest tests/unit/test_settings.py::test_specific_function
```

---

## 📋 Buenas Prácticas

### ✅ Hacer

- **Nombrar tests descriptivamente:** `test_user_can_login_with_valid_credentials`
- **Un assert por test:** Enfocarse en una verificación específica
- **Usar fixtures:** Para datos compartidos entre tests
- **Tests independientes:** Cada test debe poder ejecutarse solo
- **Limpiar después:** Usar fixtures para setup/teardown
- **Documentar tests complejos:** Explicar qué verifica el test

### ❌ No hacer

- **Tests dependientes:** Un test no debe depender de otro
- **Datos hardcodeados:** Usar fixtures o factories
- **Tests que modifican estado global:** Usar mocks o BD temporal
- **Tests muy largos:** Dividir en tests más pequeños
- **Ignorar tests fallidos:** Siempre investigar y corregir

---

## 🔄 Flujo de Desarrollo con Tests

### 1. Desarrollo de Nueva Funcionalidad

```bash
# 1. Crear branch
git flow feature start nueva-funcionalidad

# 2. Escribir test unitario primero (TDD)
# Crear tests/unit/test_nueva_funcionalidad.py

# 3. Ejecutar test (debe fallar)
pytest tests/unit/test_nueva_funcionalidad.py -v

# 4. Implementar funcionalidad
# Editar app/...

# 5. Ejecutar test (debe pasar)
pytest tests/unit/test_nueva_funcionalidad.py -v

# 6. Agregar tests de integración si necesario
# Crear tests/integration/test_nueva_funcionalidad.py

# 7. Ejecutar todos los tests
pytest -v

# 8. Verificar cobertura
pytest --cov=app --cov-report=term-missing
```

### 2. Antes de Hacer Commit

```bash
# Ejecutar tests rápidos
pytest tests/unit/ -v

# Verificar que no hay regresiones
pytest tests/integration/ -v

# Verificar cobertura mínima
pytest --cov=app --cov-fail-under=80
```

### 3. Antes de Pull Request

```bash
# Ejecutar suite completa
pytest -v

# Generar reporte de cobertura
pytest --cov=app --cov-report=html

# Verificar tests lentos
pytest -m slow -v
```

---

## 📚 Referencias Adicionales

- [Documentación de pytest](https://docs.pytest.org/)
- [Guía de Testing con FastAPI](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)
- [Alembic Testing](https://alembic.sqlalchemy.org/en/latest/cookbook.html#test-current-database-revision-is-at-head-s)

---