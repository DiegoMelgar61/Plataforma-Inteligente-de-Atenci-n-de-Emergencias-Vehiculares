---
titulo: "WebSockets y Tiempo Real"
tipo: API
fecha: 2026-07-03
tags: [websocket, realtime, notificaciones, tracking]
---

# WebSockets y Tiempo Real

## Canales Disponibles

### 1. WebSocket Global (`/notifications/ws`)

**Para**: Dashboard y mapa en tiempo real  
**Roles**: ADMIN, TALLER, TECNICO  
**Auth**: JWT en query string `?token=<jwt>`

**Eventos recibidos**:
```json
{
  "tipo": "incidente_reportado",
  "incidente_id": "123",
  "clasificacion": "CHOQUE",
  "prioridad": "ALTA",
  "mensaje": "Nuevo incidente reportado",
  "timestamp": "2026-07-03T12:00:00"
}
```

```json
{
  "tipo": "estado_actualizado",
  "incidente_id": "123",
  "nuevo_estado": "EN_CAMINO",
  "mensaje": "Incidente 123 cambió a EN_CAMINO",
  "timestamp": "2026-07-03T12:05:00"
}
```

### 2. WebSocket por Incidente (`/notifications/ws/incidents/{id}`)

**Para**: Seguimiento en tiempo real de un incidente específico  
**Roles**: CLIENTE (dueño), TALLER, ADMIN  
**Auth**: JWT en query string

**Eventos recibidos**:
- `estado_actualizado` — Cambio de estado
- `cotizacion_propuesta` — Taller propuso cotización
- `cotizacion_aceptada` — Cliente aceptó
- `cotizacion_rechazada` — Cliente rechazó
- `ubicacion_tecnico` — Ubicación GPS del técnico
- `pago_creado` — Pago generado
- `pago_confirmado` — Pago confirmado
- `pago_rechazado` — Pago rechazado

### 3. Tracking GPS (`/tracking/ws/incidents/{id}`)

**Para**: Técnico envía ubicación GPS en tiempo real  
**Roles**: TECNICO  
**Auth**: JWT en query string `?token=<jwt>`

**Flujo**:
```
1. Técnico se conecta
2. Servidor valida token + asignación activa
3. Servidor acepta conexión
4. Técnico envía: {"lat": -16.5, "lng": -68.15}
5. Servidor persiste en TECNICOS.UBICACION_ACTUAL
6. Servidor broadcast a suscriptores del incidente
7. Al llegar a ATENDIDO → servidor cierra conexión
```

**Mensajes del técnico**:
```json
{"lat": -16.5, "lng": -68.15}
```

**Mensajes a suscriptores**:
```json
{
  "tipo": "ubicacion_tecnico",
  "incidente_id": "123",
  "tecnico_id": "456",
  "lat": -16.5,
  "lng": -68.15,
  "timestamp": "2026-07-03T12:10:00"
}
```

## Documentos Relacionados

- [[Endpoints]]
- [[Autenticación]]
- [[Tracking GPS]]
