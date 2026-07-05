---
titulo: "Arquitectura Backend"
tipo: Arquitectura
fecha: 2026-07-03
tags: [backend, fastapi, python, arquitectura]
---

# Arquitectura Backend

## Stack

- **Framework**: FastAPI (Python)
- **ORM**: SQLAlchemy (synchronous)
- **DB**: PostgreSQL + PostGIS (Supabase)
- **Migraciones**: Alembic
- **Auth**: JWT (PyJWT) + bcrypt
- **Archivos**: FastAPI StaticFiles

## Estructura de Módulos

Cada módulo sigue el patrón:

```
modules/{nombre}/
├── __init__.py
├── models.py        ← Modelos SQLAlchemy (tablas)
├── schemas.py       ← Pydantic schemas (request/response)
├── router.py        ← Endpoints FastAPI
├── service.py       ← Lógica de negocio (opcional)
└── dependencies.py  ← Dependencias de autenticación (solo auth/)
```

## Módulos Activos (18)

| Módulo | Responsabilidad | Rutas principales |
|--------|----------------|-------------------|
| `auth` | Login, registro, JWT | `/auth/login`, `/auth/register` |
| `users` | Perfil, gestión usuarios | `/usuarios/me`, `/usuarios` |
| `tenants` | Multi-tenant CRUD | `/api/v1/tenants` |
| `vehicles` | Vehículos del cliente | `/vehicles` |
| `workshops` | Talleres mecánicos | `/talleres` |
| `technicians` | Técnicos del taller | `/tecnicos` |
| `incidents` | Incidentes + evidencias + IA | `/incidents` |
| `assignments` | Asignación inteligente + cotizaciones | `/assignments` |
| `payments` | Pagos con comprobantes | `/payments` |
| `notifications` | WebSocket notificaciones | `/notifications/ws` |
| `tracking` | GPS tracking en tiempo real | `/tracking/ws` |
| `stats` | Estadísticas | `/stats` |
| `bitacora` | Auditoría | `/bitacora` |
| `reports` | Reportes | `/reports` |
| `backups` | Respaldos | `/backups` |
| `dashboards_ia` | Dashboards con IA | `/dashboards-ia` |

## Flujo de Request

```
Request → CORS Middleware → Router → Dependencies (auth) → Endpoint → Service → DB → Response
```

## Dependencias de Autenticación

```python
get_current_user        ← Decodifica JWT, retorna USUARIOS
get_current_active_user ← Valida que esté activo
get_current_cliente     ← Solo rol CLIENTE
get_current_taller      ← Solo rol TALLER
get_current_admin       ← Solo rol ADMIN
get_current_tecnico     ← Solo rol TECNICO (retorna TECNICOS)
```

## Aislamiento por Tenant

```python
def verificar_acceso_incidente(usuario, incidente):
    if rol == "ADMIN": return  # Acceso total
    if rol == "CLIENTE":
        # Solo sus propios incidentes
    # TALLER / TECNICO: solo mismo tenant
```

## Lifespan (Startup/Shutdown)

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: crear directorios de uploads
    uploads/evidencias/
    uploads/comprobantes/
    yield
    # Shutdown: cleanup
```

## Documentos Relacionados

- [[Endpoints]] — Lista completa de endpoints
- [[Autenticación]] — JWT, roles, permisos
- [[Modelo de Datos]] — Tablas y relaciones
- [[Arquitectura Modular]] — Decisiones de diseño
