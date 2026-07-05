---
titulo: "Visión General de Arquitectura"
tipo: Arquitectura
fecha: 2026-07-03
tags: [arquitectura, overview, monorepo]
---

# Visión General de Arquitectura

## Tipo de Arquitectura

**Monorepo** con tres capas independientes:

```
┌─────────────────────────────────────────────────────┐
│                    MONOREPO                         │
├──────────────┬──────────────┬───────────────────────┤
│   backend/   │  frontend/   │       mobile/         │
│   FastAPI    │   Angular    │       Flutter         │
│   Python     │   TypeScript │       Dart            │
└──────┬───────┴──────┬───────┴───────────┬───────────┘
       │              │                   │
       ▼              ▼                   ▼
  ┌─────────┐   ┌──────────┐      ┌──────────────┐
  │Supabase │   │  Vercel  │      │  Dispositivo │
  │PostgreSQL│   │  (SPA)   │      │  (iOS/Android│
  │+PostGIS │   └──────────┘      └──────────────┘
  └─────────┘
```

## Comunicación entre Capas

```
Mobile (Flutter)  ──HTTP/WS──▶  Backend (FastAPI)  ──SQL──▶  Supabase (PostgreSQL)
                                        ▲
Frontend (Angular) ──HTTP/WS────────────┘
```

- **HTTP REST**: CRUD operaciones, autenticación, reportes
- **WebSocket**: Notificaciones en tiempo real, tracking GPS, dashboards
- **JWT**: Token Bearer compartido entre las tres capas

## Patrón de Arquitectura Backend

**Arquitectura Modular** (no es Clean Architecture completa, pero sigue principios similares):

```
backend/app/
├── core/           ← Infraestructura compartida (DB, config, security)
├── modules/        ← Dominio de negocio (cada módulo = models + schemas + router + service)
├── infrastructure/ ← Servicios externos (IA)
└── main.py         ← Orquestación (FastAPI app)
```

## Patrón de Arquitectura Frontend

**Feature-based** con lazy loading:

```
frontend/src/app/
├── core/           ← Servicios globales, guards, interceptors
├── features/       ← Cada feature = componente + servicio
├── layout/         ← Componentes de layout (navbar, sidebar)
└── models/         ← Modelos compartidos
```

## Patrón de Arquitectura Mobile

**Presentation → Data** con Provider:

```
mobile/lib/
├── core/           ← Config, API client
├── data/           ← Models + Repositories
├── presentation/   ← Providers + Screens
└── shared/         ← Widgets reutilizables
```

## Aislamiento Multi-Tenant

Todos los módulos de negocio filtran por `ID_TENANT`:

```
Usuario → ID_TENANT → Talleres del tenant → Incidentes del tenant → Pagos del tenant
```

- **ADMIN**: Acceso total (super-admin de plataforma)
- **CLIENTE**: Solo sus propios datos
- **TALLER / TECNICO**: Datos de su mismo tenant

## Documentos Relacionados

- [[Backend]]
- [[Frontend]]
- [[Mobile]]
- [[Patrones de Diseño]]
