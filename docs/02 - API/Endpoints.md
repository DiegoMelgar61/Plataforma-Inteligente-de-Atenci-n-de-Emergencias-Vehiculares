---
titulo: "Endpoints API"
tipo: API
fecha: 2026-07-03
tags: [api, endpoints, rest, http]
---

# Endpoints API

## Autenticación (`/auth`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| `POST` | `/auth/register` | Registro de usuario (rol CLIENTE) | No |
| `POST` | `/auth/login` | Login → JWT token | No |

## Usuarios (`/usuarios`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| `GET` | `/usuarios/me` | Mi perfil | Cualquier rol |
| `PUT` | `/usuarios/me` | Actualizar mi perfil | Cualquier rol |
| `GET` | `/usuarios` | Listar usuarios (filtro: rol, activo) | ADMIN |
| `PATCH` | `/usuarios/{id}/rol` | Cambiar rol | ADMIN |
| `PATCH` | `/usuarios/{id}/activo` | Activar/desactivar | ADMIN |

## Talleres (`/talleres`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| `GET` | `/talleres` | Listar talleres | Cualquier rol |
| `GET` | `/talleres/{id}` | Detalle de taller | Cualquier rol |
| `POST` | `/talleres` | Crear taller | TALLER, ADMIN |
| `PUT` | `/talleres/{id}` | Actualizar taller | Dueño, ADMIN |
| `DELETE` | `/talleres/{id}` | Baja lógica | Dueño, ADMIN |

## Técnicos (`/tecnicos`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| `GET` | `/tecnicos/mi-asignacion` | Orden activa del técnico | TECNICO |
| `PATCH` | `/tecnicos/incidente/{id}/estado` | Máquina de estados | TECNICO |
| `GET` | `/tecnicos` | Listar técnicos | TALLER, ADMIN |
| `POST` | `/tecnicos` | Crear técnico (sin login) | TALLER |
| `POST` | `/tecnicos/crear-con-usuario` | Crear técnico con login | TALLER, ADMIN |
| `GET` | `/tecnicos/{id}` | Detalle de técnico | TALLER |
| `PUT` | `/tecnicos/{id}` | Actualizar técnico | TALLER |
| `DELETE` | `/tecnicos/{id}` | Eliminar técnico | TALLER |

## Incidentes (`/incidents`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| `POST` | `/incidents/report` | Reportar incidente multimodal | CLIENTE |
| `POST` | `/incidents/sync` | Sincronizar offline | CLIENTE |
| `GET` | `/incidents` | Listar todos (TALLER/ADMIN) | TALLER, ADMIN |
| `GET` | `/incidents/my` | Mis incidentes | Cualquier rol |
| `GET` | `/incidents/{id}` | Detalle con evidencias | Dueño, TALLER, ADMIN |
| `PATCH` | `/incidents/{id}/estado` | Actualizar estado | TALLER, ADMIN |
| `GET` | `/incidents/{id}/cotizaciones` | Ofertas de talleres | CLIENTE |
| `POST` | `/incidents/{id}/seleccionar-taller` | Elegir taller | CLIENTE |
| `POST` | `/incidents/{id}/cancelar` | Cancelar servicio | CLIENTE |

## Asignación (`/assignments`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| `POST` | `/assignments/incidents/{id}/assign` | Asignar a taller | TALLER, ADMIN |
| `GET` | `/assignments/incidents/{id}/available-workshops` | Talleres disponibles | Cualquier rol |
| `GET` | `/assignments/my` | Mis asignaciones | TALLER, ADMIN |
| `POST` | `/assignments/incidents/{id}/reject` | Rechazar asignación | TALLER |
| `GET` | `/assignments/incidents/{id}/cotizacion` | Ver cotización | Cualquier rol |
| `POST` | `/assignments/incidents/{id}/cotizacion` | Proponer cotización | TALLER |
| `POST` | `/assignments/incidents/{id}/cotizacion/respuesta` | Responder cotización | CLIENTE |

## Pagos (`/payments`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| `GET` | `/payments/stats` | Estadísticas | TALLER, ADMIN |
| `GET` | `/payments/my` | Mis pagos | Cualquier rol |
| `GET` | `/payments` | Todos los pagos | TALLER, ADMIN |
| `GET` | `/payments/{id}` | Detalle de pago | Cualquier rol |
| `POST` | `/payments/{id}/mark-paid` | Subir comprobante | CLIENTE |
| `POST` | `/payments/{id}/confirm` | Confirmar pago | TALLER, ADMIN |
| `POST` | `/payments/{id}/reject` | Rechazar comprobante | TALLER, ADMIN |

## Notificaciones (`/notifications`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| `WS` | `/notifications/ws` | WebSocket global | ADMIN, TALLER, TECNICO |
| `WS` | `/notifications/ws/incidents/{id}` | WebSocket por incidente | Cualquier rol |
| `POST` | `/notifications/test` | Test de notificación | Cualquier rol |
| `POST` | `/notifications/incidents/{id}/update-status` | Actualizar y notificar | Cualquier rol |

## Tracking GPS (`/tracking`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| `WS` | `/tracking/ws/incidents/{id}` | GPS en tiempo real | TECNICO |

## Otros

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| `GET` | `/health` | Health check | No |
| `GET` | `/stats` | Estadísticas generales | ADMIN, TALLER |
| `GET` | `/bitacora` | Auditoría | ADMIN |
| `GET` | `/reports` | Reportes | ADMIN, TALLER |
| `GET` | `/backups` | Respaldos | ADMIN |
| `GET` | `/dashboards-ia` | Dashboards IA | ADMIN |

## Documentos Relacionados

- [[Autenticación]]
- [[WebSockets]]
- [[Schemas]]
- [[Backend]]
