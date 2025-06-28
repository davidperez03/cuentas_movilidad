# 🗄️ Configuración de Migraciones - Alembic

---

## 📁 Estructura de Archivos

```
proyecto/
├── alembic/
│   ├── versions/          ← Migraciones generadas
│   └── env.py            ← Configuración de conexión
├── alembic.ini           ← Configuración principal
├── app/core/settings.py  ← Variables de BD
└── .env                  ← URL de base de datos
```

---

## ⚙️ Configuración Inicial

### 1. Inicializar Alembic
```bash
alembic init alembic
```

### 2. Configurar `app/core/settings.py`
```python
class Settings(BaseSettings):
    # ... otras configuraciones ...
    
    # Base de datos
    database_url: str = "sqlite:///./app.db"
```

### 3. Configurar `.env`
```env
DATABASE_URL=sqlite:///./app.db
# O para PostgreSQL:
# DATABASE_URL=postgresql://usuario:password@localhost:5432/base_datos
```

### 4. Actualizar `alembic/env.py`
```python
# Agregar estas líneas al inicio:
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.settings import settings

# Y esta función:
def get_url():
    return settings.database_url
```

---

## 🧪 Verificar Configuración

```bash
# 1. Verificar que settings funciona
python -c "from app.core.settings import settings; print(settings.database_url)"

# 2. Verificar Alembic
alembic check
```

---

## 🔄 Cambio de Base de Datos

### SQLite (desarrollo):
```env
DATABASE_URL=sqlite:///./app.db
```

### PostgreSQL (producción):
```env
DATABASE_URL=postgresql://usuario:password@localhost:5432/base_datos
```

---

## 📋 Archivos Importantes

| Archivo | Propósito |
|---------|-----------|
| `alembic.ini` | Configuración general |
| `alembic/env.py` | Conexión a BD |
| `app/core/settings.py` | Variables de entorno |
| `.env` | URL de base de datos |
| `alembic/versions/` | Archivos de migración |