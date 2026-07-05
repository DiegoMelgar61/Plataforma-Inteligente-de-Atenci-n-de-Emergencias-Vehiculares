---
titulo: "Flujo de Reporte de Incidente"
tipo: Flujo
fecha: 2026-07-03
tags: [flujo, incidente, reporte, multimodal]
---

# Flujo de Reporte de Incidente

## Diagrama

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Cliente │────▶│ Mobile/ │────▶│ Backend │────▶│   IA    │────▶│   DB    │
│         │     │ Frontend│     │         │     │ Service │     │         │
└─────────┘     └─────────┘     └─────────┘     └─────────┘     └─────────┘
     │               │               │               │               │
     │  1. Tomar foto/audio         │               │               │
     │  2. Obtener GPS              │               │               │
     │  3. POST /incidents/report   │               │               │
     │  (multipart: lat,lng,imgs,  │               │               │
     │   audio,texto)              │               │               │
     │──────────────────────────────▶│               │               │
     │                              │  4. Crear incidente           │
     │                              │  estado=PENDIENTE             │
     │                              │──────────────────────────────▶│
     │                              │  5. Guardar evidencias        │
     │                              │  en uploads/evidencias/{id}/  │
     │                              │──────────────────────────────▶│
     │                              │  6. Ejecutar pipeline IA      │
     │                              │──────────────▶│               │
     │                              │               │  7. Transcribir audio
     │                              │               │  8. Analizar imágenes
     │                              │               │  9. Clasificar incidente
     │                              │               │ 10. Asignar prioridad
     │                              │               │ 11. Generar resumen
     │                              │◀──────────────│               │
     │                              │  12. Actualizar estado        │
     │                              │  a CLASIFICADO                │
     │                              │──────────────────────────────▶│
     │  13. {incidente_id,          │               │               │
     │       evidencias}            │               │               │
     │◀──────────────────────────────│               │               │
     │                              │               │               │
     │  14. WebSocket: nuevo        │               │               │
     │      incidente reportado     │               │               │
     │◀─────────────────────────────│               │               │
```

## Estados del Incidente

```
PENDIENTE → EN_PROCESO_IA → CLASIFICADO → ASIGNADO → EN_CAMINO → EN_PROCESO → ATENDIDO
                                                                  ↘ CANCELADO
```

## Tipos de Evidencia

| Tipo | Formato | Procesamiento IA |
|------|---------|-----------------|
| IMAGEN | JPEG, PNG, WEBP, GIF | Análisis de imagen |
| AUDIO | MP3, WAV, WEBM, OGG | Transcripción a texto |
| TEXTO | String | Clasificación directa |

## Validaciones

- Solo CLIENTE puede reportar
- Debe incluir al menos una imagen, audio o texto
- Vehículo debe pertenecer al cliente
- Cliente no debe tener multa pendiente

## Documentos Relacionados

- [[Incidentes]]
- [[Endpoints]]
- [[Autenticación]]
