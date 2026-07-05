---
titulo: "Vault del Proyecto"
tipo: Índice
fecha: 2026-07-03
tags: [vault, índice, nawigación]
---

# Vault del Proyecto

**Plataforma Inteligente de Atención de Emergencias Vehiculares**

Centralización versionada de la información del proyecto en Obsidian para mantener trazabilidad entre documentación, código y producción.

---

## Estado Actual

| Tema | Estado |
|------|--------|
| Producción | `main` activo y validado |
| Desarrollo | Todo cambio nuevo se trabaja en `dev` |
| Integración | PR de `dev` hacia `main` |
| Documentación | `docs/` se versiona en Git |
| Config local | `.vscode/` y `docs/.obsidian/workspace.json` quedan fuera de Git |

## 00 - Proyecto

- [[Resumen del Proyecto]] — Visión general del sistema
- [[Estado Actual del Proyecto]] — Snapshot operativo vigente
- [[Stack Tecnológico]] — Tecnologías y dependencias
- [[Roadmap y TODOs]] — Pendientes y mejoras

## 01 - Arquitectura

- [[Visión General]] — Arquitectura monorepo y patrones
- [[Backend]] — FastAPI, módulos, estructura
- [[Frontend]] — Angular, features, routing
- [[Mobile]] — Flutter, providers, screens
- [[Patrones de Diseño]] — SOLID, state machine, observer

## 02 - API

- [[Endpoints]] — Lista completa de endpoints REST
- [[Autenticación]] — JWT, roles, permisos
- [[WebSockets]] — Tiempo real, notificaciones, tracking
- [[Schemas]] — Pydantic models request/response

## 03 - Modelo de Datos

- [[Diagrama ER]] — Entidades y relaciones
- [[Usuarios y Roles]] — Modelo de usuarios
- [[Incidentes]] — Incidentes y evidencias
- [[Talleres y Técnicos]] — Modelo de talleres
- [[Asignaciones]] — Asignaciones y cotizaciones
- [[Pagos]] — Sistema de pagos
- [[Bitácora]] — Auditoría

## 04 - Flujos

- [[Login y Registro]] — Autenticación
- [[Reporte de Incidente]] — Flujo multimodal
- [[Asignación de Técnico]] — Selección GPS
- [[Flujo de Pago]] — Comprobantes y confirmación
- [[Dashboards IA]] — Analytics en tiempo real

## 05 - Decisiones Técnicas

- [[Migración UUID→int]] — De UUID a Integer PKs
- [[Arquitectura Modular]] — Reorganización de código
- [[Stack Choices]] — Por qué FastAPI, Angular, Flutter

## 06 - Infraestructura

- [[Docker]] — Containerización
- [[Supabase]] — PostgreSQL hosting
- [[Environment Variables]] — Configuración

## 07 - Desarrollo

- [[Setup Local]] — Guía de instalación
- [[Testing]] — Estrategia de tests
- [[Workflow de Desarrollo]] — Flujo dev → PR → main
- [[Conventions]] — Convenciones de código

## 08 - Exámenes

- [[Primer Parcial]] — Documento del examen 1 (casos de uso incluidos)
- [[Segundo Parcial]] — Documento del examen 2 (casos de uso incluidos)

## Templates

- [[Plantilla Endpoint]] — Para documentar endpoints
- [[Plantilla Decisión]] — Para documentar decisiones técnicas
- [[Plantilla Flujo]] — Para documentar flujos

---

## Navegación Rápida

| Quiero ver... | Ir a... |
|---------------|---------|
| Estado operativo actual | [[Estado Actual del Proyecto]] |
| Cómo trabajamos cambios nuevos | [[Workflow de Desarrollo]] |
| Cómo corre el proyecto | [[Setup Local]] |
| Todos los endpoints | [[Endpoints]] |
| Cómo se autentica | [[Autenticación]] |
| Modelo de datos completo | [[Diagrama ER]] |
| Flujo de un incidente | [[Reporte de Incidente]] |
| Por qué se migró UUID | [[Migración UUID→int]] |
| Documentos de exámenes | [[Primer Parcial]], [[Segundo Parcial]] |

---

*Última actualización: 2026-07-05*
