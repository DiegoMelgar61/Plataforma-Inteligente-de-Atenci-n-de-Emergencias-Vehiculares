---
titulo: "Flujo de Pago"
tipo: Flujo
fecha: 2026-07-03
tags: [flujo, pago, comprobante, manual]
---

# Flujo de Pago

## Diagrama

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Técnico │────▶│ Backend │────▶│ Cliente │────▶│  Taller │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
     │               │               │               │
     │  1. Técnico cambia estado     │               │
     │  a ATENDIDO                   │               │
     │──────────────────────────────▶│               │
     │                               │  2. Crear PAGO│
     │                               │  estado=PENDIENTE
     │                               │──────────────▶│
     │                               │               │
     │                               │  3. WebSocket│
     │                               │  pago_creado │
     │                               │──────────────▶│
     │                               │               │
     │                               │  4. Cliente sube
     │                               │  comprobante
     │                               │  POST /payments/{id}/mark-paid
     │                               │◀──────────────│
     │                               │  5. Guardar archivo
     │                               │  estado=PAGADO
     │                               │──────────────▶│
     │                               │               │
     │                               │  6. Taller confirma
     │                               │  POST /payments/{id}/confirm
     │                               │◀──────────────│
     │                               │  7. Estado=PAGADO
     │                               │  (confirmado)
     │                               │──────────────▶│
     │                               │               │
     │  8. WebSocket: pago_confirmado│               │
     │◀──────────────────────────────│               │
```

## Estados del Pago

```
NO_PAGO → PENDIENTE → PAGADO → (confirmado)
                   ↘ RECHAZADO
```

## Comisiones

- `tasa_comision`: Porcentaje del taller (default 10%)
- `comision_plataforma`: Calculada al crear el pago

## Rechazo de Comprobante

```
POST /payments/{id}/reject
{"motivo_rechazo": "Comprobante ilegible"}
```

- Estado → RECHAZADO
- Cliente puede subir nuevo comprobante

## Documentos Relacionados

- [[Pagos]]
- [[Incidentes]]
- [[Endpoints]]
