# 🐍 Entornos Virtuales - venv y virtualenv

---

## 🎯 Método 1: venv (Recomendado)

### ✅ Prerrequisitos
- Python 3.3+ (incluido por defecto)

### 🚀 Configuración

#### Crear entorno:
```bash
python -m venv .venv
```

#### Activar entorno:
```bash
# Windows:
.venv\Scripts\activate

# Linux/macOS:
source .venv/bin/activate
```

#### Instalar dependencias:
```bash
pip install -r requirements.txt
```

#### Desactivar:
```bash
deactivate
```

---

## 🛠️ Método 2: virtualenv (Alternativo)

### 📦 Instalación:
```bash
pip install virtualenv
```

### 🚀 Configuración

#### Crear entorno:
```bash
virtualenv .venv
```

#### Activar entorno:
```bash
# Windows:
.venv\Scripts\activate

# Linux/macOS:
source .venv/bin/activate
```

#### Instalar dependencias:
```bash
pip install -r requirements.txt
```

#### Desactivar:
```bash
deactivate
```

---

## 🔧 Comandos Útiles

| Comando | Descripción |
|---------|-------------|
| `pip list` | Ver paquetes instalados |
| `pip freeze > requirements.txt` | Generar requirements.txt |
| `rm -rf .venv` | Eliminar entorno (Linux/macOS) |
| `rmdir /s .venv` | Eliminar entorno (Windows) |

---

## ⚡ Flujo Rápido

```bash
# 1. Crear y activar
python -m venv .venv
source .venv/bin/activate  # o .venv\Scripts\activate en Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Trabajar en el proyecto
# ...

# 4. Desactivar al terminar
deactivate
```