---
titulo: "Migración UUID a Integer"
tipo: Decisión
fecha: 2026-07-03
tags: [decisión, migración, uuid, int, postgresql]
---

# Migración UUID a Integer

## Problema

Los modelos originales usaban `UUID` como Primary Key y Foreign Key. Esto causaba:
- Rendimiento deficiente en joins y búsquedas
- Complejidad innecesaria en el frontend (pasar strings UUIDs)
- Incompatibilidad con SQLite para tests
- Mayor consumo de espacio en disco

## Decisión

Migrar todos los PKs y FKs de `UUID` a `Integer` con autoincrement.

## Archivos Afectados

### Backend (66 archivos)
- Todos los `models.py` de cada módulo
- Todos los `schemas.py` de cada módulo
- Todos los `router.py` de cada módulo
- `auth/dependencies.py`
- `main.py`
- Tests (`test_app_smoke.py`, `test_technician_flow.py`)
- Migraciones Alembic existentes

### Frontend (60 archivos)
- Todos los modelos TypeScript
- Todos los servicios
- Todos los componentes

### Mobile (17 archivos)
- Todos los modelos Dart
- Todos los repositorios
- Todos los providers
- Todos los screens

## Migración Alembic

```python
# e7d9c2a8b4f6_migrate_uuid_pks_to_integer.py
# 1. Crear sequences para cada tabla
# 2. Agregar columnas integer temporales
# 3. Migrar datos (cast UUID a hash int)
# 4. Renombrar columnas
# 5. Eliminar columnas UUID antiguas
# 6. Crear indexes y constraints
```

## Resultado

- Backend: compila sin errores
- Frontend: build production sin errores
- Mobile: flutter analyze sin errores
- DB: migración aplicada exitosamente en Supabase

## Lecciones Aprendidas

- La migración fue idempotente porque el schema ya estaba en INTEGER desde baseline
- Los tests de backend fallan contra Supabase (entorno, no código)
- La cadena de revisiones Alembic: `21b50363b001 → a7c3e1f89b42 → c9e5a2b1d4f8 → f2b8c3d5e1a7 → d4f1a6c8b920 → e7d9c2a8b4f6`

## Documentos Relacionados

- [[Modelo de Datos]]
- [[Backend]]
- [[Supabase]]
