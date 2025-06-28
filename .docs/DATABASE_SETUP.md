# 🗄️ Configuración de Base de Datos

Esta guía te ayudará a configurar correctamente el sistema de base de datos con soporte para **SQLite** (desarrollo) y **PostgreSQL** (producción).

---

## 📋 Tabla de Contenidos

1. [Resumen de Configuración](#resumen-de-configuración)
2. [Configuración para Desarrollo (SQLite)](#configuración-para-desarrollo-sqlite)
3. [Configuración para Producción (PostgreSQL)](#configuración-para-producción-postgresql)
4. [Variables de Entorno](#variables-de-entorno)
5. [Verificación de Configuración](#verificación-de-configuración)
6. [Solución de Problemas](#solución-de-problemas)
7. [Comandos Útiles](#comandos-útiles)

---

## 🎯 Resumen de Configuración

El sistema cambia automáticamente entre bases de datos según el entorno:

| Entorno | Base de Datos | Configuración |
|---------|---------------|---------------|
| **Desarrollo** | SQLite | `DEBUG=True` |
| **Producción** | PostgreSQL | `DEBUG=False` |

## 📁 Estructura de Archivos

```
tu-proyecto/
├── .env                    ← Configuración
├── database.sqlite         ← SQLite (desarrollo)
├── app/
│   ├── main.py            ← Aplicación principal
│   └── core/
│       ├── db.py    ← Configuración BD
│       └── settings.py    ← Variables entorno
└── requirements.txt
```

---

## 🛠️ Configuración para Desarrollo (SQLite)

### ✅ Prerrequisitos
- Python 3.9+
- SQLite (incluido con Python)

### 🚀 Configuración Rápida

#### 1. Configurar variables de entorno:
```env
# .env
DEBUG=True
APP_NAME=Sistema de Gestión de Cuentas
SECRET_KEY=tu_clave_secreta_muy_segura
ALGORITHM=HS256
APP_BASE_URL=http://localhost:8000
```

#### 2. Instalar dependencias:
```bash
pip install sqlalchemy
```

#### 3. Ejecutar la aplicación:
```bash
python -m app.main
```

#### 4. Verificar:
- **Consola**: Debería mostrar `🔗 Configurando SQLite para desarrollo`
- **Endpoint**: http://localhost:8000/salud → `"type": "SQLite"`
- **Archivo**: Se crea `database.sqlite` en el directorio raíz

---

## 🐘 Configuración para Producción (PostgreSQL)

### ✅ Prerrequisitos
- PostgreSQL 13+ instalado y corriendo
- Driver psycopg2

### 🚀 Opción 1: Instalación con Docker (Recomendado)

#### 1. Ejecutar PostgreSQL:
```bash
# Crear y ejecutar contenedor PostgreSQL
docker run --name postgres-prod \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=mi_password_seguro \
  -e POSTGRES_DB=sistema_cuentas \
  -p 5432:5432 \
  -d postgres:13

# Verificar que está corriendo
docker ps
```

#### 2. Instalar dependencias:
```bash
pip install psycopg2-binary
```

#### 3. Configurar variables de entorno:
```env
# .env
DEBUG=False
APP_NAME=Sistema de Gestión de Cuentas
SECRET_KEY=tu_clave_secreta_muy_segura_para_produccion
ALGORITHM=HS256
APP_BASE_URL=https://tu-dominio.com

# Configuración PostgreSQL
POSTGRES_SERVER=localhost
POSTGRES_USER=admin
POSTGRES_PASSWORD=mi_password_seguro
POSTGRES_DB=sistema_cuentas
POSTGRES_PORT=5432
```

### 🚀 Opción 2: Instalación Local

#### Ubuntu/Debian:
```bash
# Instalar PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Crear base de datos
sudo -u postgres createdb sistema_cuentas
sudo -u postgres createuser admin
sudo -u postgres psql -c "ALTER USER admin PASSWORD 'mi_password_seguro';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE sistema_cuentas TO admin;"
```

#### Windows:
1. Descargar PostgreSQL desde [postgresql.org](https://www.postgresql.org/download/windows/)
2. Instalar siguiendo el asistente
3. Crear base de datos usando pgAdmin o línea de comandos

#### macOS:
```bash
# Con Homebrew
brew install postgresql
brew services start postgresql

# Crear base de datos
createdb sistema_cuentas
createuser admin
psql -c "ALTER USER admin PASSWORD 'mi_password_seguro';"
```

---

## ⚙️ Variables de Entorno

### 📝 Archivo `.env` Completo

```env
# =====================================
# CONFIGURACIÓN BÁSICA
# =====================================
APP_NAME=Sistema de Gestión de Cuentas
DEBUG=True  # False para producción
SECRET_KEY=tu_clave_secreta_muy_segura_cambiala_en_produccion
ALGORITHM=HS256
APP_BASE_URL=http://localhost:8000

# =====================================
# CONFIGURACIÓN DE BASE DE DATOS
# =====================================

# Opción 1: URL completa (opcional)
# DATABASE_URL=sqlite:///./database.sqlite  # Desarrollo
# DATABASE_URL=postgresql://admin:password@localhost:5432/sistema_cuentas  # Producción

# Opción 2: Configuración por partes (recomendado)
POSTGRES_SERVER=localhost
POSTGRES_USER=admin
POSTGRES_PASSWORD=mi_password_seguro
POSTGRES_DB=sistema_cuentas
POSTGRES_PORT=5432

# =====================================
# OTRAS CONFIGURACIONES
# =====================================
TIMEZONE=America/Bogota
```

### 🔐 Variables Obligatorias

| Variable | Desarrollo | Producción | Descripción |
|----------|------------|------------|-------------|
| `DEBUG` | `True` | `False` | Modo de depuración |
| `SECRET_KEY` | Cualquiera | **Muy segura** | Clave para tokens |
| `APP_NAME` | ✅ | ✅ | Nombre de la aplicación |
| `POSTGRES_*` | Opcional | **Obligatorio** | Configuración PostgreSQL |

---

## ✅ Verificación de Configuración

### 1. **Verificar Conexión a Base de Datos**
```bash
# Ejecutar la aplicación
python -m app.main

# En la consola deberías ver:
# 🔗 Configurando SQLite para desarrollo  (si DEBUG=True)
# 🔗 Configurando PostgreSQL para producción  (si DEBUG=False)
# ✅ Motor [SQLite/PostgreSQL] configurado
```

### 2. **Health Check via API**
```bash
# Verificar endpoint de salud
curl http://localhost:8000/salud

# Respuesta esperada:
{
  "status": "ok",
  "database": {
    "status": "healthy",
    "type": "SQLite",  # o "PostgreSQL"
    "message": "Base de datos conectada correctamente"
  }
}
```

### 3. **Información Detallada (Solo Desarrollo)**
```bash
# Solo disponible cuando DEBUG=True
curl http://localhost:8000/info

# Muestra configuración completa del sistema
```

### 4. **Verificar Archivos Creados**

#### SQLite (Desarrollo):
```bash
# Verificar que se creó el archivo
ls -la database.sqlite

# Ver tablas (si tienes sqlite3 instalado)
sqlite3 database.sqlite ".tables"
```

#### PostgreSQL (Producción):
```bash
# Conectar a la base de datos
psql -h localhost -U admin -d sistema_cuentas

# Ver tablas
\dt

# Salir
\q
```

---

## 🐛 Solución de Problemas

### ❌ Error: "No module named 'psycopg2'"
```bash
# Solución:
pip install psycopg2-binary
```

### ❌ Error: "connection to server... failed"
```bash
# Verificar que PostgreSQL está corriendo
# Docker:
docker ps
docker logs postgres-prod

# Local:
sudo systemctl status postgresql  # Linux
brew services list | grep postgres  # macOS
```

### ❌ Error: "database 'sistema_cuentas' does not exist"
```bash
# Crear la base de datos
createdb sistema_cuentas

# O con Docker:
docker exec -it postgres-prod createdb -U admin sistema_cuentas
```

### ❌ Error: "SQLite database is locked"
```bash
# El archivo SQLite está siendo usado por otro proceso
# Detener todas las instancias de la aplicación y reiniciar
```

### ❌ La aplicación no cambia de SQLite a PostgreSQL
1. **Verificar el archivo .env:**
   ```bash
   cat .env | grep DEBUG
   # Debe mostrar: DEBUG=False
   ```

2. **Reiniciar completamente la aplicación:**
   ```bash
   # Detener con Ctrl+C
   # Volver a ejecutar
   python -m app.main
   ```

3. **Verificar en los logs de consola que diga PostgreSQL**

---

## 🔧 Comandos Útiles

### Desarrollo (SQLite)
```bash
# Cambiar a modo desarrollo
echo "DEBUG=True" >> .env

# Ver contenido de la base de datos
sqlite3 database.sqlite
.tables
.schema
.quit

# Eliminar base de datos para empezar limpio
rm database.sqlite
```

### Producción (PostgreSQL)
```bash
# Cambiar a modo producción
echo "DEBUG=False" >> .env

# Conectar a PostgreSQL
psql -h localhost -U admin -d sistema_cuentas

# Backup de base de datos
pg_dump -h localhost -U admin sistema_cuentas > backup.sql

# Restaurar backup
psql -h localhost -U admin sistema_cuentas < backup.sql

# Ver conexiones activas
psql -h localhost -U admin -d sistema_cuentas -c "SELECT * FROM pg_stat_activity;"
```

### Docker (PostgreSQL)
```bash
# Detener contenedor
docker stop postgres-prod

# Iniciar contenedor existente
docker start postgres-prod

# Ver logs
docker logs postgres-prod

# Ejecutar comandos en el contenedor
docker exec -it postgres-prod psql -U admin -d sistema_cuentas

# Eliminar contenedor (⚠️ elimina todos los datos)
docker rm -f postgres-prod
```

### Migración entre Entornos
```bash
# 1. Exportar datos de SQLite
sqlite3 database.sqlite ".dump" > export.sql

# 2. Limpiar el archivo para PostgreSQL (manual)
# Editar export.sql para compatibilidad

# 3. Importar a PostgreSQL
psql -h localhost -U admin -d sistema_cuentas < export_cleaned.sql
```

---

## 🔍 Logs y Monitoreo

### Verificar Logs de la Aplicación
```bash
# La aplicación muestra logs informativos:
INFO:app.core.database:🔗 Configurando SQLite para desarrollo
INFO:app.core.database:✅ Motor SQLite configurado con optimizaciones
INFO:__main__:🚀 Iniciando Sistema de Gestión de Cuentas
```

### Verificar Performance
```bash
# Para SQLite - verificar tamaño del archivo
ls -lh database.sqlite

# Para PostgreSQL - verificar conexiones
psql -h localhost -U admin -d sistema_cuentas -c "SELECT count(*) FROM pg_stat_activity;"
```

---

## 🎯 Próximos Pasos

Una vez que tengas la base de datos configurada:

1. **Crear modelos de datos** (tablas)
2. **Configurar Alembic** para migraciones
3. **Configurar tests** con base de datos de prueba

---
