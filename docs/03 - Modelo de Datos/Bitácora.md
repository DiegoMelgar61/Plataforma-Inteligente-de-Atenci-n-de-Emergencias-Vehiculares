---
titulo: "Bitácora de Auditoría"
tipo: Modelo de Datos
fecha: 2026-07-03
tags: [bitacora, auditoria, log]
---

# Bitácora de Auditoría

## Tabla `bitacora`

| Campo | Tipo | Constraints |
|-------|------|------------|
| `id_bitacora` | INTEGER | PK, autoincrement |
| `id_usuario` | INTEGER | FK → usuarios (SET NULL), nullable |
| `id_tenant` | INTEGER | FK → tenants, nullable |
| `accion` | VARCHAR(100) | NOT NULL |
| `entidad` | VARCHAR(50) | nullable |
| `id_entidad` | VARCHAR(64) | nullable |
| `descripcion` | TEXT | nullable |
| `ip` | VARCHAR(64) | nullable |
| `fecha_creacion` | TIMESTAMP | server_default NOW() |

## Modelo SQLAlchemy

```python
class BITACORA(Base):
    __tablename__ = "bitacora"

    ID_BITACORA = Column("id_bitacora", Integer, primary_key=True)
    ID_USUARIO = Column("id_usuario", Integer, ForeignKey("usuarios.id_usuario", ondelete="SET NULL"))
    ACCION = Column("accion", String(100), nullable=False)
    ENTIDAD = Column("entidad", String(50))
    ID_ENTIDAD = Column("id_entidad", String(64))
    DESCRIPCION = Column("descripcion", Text)
    IP = Column("ip", String(64))
```

## Acciones Registradas

| Acción | Descripción |
|--------|------------|
| `USUARIO_REGISTRADO` | Nuevo usuario registrado |
| `LOGIN` | Inicio de sesión |
| `INCIDENTE_REPORTADO` | Cliente reportó incidente |
| `TALLER_SELECCIONADO` | Cliente eligió taller |
| `ESTADO_ACTUALIZADO` | Técnico cambió estado |
| `SERVICIO_CANCELADO` | Cliente canceló servicio |
| `PAGO_CONFIRMADO` | Taller confirmó pago |
| `PAGO_RECHAZADO` | Taller rechazó comprobante |

## Uso

```python
from app.modules.bitacora import service as bitacora_service

bitacora_service.registrar(
    "LOGIN",
    f"Inicio de sesión de {correo}",
    id_usuario=usuario.ID_USUARIO,
    id_tenant=id_tenant,
    entidad="USUARIO",
    id_entidad=usuario.ID_USUARIO,
    ip=request.client.host,
)
```

## Documentos Relacionados

- [[Diagrama ER]]
- [[Resumen del Proyecto]]
