---
titulo: "Asignaciones"
tipo: Modelo de Datos
fecha: 2026-07-03
tags: [asignaciones, cotizaciones, modelo]
---

# Asignaciones

## Tabla `asignaciones`

| Campo | Tipo | Constraints |
|-------|------|------------|
| `id_asignacion` | INTEGER | PK, autoincrement |
| `id_incidente` | INTEGER | FK → incidentes, UNIQUE |
| `id_taller` | INTEGER | FK → talleres |
| `id_tecnico` | INTEGER | FK → tecnicos |
| `fecha_asignacion` | TIMESTAMP | server_default NOW() |
| `fecha_aceptacion` | TIMESTAMP | nullable |
| `fecha_rechazo` | TIMESTAMP | nullable |
| `motivo_rechazo` | TEXT | nullable |
| `monto_cotizado` | DECIMAL(10,2) | nullable |
| `tiempo_estimado_reparacion` | INTEGER | nullable |
| `cotizacion_aceptada` | BOOLEAN | nullable |
| `notas_cotizacion` | TEXT | nullable |

## Modelo SQLAlchemy

```python
class ASIGNACIONES(Base):
    __tablename__ = "asignaciones"

    ID_ASIGNACION = Column("id_asignacion", Integer, primary_key=True)
    ID_INCIDENTE = Column("id_incidente", Integer, ForeignKey("incidentes.id_incidente"), unique=True)
    ID_TALLER = Column("id_taller", Integer, ForeignKey("talleres.id_taller"))
    ID_TECNICO = Column("id_tecnico", Integer, ForeignKey("tecnicos.id_tecnico"))
    MONTO_COTIZADO = Column("monto_cotizado", DECIMAL(10, 2), nullable=True)
    COTIZACION_ACEPTADA = Column("cotizacion_aceptada", Boolean, nullable=True)
```

## Flujo de Asignación

```
1. Cliente reporta incidente → PENDIENTE
2. Pipeline IA procesa → CLASIFICADO
3. Cliente ve cotizaciones de talleres cercanos
4. Cliente selecciona taller → ASIGNADO
5. Taller propone cotización
6. Cliente acepta → EN_CAMINO
7. Técnico avanza: EN_CAMINO → EN_PROCESO → ATENDIDO
```

## Asignación Automática por GPS

```python
# assignments/service.py
def asignar_taller_automaticamente(db, id_incidente):
    # 1. Buscar talleres cercanos con PostGIS
    # 2. Verificar técnicos disponibles
    # 3. Seleccionar el más cercano
    # 4. Crear ASIGNACIONES
    # 5. Marcar técnico como no disponible
    # 6. Actualizar estado a ASIGNADO
```

## Cotizaciones

### Proponer (Taller)
```
POST /assignments/incidents/{id}/cotizacion
{
  "monto_cotizado": 150.00,
  "tiempo_estimado_reparacion": 120,
  "notas_cotizacion": "Reparación estimada"
}
```

### Responder (Cliente)
```
POST /assignments/incidents/{id}/cotizacion/respuesta
{
  "aceptada": true,
  "motivo_rechazo": null
}
```

- **Aceptar**: Estado → EN_CAMINO
- **Rechazar**: Estado → CLASIFICADO, liberar técnico, eliminar asignación

## Documentos Relacionados

- [[Diagrama ER]]
- [[Asignación de Técnico]]
- [[Incidentes]]
