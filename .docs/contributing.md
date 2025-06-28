# 🤝 Guía de contribución – Proyecto FastAPI

Gracias por tu interés en contribuir al proyecto. Esta guía te ayudará a seguir el flujo correcto de trabajo para mantener un desarrollo limpio, colaborativo y escalable.

---

## 🧬 Flujo de ramas: Git Flow

Este proyecto sigue la estrategia [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/) para gestionar versiones y desarrollo colaborativo.

### 📚 Ramas principales

| Rama           | Propósito                                 |
|----------------|-------------------------------------------|
| `main`         | Código en producción estable              |
| `develop`      | Integración de funcionalidades            |
| `feature/*`    | Nuevas funcionalidades                    |
| `release/*`    | Preparación de nuevas versiones           |
| `hotfix/*`     | Correcciones urgentes en producción       |
| `bugfix/*`     | Correcciones menores                      |

---

## ✍️ Convenciones de commits semánticos

Todos los commits deben seguir esta estructura:

```bash
<tipo>[alcance opcional]: <descripción corta>
```

Ejemplos:

```bash
feat(api): agregar endpoint de autenticación JWT
fix(ui): corregir validación del formulario de registro
```

### Tipos permitidos

| Tipo       | Descripción                                         |
|------------|-----------------------------------------------------|
| `feat:`    | Nueva funcionalidad                                  |
| `fix:`     | Corrección de errores                                |
| `refactor:`| Mejora interna sin cambiar comportamiento funcional |
| `chore:`   | Cambios menores (scripts, config, etc.)              |
| `docs:`    | Documentación                                        |
| `style:`   | Estilo (formato, espacios, etc.)                     |
| `test:`    | Agregado o cambios a pruebas                         |
| `perf:`    | Mejora de rendimiento                                |
| `build:`   | Sistema de compilación, dependencias, docker, etc.  |

---

## 🚀 Flujos de trabajo completos

### 1. 🆕 Nueva funcionalidad (Feature)

```bash
# 1. Asegurarse de estar en develop actualizada
git checkout develop
git pull origin develop

# 2. Crear rama de funcionalidad
git flow feature start nombre-funcionalidad

# 3. Desarrollar la funcionalidad
# Hacer cambios en el código...

# 4. Commits semánticos frecuentes
git add .
git commit -m "feat(auth): implementar middleware de autenticación"
git add .
git commit -m "test(auth): agregar pruebas unitarias para middleware"
git add .
git commit -m "docs(auth): documentar endpoints de autenticación"

# 5. Ejecutar pruebas antes de finalizar
python -m pytest tests/
python -m pytest tests/test_auth.py -v

# 6. Finalizar funcionalidad (mergea a develop)
git flow feature finish nombre-funcionalidad

# 7. Subir cambios
git push origin develop
```

### 2. 🐛 Corrección de bug menor (Bugfix)

```bash
# 1. Desde develop actualizada
git checkout develop
git pull origin develop

# 2. Crear rama de bugfix
git flow bugfix start fix-validacion-email

# 3. Corregir el bug
# Hacer cambios necesarios...

# 4. Commit del fix
git add .
git commit -m "fix(validation): corregir regex de validación de email"

# 5. Agregar test para el fix
git add .
git commit -m "test(validation): agregar casos de prueba para email"

# 6. Ejecutar pruebas
python -m pytest tests/test_validation.py -v

# 7. Finalizar bugfix
git flow bugfix finish fix-validacion-email

# 8. Subir cambios
git push origin develop
```

### 3. 🚨 Hotfix en producción

```bash
# 1. Desde main actualizada
git checkout main
git pull origin main

# 2. Crear hotfix
git flow hotfix start fix-security-1.2.1

# 3. Aplicar la corrección crítica
# Hacer cambios urgentes...

# 4. Commit del hotfix
git add .
git commit -m "fix(security): patchear vulnerabilidad de SQL injection"

# 5. Pruebas críticas
python -m pytest tests/test_security.py -v

# 6. Finalizar hotfix (mergea a main y develop)
git flow hotfix finish fix-security-1.2.1

# 7. Subir todos los cambios
git push origin main
git push origin develop
git push origin --tags
```

### 4. 🎯 Nueva versión (Release)

```bash
# 1. Desde develop actualizada
git checkout develop
git pull origin develop

# 2. Crear rama de release
git flow release start 1.3.0

# 3. Preparar la release
# Actualizar version en pyproject.toml o setup.py
# Actualizar CHANGELOG.md
# Ejecutar todas las pruebas

# 4. Commits de preparación
git add .
git commit -m "chore(release): bump version to 1.3.0"
git add .
git commit -m "docs(changelog): actualizar changelog para v1.3.0"

# 5. Pruebas completas
python -m pytest tests/ -v
python -m pytest tests/ --cov=app --cov-report=html

# 6. Finalizar release (mergea a main y develop)
git flow release finish 1.3.0

# 7. Subir todos los cambios y tags
git push origin main
git push origin develop
git push origin --tags
```

---

## 🔧 Configuración inicial del proyecto

### Instalación de git-flow

```bash
# Ubuntu/Debian
sudo apt-get install git-flow

# macOS
brew install git-flow-avh

# Windows (con Git Bash)
wget -q -O - --no-check-certificate https://raw.githubusercontent.com/petervanderdoes/gitflow-avh/develop/contrib/gitflow-installer.sh install stable | bash
```

### Configuración del repositorio

```bash
# Clonar el repositorio
https://github.com/davidperez03/sistema-movilidad.git
cd sistemas-movilidad

# Inicializar git-flow
git flow init

# Configurar con estos valores:
# Branch name for production releases: main
# Branch name for "next release" development: develop
# Feature branches? [feature/]
# Bugfix branches? [bugfix/]
# Release branches? [release/]
# Hotfix branches? [hotfix/]
# Support branches? [support/]
# Version tag prefix? [v]
```

### Configuración del entorno de desarrollo

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

```

---

## 🛠 Ejemplos por rama y commit

| Rama                         | Commit recomendado                                 |
|------------------------------|----------------------------------------------------|
| `feature/login-jwt`          | `feat(auth): implementar login por JWT`           |
| `feature/user-crud`          | `feat(users): agregar CRUD completo de usuarios`  |
| `bugfix/estilo-footer`       | `style(ui): corregir márgenes en footer`          |
| `bugfix/validation-error`    | `fix(validation): manejar errores de pydantic`    |
| `hotfix/token-expirado`      | `fix(auth): manejar expiración de token correctamente` |
| `release/1.2.0`              | `chore(release): preparar versión 1.2.0`          |

---

## 📋 Checklist antes de hacer commits

### ✅ Para Features
- [ ] Código implementado y funcionando
- [ ] Documentación actualizada (docstrings, README)
- [ ] No hay código comentado o debug prints
- [ ] Commit message sigue convenciones semánticas

### ✅ Para Bugfix/Hotfix
- [ ] Bug reproducido y identificado
- [ ] Fix implementado
- [ ] Test de regresión agregado
- [ ] Pruebas existentes siguen pasando
- [ ] Documentación actualizada si es necesario

### ✅ Para Release
- [ ] Todas las features planeadas están completas
- [ ] Todas las pruebas pasan
- [ ] CHANGELOG.md actualizado
- [ ] Versión bumpeada en archivos correspondientes
- [ ] Documentación de API actualizada
- [ ] Migraciones de BD preparadas (si aplica)

---

## 🔍 Comandos útiles para desarrollo

```bash
# Ver estado de ramas git-flow
git flow

# Ver todas las ramas
git branch -a

# Ver commits de una rama
git log --oneline --graph

```

---

## 🚫 Qué NO hacer

- ❌ No hacer commits directamente en `main` o `develop`
- ❌ No usar `git merge` manualmente entre ramas principales
- ❌ No hacer push --force en ramas compartidas
- ❌ No dejar ramas feature sin finalizar por mucho tiempo
- ❌ No hacer commits con mensajes vagos como "fix", "update"

---

## 🎯 Flujo colaborativo en equipo

### Para desarrolladores

```bash
# Mantener develop actualizada
git checkout develop
git pull origin develop

# Antes de crear nueva feature
git flow feature start mi-feature

# Sincronizar frecuentemente con develop
git checkout develop
git pull origin develop
git checkout feature/mi-feature
git merge develop

# Al finalizar
git flow feature finish mi-feature
git push origin develop
```
---

## 🔗 Recursos adicionales

- [Git Flow – modelo oficial](https://nvie.com/posts/a-successful-git-branching-model/)
- [Convenciones de commits](https://www.conventionalcommits.org/)
- [FastAPI - Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Git Flow Cheatsheet](https://danielkummer.github.io/git-flow-cheatsheet/)

---

*Esta guía está adaptada para proyectos profesionales con FastAPI, Docker y despliegue continuo. Mantener esta estructura permite escalar el código y el equipo sin perder control.*