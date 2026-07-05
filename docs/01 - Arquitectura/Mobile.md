---
titulo: "Arquitectura Mobile"
tipo: Arquitectura
fecha: 2026-07-03
tags: [mobile, flutter, dart, arquitectura]
---

# Arquitectura Mobile

## Stack

- **Framework**: Flutter / Dart
- **State**: Provider
- **HTTP**: Dio
- **Storage**: SharedPreferences

## Estructura

```
mobile/lib/
├── main.dart                 ← Entry point
├── core/
│   ├── config.dart           ← API URLs, constants
│   ├── api_client.dart       ← Dio HTTP client
│   └── auth_service.dart     ← JWT storage
├── data/
│   ├── models/
│   │   ├── auth_models.dart      ← Login, registro
│   │   ├── incident_models.dart  ← Incidentes, evidencias
│   │   ├── assignment_models.dart ← Asignaciones, cotizaciones
│   │   ├── payment_models.dart   ← Pagos
│   │   └── vehicle_models.dart   ← Vehículos
│   └── repositories/
│       ├── incident_repository.dart
│       ├── payments_repository.dart
│       └── technician_repository.dart
├── presentation/
│   ├── providers/
│   │   ├── incident_providers.dart
│   │   └── technician_providers.dart
│   ├── screens/
│   │   ├── auth/               ← Login
│   │   ├── incidents/          ← Incidentes
│   │   ├── map/                ← Mapa
│   │   ├── payments/           ← Pagos
│   │   └── profile/            ← Perfil
│   └── routes.dart             ← Navegación
└── shared/
    └── widgets.dart            ← Widgets reutilizables
```

## Modelos Principales

| Modelo | Campos clave |
|--------|-------------|
| `Usuario` | id, correo, nombre, telefono, rol |
| `Incidente` | id, ubicacion, estado, prioridad, clasificacion |
| `Evidencia` | id, tipo, url, textoTranscrito |
| `Asignacion` | id, idTaller, idTecnico, montoCotizado |
| `Pago` | id, monto, estado, metodoPago |
| `Vehiculo` | id, marca, modelo, anio, placa |

## Flujos Principales

1. **Login** → Auth screens → Provider → Repository → API
2. **Reportar** → Camera/GPS → Form → Provider → Repository → API
3. **Seguimiento** → WebSocket → Provider → UI update
4. **Pago** → Form → Provider → Repository → API

## Documentos Relacionados

- [[Visión General]]
- [[Stack Tecnológico]]
- [[Setup Local]]
