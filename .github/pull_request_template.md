# 🏛️ Pull Request

## 📝 ¿Qué hace este PR?
<!-- Describe en 2-3 líneas qué cambia y por qué -->

**Resuelve:** #(número-issue)

## 🔧 Tipo de cambio
- [ ] `feat:` Nueva funcionalidad
- [ ] `fix:` Corrección de errores
- [ ] `refactor:` Mejora interna sin cambiar comportamiento
- [ ] `chore:` Cambios menores (scripts, config, etc.)
- [ ] `docs:` Documentación
- [ ] `style:` Estilo (formato, espacios, etc.)
- [ ] `test:` Agregado o cambios a pruebas
- [ ] `perf:` Mejora de rendimiento
- [ ] `build:` Sistema de compilación, dependencias, docker

## 🌿 Git Flow
**Tipo de rama:**
- [ ] `feature/*` - Nueva funcionalidad
- [ ] `bugfix/*` - Corrección menor
- [ ] `hotfix/*` - Corrección urgente en producción
- [ ] `release/*` - Preparación de nueva versión

**Flujo:** `[rama-origen]` → `develop` (o `main` para hotfix)

## 🧪 ¿Cómo probarlo?
1. 
2. 
3. 

**Comando de pruebas:** 
```bash
# Pruebas completas
python -m pytest tests/

# Por tipo específico
python -m pytest tests/test_auth.py -v
```

## ✅ Checklist (basado en contributing.md)
- [ ] El código funciona correctamente
- [ ] Las pruebas pasan completamente
- [ ] Commits siguen convenciones semánticas
- [ ] Finalicé la rama con git-flow (`git flow feature finish`)
- [ ] Sin código comentado o prints de debug
- [ ] Documenté cambios importantes

## 📋 Para el reviewer
<!-- Lo que debe verificar quien revisa -->
- **Enfocarse en:** [área específica]
- **Probado en:** [entorno/navegador]

## 💬 Notas adicionales
<!-- Información extra, decisiones técnicas, TODOs futuros -->
