# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
```bash
# Development mode with auto-reload
uvicorn app.main:app --reload

# Production mode
python -m app.main

# Alternative using module syntax
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Testing
```bash
# Run all tests with coverage
pytest

# Run specific test categories
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
pytest -m database       # Database-related tests
pytest -m postgres       # PostgreSQL-specific tests

# Run single test file
pytest tests/unit/cuentas/domain/value_objects/test_placa.py

# Generate coverage report
pytest --cov=app --cov-report=html
```

### Database Management
```bash
# Generate new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Check migration status
alembic current

# Rollback migration
alembic downgrade -1
```

## Architecture Overview

### Domain-Driven Design Structure
The application follows DDD principles with clear separation of concerns:

- **Domain Layer**: `app/cuentas/domain/` - Contains business logic, value objects, and enums
- **Core Layer**: `app/core/` - Application settings and database configuration
- **Value Objects**: Encapsulate business rules and validation (e.g., `Placa`, `NumeroCuenta`, `FechaTramite`)
- **Enums**: Define business states and types with validation logic

### Database Configuration
The application uses a dual-database approach:
- **Development**: SQLite (`database.sqlite`) when `DEBUG=True`
- **Production**: PostgreSQL when `DEBUG=False`

Database connection is automatically determined by environment settings and managed through `app/core/db.py`.

### Value Objects Pattern
Value objects are immutable and contain validation logic:
- Located in `app/cuentas/domain/value_objects/`
- Each value object validates its data on creation
- Enums include business logic for state transitions and validation
- Examples: `Placa` (vehicle license plates), `NumeroCuenta` (account numbers), date objects

### Testing Strategy
Tests are organized by type and location:
- **Unit tests**: `tests/unit/` - Test individual components in isolation
- **Integration tests**: `tests/integration/` - Test component interactions
- **Database tests**: Test database connectivity and queries
- **Value object tests**: Comprehensive validation testing

Test markers are defined in `pytest.ini` for selective test execution.

### Environment Configuration
Settings are managed through `app/core/settings.py` using Pydantic:
- Environment variables loaded from `.env` file
- Automatic database URL construction for PostgreSQL
- Debug mode controls API documentation availability
- Colombia timezone (`America/Bogota`) as default

### FastAPI Application Structure
- Main application in `app/main.py`
- Health check endpoint at `/salud`
- Development info endpoint at `/info` (debug mode only)
- API documentation at `/docs` (debug mode only)
- Structured logging with lifecycle management

## Key Conventions

### Code Style
- Spanish naming for domain concepts reflecting business language
- Enum values in lowercase with underscores
- Clear separation between domain and infrastructure concerns
- Comprehensive error handling with appropriate HTTP status codes

### Git Workflow
- Main branch: `main` (production)
- Development branch: `develop` 
- Feature branches: `feature/*`
- Hotfix branches: `hotfix/*`
- Release branches: `release/*`

### Database Migrations
- Use descriptive migration messages
- Always review auto-generated migrations before applying
- Test migrations in development environment first
- Database schema changes require corresponding model updates