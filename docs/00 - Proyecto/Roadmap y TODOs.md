---
titulo: "Roadmap y TODOs"
tipo: Roadmap
fecha: 2026-07-05
tags: [roadmap, todo, pendientes, mejoras]
---

# Roadmap y TODOs

## Estado de Trabajo

| Tema | Decisión |
|------|----------|
| Rama de desarrollo | `dev` |
| Rama de producción | `main` |
| Integración | Pull Request `dev` → `main` |
| Documentación | `docs/` se versiona en Git |
| Obsidian UI local | `docs/.obsidian/workspace.json` no se versiona |

## Completado

- [x] Backend: Arquitectura modular con 18 módulos
- [x] Backend: Migración UUID → Integer PKs
- [x] Backend: Pipeline de procesamiento IA
- [x] Backend: Sistema de pagos con comprobantes
- [x] Backend: WebSocket notificaciones + tracking GPS
- [x] Backend: Multi-tenant con aislamiento por tenant
- [x] Backend: Bitácora de auditoría
- [x] Backend: Alembic migrations en Supabase
- [x] Frontend: Angular standalone con lazy loading
- [x] Frontend: 15 features (login, dashboard, admin, etc.)
- [x] Frontend: Deploy en Vercel
- [x] Mobile: Flutter con Provider
- [x] Mobile: Modelos migrados a int IDs
- [x] Mobile: Flujo offline/sync parcial implementado
- [x] Infra: Docker Compose con Supabase
- [x] Documentación: Vault de Obsidian
- [x] Producción: `main` validado en primera instancia

## Pendiente (Prioridad Alta)

- [ ] Tests backend: Arreglar tests que apuntan a Supabase en vez de DB local
- [ ] Tests frontend: Configurar testing con Karma/Jest
- [ ] Tests mobile: Configurar testing con flutter_test
- [ ] CI/CD: GitHub Actions para lint + test + build automático
- [ ] Backend: Health check detallado (DB, migración, storage, servicios críticos)
- [ ] Observabilidad: Logging estructurado y trazabilidad de errores productivos
- [ ] Seguridad: Rate limiting en endpoints públicos
- [ ] Seguridad: Refresh tokens (rotación de JWT)

## Pendiente (Prioridad Media)

- [ ] Pagos: Integración con pasarela de pago real (Stripe/MercadoPago)
- [ ] IA: Dashboard de métricas de procesamiento IA
- [ ] Mobile: Completar hardening del modo offline/sync (conflictos, reintentos, UX de errores)
- [ ] Frontend: Modo oscuro
- [ ] Frontend: Exportar reportes en PDF
- [ ] Monitoreo: Métricas con Prometheus/Grafana

## Pendiente (Prioridad Baja)

- [ ] Infra: Redis para caché de sesiones y rate limiting
- [ ] Infra: CDN para archivos estáticos (evidencias, comprobantes)
- [ ] Mobile: Push notifications (FCM/APNs)
- [ ] Frontend: PWA capabilities
- [ ] Backend: GraphQL (opcional)
- [ ] Documentación: Swagger/OpenAPI detallado por módulo

## Bugs Conocidos

- Backend tests fallan contra Supabase (entorno, no código)
- `NG8102` warnings en Angular build (pre-existentes)
- Lint warnings en Flutter config (pre-existentes)

## Documentos Relacionados

- [[Resumen del Proyecto]]
- [[Estado Actual del Proyecto]]
- [[Stack Tecnológico]]
- [[Setup Local]]
