---
titulo: "Elección de Stack Tecnológico"
tipo: Decisión
fecha: 2026-07-03
tags: [decisión, stack, fastapi, angular, flutter]
---

# Elección de Stack Tecnológico

## Backend: FastAPI

**Por qué FastAPI:**
- Rendimiento alto (async/await nativo)
- Auto-generación de docs (Swagger/OpenAPI)
- Type hints + Pydantic = validación automática
- Dependencias inyectables
- Soporte WebSocket nativo

**Alternativas consideradas:**
- Django: Más pesado, ORM propio, menos moderno
- Flask: Sin async nativo, menos features
- Express.js: No tiene type safety nativo

## Frontend: Angular

**Por qué Angular:**
- Framework completo (routing, forms, HTTP, testing)
- TypeScript = type safety
- Angular Material = UI profesional
- Lazy loading nativo
- Standalone components (moderno)

**Alternativas consideradas:**
- React: Más flexible pero menos estructurado
- Vue: Menos enterprise-ready
- Svelte: Más nuevo, menos ecosistema

## Mobile: Flutter

**Por qué Flutter:**
- Single codebase para iOS y Android
- Hot reload = productividad alta
- Dart = type safety
- Provider = state management simple
- Buena documentación

**Alternativas consideradas:**
- React Native: Más plugins pero más complejo
- Kotlin Multiplatform: Más nuevo, menos maduro
- Swift/UI: Solo iOS

## DB: PostgreSQL + PostGIS

**Por qué PostgreSQL:**
- Robusto y escalable
- PostGIS = geolocalización nativa
- Supabase = hosting managed con features extra
- JSONB = flexibilidad
- Extensions丰富

**Alternativas consideradas:**
- MySQL: Sin PostGIS nativo
- MongoDB: Sin relational integrity
- Firebase: Vendor lock-in

## Documentos Relacionados

- [[Stack Tecnológico]]
- [[Resumen del Proyecto]]
