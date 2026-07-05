---
titulo: "Pagos"
tipo: Modelo de Datos
fecha: 2026-07-03
tags: [pagos, comprobantes, modelo]
---

# Pagos

## Tabla `pagos`

| Campo | Tipo | Constraints |
|-------|------|------------|
| `id_pago` | INTEGER | PK, autoincrement |
| `id_incidente` | INTEGER | FK → incidentes, UNIQUE |
| `id_usuario_cliente` | INTEGER | FK → usuarios |
| `id_taller` | INTEGER | FK → talleres |
| `id_asignacion` | INTEGER | FK → asignaciones |
| `monto` | DECIMAL(10,2) | NOT NULL |
| `comision_plataforma` | DECIMAL(10,2) | NOT NULL |
| `estado` | ENUM | default 'NO_PAGO' |
| `metodo_pago` | VARCHAR(50) | nullable |
| `id_transaccion` | VARCHAR(255) | nullable |
| `comprobante_url` | TEXT | nullable |
| `comprobante_clave` | TEXT | nullable |
| `notas_cliente` | TEXT | nullable |
| `id_usuario_confirmo` | INTEGER | FK → usuarios, nullable |
| `id_tenant` | INTEGER | FK → tenants, nullable |
| `fecha_creacion` | TIMESTAMP | server_default NOW() |
| `fecha_marcado_pago` | TIMESTAMP | nullable |
| `fecha_confirmacion` | TIMESTAMP | nullable |
| `fecha_rechazo` | TIMESTAMP | nullable |
| `motivo_rechazo` | TEXT | nullable |

## ENUM `estado_pago_enum`

| Valor | Descripción |
|-------|------------|
| `NO_PAGO` | Sin pago generado |
| `PENDIENTE` | Pago creado, esperando comprobante |
| `PAGADO` | Comprobante subido, esperando confirmación |
| `RECHAZADO` | Comprobante rechazado |

## Modelo SQLAlchemy

```python
class PAGOS(Base):
    __tablename__ = "pagos"

    ID_PAGO = Column("id_pago", Integer, primary_key=True)
    ID_INCIDENTE = Column("id_incidente", Integer, ForeignKey("incidentes.id_incidente"), unique=True)
    MONTO = Column("monto", DECIMAL(10, 2), nullable=False)
    COMISION_PLATAFORMA = Column("comision_plataforma", DECIMAL(10, 2), nullable=False)
    ESTADO = Column("estado", EstadoPagoEnum, default="NO_PAGO")
```

## Flujo de Pago

```
1. Incidente llega a ATENDIDO
2. Backend crea PAGO con estado PENDIENTE
3. Cliente sube comprobante → POST /payments/{id}/mark-paid
4. Estado cambia a PAGADO
5. Taller/Admin confirma → POST /payments/{id}/confirm
6. Estado cambia a PAGADO (confirmado)
```

## Comisiones

- `tasa_comision`: Porcentaje del taller (default 10%)
- `comision_plataforma`: Calculada al crear el pago

## Multas por Cancelación

Si el cliente cancela con técnico en camino:
- Multa del 20% del monto cotizado
- Cliente no puede solicitar nuevos servicios hasta pagar

## Documentos Relacionados

- [[Diagrama ER]]
- [[Flujo de Pago]]
