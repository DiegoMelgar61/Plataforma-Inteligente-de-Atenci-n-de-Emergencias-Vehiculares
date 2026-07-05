---
titulo: "Talleres y Técnicos"
tipo: Modelo de Datos
fecha: 2026-07-03
tags: [talleres, tecnicos, modelo]
---

# Talleres y Técnicos

## Tabla `talleres`

| Campo | Tipo | Constraints |
|-------|------|------------|
| `id_taller` | INTEGER | PK, autoincrement |
| `id_usuario` | INTEGER | FK → usuarios (CASCADE), UNIQUE |
| `nombre_negocio` | VARCHAR(255) | NOT NULL |
| `nit` | VARCHAR(50) | UNIQUE |
| `direccion` | TEXT | nullable |
| `tasa_comision` | DECIMAL(5,2) | default 10.00 |
| `latitud` | DECIMAL(10,7) | nullable |
| `longitud` | DECIMAL(10,7) | nullable |
| `activo` | BOOLEAN | default TRUE |
| `id_tenant` | INTEGER | FK → tenants, nullable |
| `fecha_creacion` | TIMESTAMP | server_default NOW() |
| `fecha_actualizacion` | TIMESTAMP | onupdate NOW() |

## Tabla `tecnicos`

| Campo | Tipo | Constraints |
|-------|------|------------|
| `id_tecnico` | INTEGER | PK, autoincrement |
| `id_taller` | INTEGER | FK → talleres (CASCADE), NOT NULL |
| `id_usuario` | INTEGER | FK → usuarios (SET NULL), UNIQUE, nullable |
| `nombre_completo` | VARCHAR(255) | NOT NULL |
| `telefono` | VARCHAR(20) | nullable |
| `disponible` | BOOLEAN | default TRUE |
| `ubicacion_actual` | GEOGRAPHY(POINT, 4326) | nullable |
| `fecha_creacion` | TIMESTAMP | server_default NOW() |
| `fecha_actualizacion` | TIMESTAMP | onupdate NOW() |

## Modelo SQLAlchemy

```python
class TALLERES(Base):
    __tablename__ = "talleres"

    ID_TALLER = Column("id_taller", Integer, primary_key=True)
    ID_USUARIO = Column("id_usuario", Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), unique=True)
    NOMBRE_NEGOCIO = Column("nombre_negocio", String(255), nullable=False)
    NIT = Column("nit", String(50), unique=True)
    TASA_COMISION = Column("tasa_comision", DECIMAL(5, 2), default=10.00)

class TECNICOS(Base):
    __tablename__ = "tecnicos"

    ID_TECNICO = Column("id_tecnico", Integer, primary_key=True)
    ID_TALLER = Column("id_taller", Integer, ForeignKey("talleres.id_taller", ondelete="CASCADE"), nullable=False)
    ID_USUARIO = Column("id_usuario", Integer, ForeignKey("usuarios.id_usuario", ondelete="SET NULL"), unique=True)
    DISPONIBLE = Column("disponible", Boolean, default=True)
    UBICACION_ACTUAL = Column("ubicacion_actual", Geography(geometry_type='POINT', srid=4326))
```

## Relación Taller-Técnico

```
TALLER (1) ──── (N) TECNICOS
   │                    │
   │                    └── Puede tener cuenta de login (ID_USUARIO)
   └── Vinculado a un USUARIO (duño)
```

## Creación de Técnico con Login

```
POST /tecnicos/crear-con-usuario
{
  "correo_electronico": "tecnico@taller.com",
  "contrasena": "password123",
  "nombre_completo": "Juan Técnico",
  "telefono": "70123456",
  "id_taller": 1
}
```

Crea atómicamente:
1. USUARIO con rol=TECNICO
2. Registro TECNICOS vinculado al usuario

## Documentos Relacionados

- [[Diagrama ER]]
- [[Asignación de Técnico]]
