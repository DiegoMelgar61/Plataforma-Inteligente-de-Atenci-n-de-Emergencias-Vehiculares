---
titulo: "Flujo de Asignación de Técnico"
tipo: Flujo
fecha: 2026-07-03
tags: [flujo, asignacion, tecnico, taller]
---

# Flujo de Asignación de Técnico

## Diagrama

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Cliente │────▶│ Backend │────▶│  Taller │────▶│ Técnico │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
     │               │               │               │
     │  1. GET /incidents/{id}/cotizaciones
     │  (ver ofertas de talleres cercanos)
     │──────────────────────────────▶│               │
     │  2. Lista de ofertas con      │               │
     │     precios y distancias     │               │
     │◀──────────────────────────────│               │
     │                               │               │
     │  3. POST /incidents/{id}/seleccionar-taller
     │  {id_taller}                 │               │
     │──────────────────────────────▶│               │
     │                               │  4. Crear ASIGNACION
     │                               │  estado=ASIGNADO
     │                               │  técnico=disponible
     │                               │──────────────▶│
     │                               │               │
     │  5. Taller propone cotización │               │
     │  POST /assignments/.../cotizacion
     │                               │◀──────────────│
     │                               │               │
     │  6. Cliente responde         │               │
     │  POST /assignments/.../respuesta
     │  {aceptada: true}            │               │
     │──────────────────────────────▶│               │
     │                               │  7. Estado → EN_CAMINO
     │                               │──────────────▶│
     │                               │               │
     │                               │  8. Técnico avanza
     │                               │  EN_CAMINO → EN_PROCESO
     │                               │  → ATENDIDO
     │                               │──────────────▶│
     │                               │               │
     │  9. WebSocket: estado         │               │
     │     actualizado               │               │
     │◀──────────────────────────────│               │
```

## Máquina de Estados del Técnico

```
ASIGNADO ──▶ EN_CAMINO ──▶ EN_PROCESO ──▶ ATENDIDO
```

Solo el técnico asignado puede avanzar el estado.

## Asignación Automática por GPS

```
1. Buscar talleres cercanos con PostGIS (ST_DWithin)
2. Verificar técnicos disponibles
3. Seleccionar el más cercano
4. Crear ASIGNACION
5. Marcar técnico como no disponible
```

## Cancelación por Cliente

```
POST /incidents/{id}/cancelar
```

- Si técnico está en camino: multa del 20%
- Si técnico no está en camino: sin multa
- Cliente queda bloqueado hasta pagar multa

## Documentos Relacionados

- [[Asignaciones]]
- [[Talleres y Técnicos]]
- [[Incidentes]]
