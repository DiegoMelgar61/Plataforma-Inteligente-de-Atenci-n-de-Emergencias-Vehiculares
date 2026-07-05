---
titulo: "Stack Tecnológico"
tipo: Referencia
fecha: 2026-07-03
tags: [stack, tecnologías, dependencias]
---

# Stack Tecnológico

## Backend (Python + FastAPI)

| Componente | Tecnología | Versión |
|-----------|-----------|---------|
| Framework | FastAPI | — |
| ORM | SQLAlchemy | — |
| Migraciones | Alembic | — |
| DB | PostgreSQL + PostGIS | 16 + 3.5 |
| Geolocalización | GeoAlchemy2 | — |
| Seguridad | bcrypt + JWT (PyJWT) | — |
| Validación | Pydantic v2 | — |
| Testing | pytest + httpx | — |
| IA | Servicio externo (AI Service) | — |

### Estructura de Módulos

```
backend/app/
├── main.py                    # FastAPI app, CORS, routers
├── core/
│   ├── config.py              # Settings (pydantic-settings)
│   ├── database.py            # Engine, SessionLocal, Base
│   └── security.py            # bcrypt, JWT
├── infrastructure/
│   └── external_services/
│       └── ai_service.py      # Pipeline de procesamiento IA
├── models/                    # Re-export de modelos
└── modules/
    ├── auth/                  # Login, registro, JWT
    ├── users/                 # Perfil y gestión de usuarios
    ├── tenants/               # Multi-tenant
    ├── vehicles/              # Vehículos del cliente
    ├── workshops/             # Talleres mecánicos
    ├── technicians/           # Técnicos del taller
    ├── incidents/             # Incidentes + evidencias + IA
    ├── assignments/           # Asignación inteligente + cotizaciones
    ├── payments/              # Pagos manuales con comprobantes
    ├── notifications/         # WebSocket + notificaciones
    ├── tracking/              # GPS tracking en tiempo real
    ├── stats/                 # Estadísticas
    ├── bitacora/              # Auditoría
    ├── reports/               # Reportes
    ├── backups/               # Respaldos
    └── dashboards_ia/         # Dashboards con IA
```

## Frontend (Angular)

| Componente | Tecnología |
|-----------|-----------|
| Framework | Angular (standalone) |
| Routing | Lazy loading |
| UI | Angular Material + Tailwind CSS |
| State | Signals |
| HTTP | HttpClient + interceptors |
| Realtime | WebSocket service |

### Features

`login` · `dashboard` · `admin` · `talleres` · `tecnicos` · `incidentes` · `asignaciones` · `pagos` · `bitacora` · `estadísticas` · `historial` · `backups` · `dashboards-ia` · `mapa` · `notificaciones`

## Mobile (Flutter)

| Componente | Tecnología |
|-----------|-----------|
| Framework | Flutter / Dart |
| State | Provider |
| HTTP | Dio |
| Models | Freezed-like (manuales) |
| Storage | SharedPreferences |

### Estructura

```
mobile/lib/
├── core/                      # Config, API client, auth
├── data/
│   ├── models/                # Modelos de datos
│   └── repositories/          # Repositorios (API calls)
├── presentation/
│   ├── providers/             # State management
│   ├── screens/               # Pantallas
│   └── routes.dart            # Navegación
└── shared/                    # Widgets compartidos
```

## Infraestructura

| Componente | Tecnología |
|-----------|-----------|
| Containerización | Docker + Docker Compose |
| DB Hosting | Supabase (PostgreSQL + PostGIS) |
| Frontend Deploy | Vercel |
| Archivos | StaticFiles locales (evidencias, comprobantes) |
| CI/CD | GitHub Actions (pendiente) |

## Documentos Relacionados

- [[Resumen del Proyecto]]
- [[Docker]]
- [[Supabase]]
- [[Setup Local]]
