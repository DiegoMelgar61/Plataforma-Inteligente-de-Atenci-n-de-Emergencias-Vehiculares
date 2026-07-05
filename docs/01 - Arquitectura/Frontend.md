---
titulo: "Arquitectura Frontend"
tipo: Arquitectura
fecha: 2026-07-03
tags: [frontend, angular, typescript, arquitectura]
---

# Arquitectura Frontend

## Stack

- **Framework**: Angular (standalone components)
- **Routing**: Lazy loading
- **UI**: Angular Material + Tailwind CSS
- **State**: Signals
- **HTTP**: HttpClient con interceptors
- **Realtime**: WebSocket service

## Estructura

```
frontend/src/app/
├── app.component.ts          ← Root component
├── app.config.ts             ← AppConfig (providers)
├── app.routes.ts             ← Rutas con lazy loading
├── core/
│   ├── guards/
│   │   └── auth.guard.ts     ← Guard de autenticación
│   ├── interceptors/
│   │   └── auth.interceptor.ts ← Interceptor JWT
│   └── services/
│       ├── auth.service.ts   ← Login, registro, logout
│       └── websocket.service.ts ← Conexión WebSocket
├── features/
│   ├── admin/                ← Gestión de usuarios y talleres
│   ├── assignments/          ← Asignaciones
│   ├── auth/                 ← Login
│   ├── backups/              ← Respaldos
│   ├── bitacora/             ← Auditoría
│   ├── dashboard/            ← Dashboard principal
│   ├── dashboards-ia/        ← Dashboards con IA
│   ├── history/              ← Historial y reportes
│   ├── map/                  ← Mapa de incidentes
│   ├── notifications/        ← Notificaciones
│   ├── operations/           ← Operaciones y estadísticas
│   ├── payments/             ← Pagos
│   ├── requests/             ← Incidentes (CRUD)
│   ├── technicians/          ← Gestión de técnicos
│   └── tenants/              ← Gestión de tenants
├── layout/
│   ├── main-layout.component.ts ← Layout principal
│   ├── navbar.component.ts   ← Barra de navegación
│   └── sidebar.component.ts  ← Menú lateral
└── models/
    └── index.ts              ← Modelos compartidos
```

## Features (15)

| Feature | Descripción | Roles |
|---------|------------|-------|
| `login` | Autenticación | Todos |
| `dashboard` | Panel principal | ADMIN, TALLER |
| `admin` | Gestión usuarios/talleres | ADMIN |
| `requests` | CRUD incidentes | CLIENTE, TALLER |
| `assignments` | Asignaciones | TALLER, ADMIN |
| `technicians` | Gestión técnicos | TALLER |
| `payments` | Pagos | Todos |
| `bitacora` | Auditoría | ADMIN |
| `operations` | Estadísticas | ADMIN, TALLER |
| `history` | Historial | ADMIN, TALLER |
| `backups` | Respaldos | ADMIN |
| `dashboards-ia` | Dashboards IA | ADMIN |
| `map` | Mapa | ADMIN, TALLER |
| `notifications` | Notificaciones | Todos |
| `tenants` | Gestión tenants | ADMIN |

## Routing

```typescript
const routes: Routes = [
  { path: 'login', component: LoginComponent },
  {
    path: '',
    component: MainLayoutComponent,
    canActivate: [authGuard],
    children: [
      { path: 'dashboard', component: DashboardComponent },
      { path: 'admin', component: AdminUsersComponent },
      // ... lazy loading para cada feature
    ]
  }
];
```

## Documentos Relacionados

- [[Visión General]]
- [[Stack Tecnológico]]
- [[Setup Local]]
