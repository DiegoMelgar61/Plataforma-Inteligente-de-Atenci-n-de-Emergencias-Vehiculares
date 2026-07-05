---
titulo: "Arquitectura Modular"
tipo: Decisión
fecha: 2026-07-03
tags: [decisión, arquitectura, modular, refactor]
---

# Arquitectura Modular

## Problema

El código original estaba en una estructura plana:
```
app/presentation/api/v1/routers/  ← Todos los routers juntos
app/presentation/api/v1/schemas/  ← Todos los schemas juntos
app/models/models.py              ← Todos los modelos juntos
```

## Decisión

Reorganizar en módulos autónomos:
```
app/modules/{nombre}/
├── models.py
├── schemas.py
├── router.py
├── service.py
└── dependencies.py
```

## Beneficios

1. **Encapsulación**: Cada módulo es autocontenido
2. **Escalabilidad**: Fácil agregar nuevos módulos
3. **Mantenibilidad**: Cambios en un módulo no afectan otros
4. **Testing**: Tests específicos por módulo
5. **Documentación**: Cada módulo documenta su dominio

## Migración

- `app/presentation/api/v1/routers/incidents.py` → `app/modules/incidents/router.py`
- `app/presentation/api/v1/schemas/incident.py` → `app/modules/incidents/schemas.py`
- `app/models/models.py` → distribuido en cada módulo

## Documentos Relacionados

- [[Backend]]
- [[Visión General]]
