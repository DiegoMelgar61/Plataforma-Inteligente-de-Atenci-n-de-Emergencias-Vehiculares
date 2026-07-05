---
titulo: "Supabase"
tipo: Infraestructura
fecha: 2026-07-03
tags: [supabase, postgresql, hosting, db]
---

# Supabase

## Qué es

Supabase es una plataforma de hosting para PostgreSQL con features extra:
- PostgreSQL + PostGIS gestionado
- Dashboard web para administra la DB
- Auth (no lo usamos, usamos JWT propio)
- Storage (no lo usamos, usamos StaticFiles)
- Realtime (no lo usamos, usamos WebSockets propios)

## Conexión

```python
# backend/app/core/database.py
DATABASE_URL = "postgresql://user:password@host:5432/dbname"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

## Migraciones

```bash
# Aplicar migraciones
alembic upgrade head

# Crear nueva migración
alembic revision --autogenerate -m "descripcion"
```

## Cadena de Revisiones

```
21b50363b001 (baseline)
    ↓
a7c3e1f89b42 (add_tecnico_role)
    ↓
c9e5a2b1d4f8 (add_tenant)
    ↓
f2b8c3d5e1a7 (add_analisis_ia)
    ↓
d4f1a6c8b920 (add_bitacora)
    ↓
e7d9c2a8b4f6 (migrate_uuid_to_integer)
```

## Documentos Relacionados

- [[Docker]]
- [[Environment Variables]]
- [[Migración UUID→int]]
