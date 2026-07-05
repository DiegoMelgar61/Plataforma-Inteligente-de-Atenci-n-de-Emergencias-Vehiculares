---
titulo: "Autenticación y Autorización"
tipo: API
fecha: 2026-07-03
tags: [auth, jwt, roles, seguridad]
---

# Autenticación y Autorización

## Flujo de Login

```
1. Cliente envía POST /auth/login {correo, contrasena}
2. Backend verifica credenciales (bcrypt)
3. Backend genera JWT con claims:
   - sub: correo electrónico
   - rol: CLIENTE | TALLER | ADMIN | TECNICO
   - id_tenant: ID del tenant
4. Retorna {"access_token": "...", "token_type": "bearer"}
```

## Estructura del JWT

```json
{
  "sub": "usuario@correo.com",
  "rol": "CLIENTE",
  "id_tenant": "1",
  "exp": 1234567890,
  "iat": 1234567890
}
```

## Uso del Token

```
Authorization: Bearer <access_token>
```

Para WebSocket:
```
ws://host/notifications/ws/incidents/{id}?token=<jwt>
```

## Roles y Permisos

| Rol | Permisos |
|-----|---------|
| `CLIENTE` | Reportar incidentes, ver sus pagos, responder cotizaciones |
| `TALLER` | Gestionar técnicos, cotizar, confirmar pagos, ver asignaciones |
| `TECNICO` | Actualizar estado de incidentes, enviar ubicación GPS |
| `ADMIN` | Acceso total a todo el sistema |

## Dependencias de Autorización

```python
# FastAPI dependencies
get_current_user         # Cualquier usuario autenticado
get_current_active_user  # Usuario activo y no eliminado
get_current_cliente      # Solo CLIENTE
get_current_taller       # Solo TALLER
get_current_admin        # Solo ADMIN
get_current_tecnico      # Solo TECNICO (retorna registro TECNICOS)
```

## Aislamiento por Tenant

```
CLIENTE → Solo sus propios incidentes/pagos
TALLER → Solo datos de su tenant (talleres, técnicos, incidentes del tenant)
TECNICO → Solo incidentes asignados a él
ADMIN → Acceso total (super-admin)
```

## Registro

```
POST /auth/register
{
  "correo": "nuevo@correo.com",
  "contrasena": "password123",
  "nombre_completo": "Juan Pérez",
  "telefono": "70123456"
}
```

- Rol siempre `CLIENTE`
- Tenant: `TENANT_DEFAULT_ID` (1)
- Retorna JWT directamente

## Documentos Relacionados

- [[Endpoints]]
- [[Usuarios y Roles]]
- [[Backend]]
