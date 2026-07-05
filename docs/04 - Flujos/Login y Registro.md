---
titulo: "Flujo de Login y Registro"
tipo: Flujo
fecha: 2026-07-03
tags: [flujo, login, registro, auth]
---

# Flujo de Login y Registro

## Registro

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Cliente │────▶│ Frontend│────▶│ Backend │────▶│   DB    │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
     │               │               │               │
     │  1. POST /auth/register       │               │
     │  {correo, pass, nombre}       │               │
     │──────────────────────────────▶│               │
     │                               │  2. Hash password
     │                               │──────────────▶│
     │                               │  3. Crear usuario
     │                               │  rol=CLIENTE
     │                               │──────────────▶│
     │                               │  4. Generar JWT
     │  5. {access_token}            │               │
     │◀──────────────────────────────│               │
```

## Login

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  Usuario│────▶│ Frontend│────▶│ Backend │────▶│   DB    │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
     │               │               │               │
     │  1. POST /auth/login          │               │
     │  {correo, contrasena}         │               │
     │──────────────────────────────▶│               │
     │                               │  2. Buscar usuario
     │                               │──────────────▶│
     │                               │  3. Verificar bcrypt
     │                               │◀──────────────│
     │                               │  4. Generar JWT
     │  5. {access_token}            │               │
     │◀──────────────────────────────│               │
     │                               │               │
     │  6. Guardar token en storage  │               │
     │  7. Navegar a dashboard       │               │
```

## JWT Claims

```json
{
  "sub": "usuario@correo.com",
  "rol": "CLIENTE",
  "id_tenant": "1",
  "exp": 1234567890
}
```

## Protección de Rutas

```
Frontend: authGuard verifica JWT antes de acceder a rutas protegidas
Backend: Dependencies (get_current_user) verifican JWT en cada request
```

## Documentos Relacionados

- [[Autenticación]]
- [[Usuarios y Roles]]
- [[Endpoints]]
