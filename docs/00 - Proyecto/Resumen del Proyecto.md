---
titulo: "Plataforma Inteligente de Atención de Emergencias Vehiculares"
tipo: Resumen
fecha: 2026-07-03
tags: [proyecto, resumen, visión-general]
---

# Resumen del Proyecto

## Visión General

Plataforma SaaS multi-tenant para coordinar emergencias vehiculares: reporte de incidentes, evidencias multimodales (fotos, audio, texto), talleres mecánicos, técnicos, asignaciones inteligentes por GPS, pagos, procesamiento con IA y notificaciones en tiempo real.

## Objetivo

Conectar conductores con talleres mecánicos de manera inteligente, usando IA para diagnosticar, clasificar, priorizar y asignar automáticamente el taller más adecuado según ubicación y disponibilidad.

## Stack Principal

| Capa | Tecnología |
|------|-----------|
| Backend | Python + FastAPI |
| Frontend Web | Angular |
| Frontend Móvil | Flutter / Dart |
| Base de Datos | PostgreSQL + PostGIS |
| Realtime | WebSockets |
| IA | Transcripción de audio, análisis de imágenes, clasificación, priorización y resumen |
| Deploy | Docker + Supabase |

## Actores del Sistema

| Rol | Descripción |
|-----|------------|
| `CLIENTE` | Usuario que reporta incidentes y paga servicios |
| `TALLER` | Dueño de negocio mecánico que recibe y gestiona asignaciones |
| `TECNICO` | Técnico del taller que atiende el incidente en campo |
| `ADMIN` | Administrador de plataforma con acceso total |

## Módulos Funcionales

1. **Autenticación** — Registro, login JWT, roles y permisos
2. **Incidentes** — Reporte multimodal (imagen, audio, texto) con GPS
3. **IA** — Pipeline de procesamiento: transcripción, análisis, clasificación, priorización
4. **Asignación** — Selección inteligente de taller por proximidad GPS
5. **Técnicos** — CRUD y máquina de estados (ASIGNADO → EN_CAMINO → EN_PROCESO → ATENDIDO)
6. **Pagos** — Sistema manual con comprobantes y confirmación
7. **Notificaciones** — WebSocket en tiempo real para estados y tracking GPS
8. **Dashboards** — Estadísticas operacionales y KPIs por tenant
9. **Bitácora** — Auditoría de acciones relevantes
10. **Multi-tenant** — Aislamiento de datos por red de talleres

## Documentos Relacionados

- [[Stack Tecnológico]]
- [[Roadmap y TODOs]]
- [[Visión General]] (Arquitectura)
- [[Primer Parcial]] (Examen 1)
- [[Segundo Parcial]] (Examen 2)
