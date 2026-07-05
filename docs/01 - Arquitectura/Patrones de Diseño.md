---
titulo: "Patrones de Diseño"
tipo: Arquitectura
fecha: 2026-07-03
tags: [patrones, diseño, solid, clean]
---

# Patrones de Diseño

## Backend: Arquitectura Modular

Cada módulo es autónomo con sus modelos, esquemas, router y servicio. No hay dependencias circulares entre módulos.

```
modules/auth → modules/users (solo para queries)
modules/incidents → modules/assignments (solo para estados)
modules/payments → modules/incidents ( FK )
```

**Patrón**: Cada módulo expone su router, que se registra en `main.py`.

## Backend: Dependency Injection (FastAPI)

```python
@router.get("/me")
def obtener_mi_perfil(usuario: USUARIOS = Depends(get_current_active_user)):
    return UserProfile.model_validate(usuario)
```

FastAPI maneja la inyección de dependencias (DB session, usuario autenticado, etc.).

## Backend: Repository Pattern (implícito)

Los routers hacen queries directas via SQLAlchemy. No hay una capa Repository explícita, pero los services encapsulan lógica compleja:

```python
# assignments/service.py
def asignar_taller_automaticamente(db, id_incidente):
    # Lógica de búsqueda por GPS + disponibilidad
```

## Backend: State Machine (Técnicos)

Máquina de estados para el flujo del técnico:

```
ASIGNADO → EN_CAMINO → EN_PROCESO → ATENDIDO
```

Validación estricta: solo permite transiciones válidas.

## Backend: Observer Pattern (WebSocket)

Notificaciones en tiempo real cuando cambia el estado:

```python
broadcast_global({"tipo": "estado_actualizado", ...})
broadcast_incidente_async(id_incidente, {"tipo": "ubicacion_tecnico", ...})
```

## Frontend: Feature-based Architecture

Cada feature es un módulo independiente con su componente y servicio. Lazy loading por feature.

## Frontend: Guard Pattern

```typescript
canActivate: [authGuard]  // Verifica JWT antes de acceder a rutas
```

## Mobile: Provider Pattern

State management con Provider:

```dart
ChangeNotifierProvider(
  create: (_) => IncidentProvider(),
  child: MyApp(),
)
```

## Mobile: Repository Pattern

Separación entre data y presentation:

```
Screen → Provider → Repository → API Client → HTTP
```

## Principios Aplicados

| Principio | Aplicación |
|-----------|-----------|
| **S** — Single Responsibility | Cada módulo tiene una responsabilidad |
| **O** — Open/Closed | Enums para estados, extensible |
| **L** — Liskov Substitution | Roles heredan de USUARIOS |
| **I** — Interface Segregation | Dependencias específicas por rol |
| **D** — Dependency Inversion | FastAPI DI + SQLAlchemy abstraction |

## Documentos Relacionados

- [[Visión General]]
- [[Backend]]
- [[Frontend]]
- [[Mobile]]
