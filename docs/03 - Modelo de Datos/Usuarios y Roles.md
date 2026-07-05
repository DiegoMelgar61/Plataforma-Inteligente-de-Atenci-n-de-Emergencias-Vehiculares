---
titulo: "Usuarios y Roles"
tipo: Modelo de Datos
fecha: 2026-07-03
tags: [usuarios, roles, auth, modelo]
---

# Usuarios y Roles

## Tabla `usuarios`

| Campo | Tipo | Constraints |
|-------|------|------------|
| `id_usuario` | INTEGER | PK, autoincrement |
| `correo_electronico` | VARCHAR(255) | UNIQUE, NOT NULL |
| `hash_contrasena` | TEXT | NOT NULL |
| `nombre_completo` | VARCHAR(255) | NOT NULL |
| `telefono` | VARCHAR(20) | nullable |
| `rol` | ENUM | NOT NULL |
| `activo` | BOOLEAN | default TRUE |
| `id_tenant` | INTEGER | FK → tenants, nullable |
| `fecha_creacion` | TIMESTAMP | server_default NOW() |
| `fecha_actualizacion` | TIMESTAMP | onupdate NOW() |
| `fecha_eliminacion` | TIMESTAMP | nullable (soft delete) |

## ENUM `rol_enum`

| Valor | Descripción |
|-------|------------|
| `CLIENTE` | Usuario que reporta incidentes |
| `TALLER` | Dueño de negocio mecánico |
| `ADMIN` | Administrador de plataforma |
| `TECNICO` | Técnico del taller |

## Tabla `clientes`

Extensión de `usuarios` para clientes. Solo tiene `id_usuario` como PK y FK.

## Modelo SQLAlchemy

```python
class USUARIOS(Base):
    __tablename__ = "usuarios"

    ID_USUARIO = Column("id_usuario", Integer, primary_key=True)
    CORREO_ELECTRONICO = Column("correo_electronico", String(255), unique=True, nullable=False)
    HASH_CONTRASENA = Column("hash_contrasena", Text, nullable=False)
    NOMBRE_COMPLETO = Column("nombre_completo", String(255), nullable=False)
    TELEFONO = Column("telefono", String(20))
    ROL = Column("rol", Enum('CLIENTE', 'TALLER', 'ADMIN', 'TECNICO', name='rol_enum'), nullable=False)
    ACTIVO = Column("activo", Boolean, default=True)
    ID_TENANT = Column("id_tenant", Integer, ForeignKey("tenants.id_tenant"), nullable=True)
```

## Flujo de Registro

```
1. POST /auth/register
2. Crear USUARIOS con rol=CLIENTE
3. Asignar TENANT_DEFAULT_ID
4. Generar JWT con claims: sub, rol, id_tenant
5. Retornar access_token
```

## Documentos Relacionados

- [[Diagrama ER]]
- [[Autenticación]]
- [[Resumen del Proyecto]]
