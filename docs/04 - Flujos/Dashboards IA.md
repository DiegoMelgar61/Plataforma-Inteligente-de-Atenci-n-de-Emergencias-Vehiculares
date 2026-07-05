---
titulo: "Dashboards con IA"
tipo: Flujo
fecha: 2026-07-03
tags: [flujo, dashboards, ia, analytics]
---

# Dashboards con IA

## Datos del Dashboard

El dashboard muestra en tiempo real:

- **Incidentes activos**: PENDIENTE, EN_PROCESO_IA, CLASIFICADO, ASIGNADO, EN_CAMINO, EN_PROCESO
- **Técnicos disponibles**: Por taller
- **Pagos pendientes**: Montos y estados
- **Estadísticas**: Por período, por tenant

## Fuentes de Datos

```
WebSocket Global (/notifications/ws)
    │
    ├── incidente_reportado → Actualizar mapa
    ├── estado_actualizado → Actualizar contadores
    ├── pago_creado → Actualizar pagos
    ├── pago_confirmado → Actualizar estadísticas
    └── ubicacion_tecnico → Actualizar mapa en tiempo real
```

## KPIs Principales

| KPI | Cálculo |
|-----|---------|
| Tiempo promedio de atención | ATENDIDO - FECHA_CREACION |
| Tasa de cancelación | CANCELADOS / TOTAL |
| Ingresos totales | SUM(MONTO) WHERE ESTADO=PAGADO |
| Satisfacción del cliente | (pendiente de implementar) |
| Técnicos activos | COUNT(TECNICOS.DISPONIBLE=True) |

## Documentos Relacionados

- [[WebSockets]]
- [[Estadísticas]]
- [[Resumen del Proyecto]]
