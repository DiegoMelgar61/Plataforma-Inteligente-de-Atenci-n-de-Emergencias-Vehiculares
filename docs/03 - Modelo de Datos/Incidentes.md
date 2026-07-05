---
titulo: "Incidentes y Evidencias"
tipo: Modelo de Datos
fecha: 2026-07-03
tags: [incidentes, evidencias, modelo, postgis]
---

# Incidentes y Evidencias

## Tabla `incidentes`

| Campo | Tipo | Constraints |
|-------|------|------------|
| `id_incidente` | INTEGER | PK, autoincrement |
| `id_usuario_cliente` | INTEGER | FK → usuarios, NOT NULL |
| `id_vehiculo` | INTEGER | FK → vehiculos, nullable |
| `ubicacion` | GEOGRAPHY(POINT, 4326) | NOT NULL |
| `estado` | ENUM | default 'PENDIENTE' |
| `prioridad` | ENUM | default 'MEDIA' |
| `clasificacion` | ENUM | default 'OTROS' |
| `resumen_ia` | TEXT | nullable |
| `tiempo_estimado_llegada_minutos` | INTEGER | nullable |
| `id_local` | VARCHAR(36) | nullable (offline sync) |
| `id_tenant` | INTEGER | FK → tenants, nullable |
| `fecha_creacion` | TIMESTAMP | server_default NOW() |
| `fecha_actualizacion` | TIMESTAMP | onupdate NOW() |

## ENUMs

### `estado_incidente_enum`

```
PENDIENTE → EN_PROCESO_IA → CLASIFICADO → ASIGNADO → EN_CAMINO → EN_PROCESO → ATENDIDO
                                                    ↘ CANCELADO
                                                                   ↘ INCIERTO
```

### `prioridad_enum`

`BAJA` | `MEDIA` | `ALTA`

### `clasificacion_enum`

`BATERIA` | `LLANTA` | `CHOQUE` | `MOTOR` | `OTROS` | `INCIERTO`

## Tabla `evidencias`

| Campo | Tipo | Constraints |
|-------|------|------------|
| `id_evidencia` | INTEGER | PK, autoincrement |
| `id_incidente` | INTEGER | FK → incidentes (CASCADE), NOT NULL |
| `tipo` | ENUM | NOT NULL |
| `url_archivo` | TEXT | NOT NULL |
| `clave_archivo` | TEXT | nullable |
| `texto_transcrito` | TEXT | nullable |
| `analisis_ia` | TEXT | nullable |
| `fecha_creacion` | TIMESTAMP | server_default NOW() |

### `tipo_evidencia_enum`

`IMAGEN` | `AUDIO` | `TEXTO`

## Tabla `historial_incidentes`

| Campo | Tipo | Constraints |
|-------|------|------------|
| `id_historial` | INTEGER | PK, autoincrement |
| `id_incidente` | INTEGER | FK → incidentes (CASCADE), NOT NULL |
| `estado` | ENUM | NOT NULL |
| `notas` | TEXT | nullable |
| `id_usuario_cambio` | INTEGER | FK → usuarios, nullable |
| `fecha_cambio` | TIMESTAMP | server_default NOW() |

## Modelo SQLAlchemy

```python
class INCIDENTES(Base):
    __tablename__ = "incidentes"

    ID_INCIDENTE = Column("id_incidente", Integer, primary_key=True)
    ID_USUARIO_CLIENTE = Column("id_usuario_cliente", Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    UBICACION = Column("ubicacion", Geography(geometry_type='POINT', srid=4326), nullable=False)
    ESTADO = Column("estado", EstadoIncidenteEnum, default="PENDIENTE")
    PRIORIDAD = Column("prioridad", PrioridadEnum, default="MEDIA")
    CLASIFICACION = Column("clasificacion", ClasificacionEnum, default="OTROS")
    RESUMEN_IA = Column("resumen_ia", Text)
```

## Flujo de Reporte

```
1. Cliente envía POST /incidents/report (multipart: lat, lng, imagenes, audio, texto)
2. Crear INCIDENTES con estado PENDIENTE
3. Guardar archivos en UPLOADS_DIR/evidencias/{id}/
4. Crear registros EVIDENCIAS con URL temporal
5. Ejecutar pipeline IA (async)
6. Broadcast notificación por WebSocket
```

## Documentos Relacionados

- [[Diagrama ER]]
- [[Reporte de Incidente]]
- [[Asignaciones]]
