---
titulo: "Estado Actual del Proyecto"
tipo: Estado
fecha: 2026-07-05
tags: [estado-actual, produccion, trazabilidad]
---

# Estado Actual del Proyecto

El sistema está en producción y funcionando en primera instancia. El desarrollo continúa en `dev`; cada nueva funcionalidad se valida ahí y luego se integra a `main` mediante Pull Request.

## Snapshot

| Área | Estado |
|------|--------|
| Producción | Activa en `main` |
| Rama de trabajo | `dev` |
| Backend | FastAPI modular, UUID→int desplegado |
| Frontend | Angular 18 en `frontend/` |
| Mobile | Flutter con flujo cliente/técnico y sync offline parcial |
| DB | Supabase PostgreSQL + PostGIS |
| Documentación | Vault Obsidian versionado en `docs/` |

## Hechos Confirmados

- La migración UUID→int ya fue aplicada y validada.
- `main` contiene el merge de `dev` vía PR.
- El contenido de `dev` y `main` está alineado; `main` tiene más commits por merges históricos.
- El vault de Obsidian vive dentro del repo para trazabilidad.
- La configuración visual/local de VS Code queda fuera de Git.
- `docs/.obsidian/workspace.json` queda fuera de Git porque representa estado local de la UI.

## Superficie Funcional Actual

### Backend

- Auth JWT con roles `CLIENTE`, `TALLER`, `ADMIN`, `TECNICO`.
- Incidentes multimodales con evidencias de imagen, audio y texto.
- Procesamiento IA para diagnóstico, clasificación, prioridad y resumen.
- Asignación inteligente y cotizaciones.
- Flujo de técnico con máquina de estados.
- Pagos manuales con comprobantes.
- WebSockets para notificaciones y tracking GPS.
- Multi-tenant con aislamiento por tenant.
- Bitácora, reportes, backups, stats y dashboards IA.

### Frontend

- Panel Angular con dashboard, requests, assignments, technicians, map, payments, operations, history, bitácora, backups, dashboards IA, tenants y administración.
- Routing protegido con guards.
- WebSocket service para actualizaciones en tiempo real.

### Mobile

- App Flutter para cliente y técnico.
- Reporte de incidentes, detalle, pagos, mapa, perfil y pantalla de técnico.
- Flujo offline/sync parcial ya implementado con almacenamiento local y sincronización.

## Pendientes Reales

- Corregir estrategia de tests backend para no depender de Supabase productiva.
- Agregar health check profundo: DB, migración actual, storage y servicios críticos.
- Mejorar observabilidad: logging estructurado, errores operativos y métricas.
- Definir pipeline CI/CD para validar cambios antes del PR a `main`.
- Evaluar rate limiting en endpoints sensibles como login y registro.

## Documentos Relacionados

- [[Roadmap y TODOs]]
- [[Conventions]]
- [[Backend]]
- [[Frontend]]
- [[Mobile]]
- [[Migración UUID→int]]
