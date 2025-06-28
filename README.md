# 🏛️ Sistema de Gestión de Cuentas

> Sistema web para la gestión y seguimiento de traslados y radicación de cuentas administrativas

---

## 📋 Descripción

Este sistema permite gestionar de manera eficiente los procesos administrativos relacionados con el manejo de cuentas, proporcionando una solución integral para:

- **Traslados entre organismos** con seguimiento completo del flujo
- **Radicación de cuentas** con control automático de vencimientos  
- **Gestión de estados** en tiempo real para cada proceso
- **Trazabilidad completa** de todas las operaciones realizadas

---

## ⚡ Funcionalidades Principales

| Característica | Descripción |
|---------------|-------------|
| 🔍 **Búsqueda Avanzada** | Sistema de filtros por fecha, placa, destino/origen y estado |
| 📤 **Exportación** | Descarga de datos en múltiples formatos (PDF, Excel, CSV) |
| 📱 **Interfaz Responsive** | Diseño adaptable para escritorio, tablet y móvil |
| 🔒 **Control de Acceso** | Autenticación por roles y permisos de usuario |
| 📊 **Dashboard** | Panel de control con métricas y estadísticas en tiempo real |
| 🔔 **Notificaciones** | Alertas automáticas para fechas de vencimiento |

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología | Versión |
|-----------|------------|---------|
| **Backend** | FastAPI | 0.104+ |
| **Base de Datos** | PostgreSQL | 13+ |
| **Templates** | Jinja2 | 3.1+ |
| **Frontend** | Bootstrap | 5.3 |
| **ORM** | SQLAlchemy | 2.0+ |
| **Migraciones** | Alembic | 1.12+ |

---

## 🚀 Instalación Rápida

### Prerrequisitos
- Python 3.9+
- Git

### Pasos de Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/davidperez03/sistema-movilidad.git
cd sistema-movilidad

# 2. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 3. Instalar dependencias  
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# 5. Ejecutar la aplicación
python -m app.main

# 6. Abrir en el navegador
# http://localhost:8000/docs
```

### Comandos Útiles

```bash
# Ejecutar tests
pytest

# Ejecutar con recarga automática
uvicorn app.main:app --reload

# Ver cobertura de tests
pytest --cov=app --cov-report=html
```

---

## 🔄 Git Flow

Este proyecto sigue el modelo [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/) para un desarrollo organizado:

### Ramas Principales
- **`main`** - Código en producción
- **`develop`** - Rama de desarrollo principal

### Ramas de Soporte
- **`feature/*`** - Nuevas funcionalidades
- **`hotfix/*`** - Correcciones urgentes
- **`release/*`** - Preparación de versiones

### Comandos Útiles
```bash
# Inicializar Git Flow
git flow init

# Nueva funcionalidad
git flow feature start nueva-funcionalidad
git flow feature finish nueva-funcionalidad

# Hotfix
git flow hotfix start fix-critico
git flow hotfix finish fix-critico
```

📖 [Ver guía completa de contribución](.docs/contributing.md)

---

## 🐍 Entornos Virtuales

Para aislar las dependencias del proyecto y evitar conflictos con otros proyectos Python.

📖 [Ver documentación completa de entornos virtuales](.docs/VIRTUAL_ENVIRONMENTS.md)

---

## 🗄️ Configuración de Base de Datos

Ver la [Guía Completa de Configuración de BD](.docs/DATABASE_SETUP.md) para instrucciones detalladas.

### Setup Rápido:
- **Desarrollo**: `DEBUG=True` → SQLite automático
- **Producción**: `DEBUG=False` → PostgreSQL requerido

---

📖 [Ver documentación completa de migraciones](docs/MIGRATIONS.md)

---

## 📚 Documentación

- [🐍 Configuración de Entornos Virtuales](.docs/VIRTUAL_ENVIRONMENTS.md)
- [🤝 Guía de Contribución](.docs/contributing.md)
- [Guía Completa de Configuración de BD](.docs/DATABASE_SETUP.md)
- [Configuración de Migraciones](.docs/MIGRACIONES.md)

---

## 📝 Licencia

Este proyecto está bajo la licencia Apache 2.0. Ver el archivo [LICENSE](LICENSE) para más detalles.

---

## 👤 Autor

**David Pérez Rodríguez**
- GitHub: [@davidperez03](https://github.com/davidperez03)