---
titulo: "Diagrama Entidad-Relación"
tipo: Modelo de Datos
fecha: 2026-07-03
tags: [modelo-datos, er, tablas, relaciones]
---

# Diagrama Entidad-Relación

## Tablas Principales

```
tenants
├── id_tenant (PK)
├── nombre
├── descripcion
├── activo
└── fecha_creacion

usuarios
├── id_usuario (PK)
├── correo_electronico (UNIQUE)
├── hash_contrasena
├── nombre_completo
├── telefono
├── rol (ENUM: CLIENTE, TALLER, ADMIN, TECNICO)
├── activo
├── id_tenant (FK → tenants)
└── fecha_creacion

clientes
└── id_usuario (PK, FK → usuarios)

vehiculos
├── id_vehiculo (PK)
├── id_usuario_cliente (FK → usuarios)
├── marca
├── modelo
├── anio
└── placa (UNIQUE)

talleres
├── id_taller (PK)
├── id_usuario (FK → usuarios, UNIQUE)
├── nombre_negocio
├── nit (UNIQUE)
├── direccion
├── tasa_comision
├── latitud
├── longitud
├── activo
└── id_tenant (FK → tenants)

tecnicos
├── id_tecnico (PK)
├── id_taller (FK → talleres)
├── id_usuario (FK → usuarios, UNIQUE, nullable)
├── nombre_completo
├── telefono
├── disponible
├── ubicacion_actual (GEOGRAPHY POINT)
└── fecha_creacion

incidentes
├── id_incidente (PK)
├── id_usuario_cliente (FK → usuarios)
├── id_vehiculo (FK → vehiculos, nullable)
├── ubicacion (GEOGRAPHY POINT)
├── estado (ENUM: PENDIENTE, EN_PROCESO_IA, CLASIFICADO, ASIGNADO, EN_CAMINO, EN_PROCESO, ATENDIDO, CANCELADO, INCIERTO)
├── prioridad (ENUM: BAJA, MEDIA, ALTA)
├── clasificacion (ENUM: BATERIA, LLANTA, CHOQUE, MOTOR, OTROS, INCIERTO)
├── resumen_ia
├── tiempo_estimado_llegada_minutos
├── id_local (nullable, para offline sync)
├── id_tenant (FK → tenants)
└── fecha_creacion

evidencias
├── id_evidencia (PK)
├── id_incidente (FK → incidentes, CASCADE)
├── tipo (ENUM: IMAGEN, AUDIO, TEXTO)
├── url_archivo
├── clave_archivo
├── texto_transcrito
├── analisis_ia
└── fecha_creacion

historial_incidentes
├── id_historial (PK)
├── id_incidente (FK → incidentes, CASCADE)
├── estado
├── notas
├── id_usuario_cambio (FK → usuarios)
└── fecha_cambio

asignaciones
├── id_asignacion (PK)
├── id_incidente (FK → incidentes, UNIQUE)
├── id_taller (FK → talleres)
├── id_tecnico (FK → tecnicos)
├── fecha_asignacion
├── fecha_aceptacion
├── fecha_rechazo
├── motivo_rechazo
├── monto_cotizado
├── tiempo_estimado_reparacion
├── cotizacion_aceptada
└── notas_cotizacion

pagos
├── id_pago (PK)
├── id_incidente (FK → incidentes, UNIQUE)
├── id_usuario_cliente (FK → usuarios)
├── id_taller (FK → talleres)
├── id_asignacion (FK → asignaciones)
├── monto
├── comision_plataforma
├── estado (ENUM: NO_PAGO, PENDIENTE, PAGADO, RECHAZADO)
├── metodo_pago
├── id_transaccion
├── comprobante_url
├── comprobante_clave
├── notas_cliente
├── id_usuario_confirmo (FK → usuarios)
├── id_tenant (FK → tenants)
└── fecha_creacion

bitacora
├── id_bitacora (PK)
├── id_usuario (FK → usuarios)
├── id_tenant (FK → tenants)
├── accion
├── entidad
├── id_entidad
├── descripcion
├── ip
└── fecha_creacion
```

## Relaciones

```
tenants ──< usuarios
tenants ──< talleres
tenants ──< incidentes
tenants ──< pagos
tenants ──< bitacora

usuarios ──< vehiculos
usuarios ──< talleres (1:1)
usuarios ──< tecnicos (1:1)
usuarios ──< incidentes
usuarios ──< bitacora

talleres ──< tecnicos
talleres ──< asignaciones
talleres ──< pagos

tecnicos ──< asignaciones

incidentes ──< evidencias
incidentes ──< historial_incidentes
incidentes ──< asignaciones (1:1)
incidentes ──< pagos (1:1)
```

## Documentos Relacionados

- [[Usuarios y Roles]]
- [[Incidentes]]
- [[Talleres y Técnicos]]
- [[Asignaciones]]
- [[Pagos]]
- [[Bitácora]]
