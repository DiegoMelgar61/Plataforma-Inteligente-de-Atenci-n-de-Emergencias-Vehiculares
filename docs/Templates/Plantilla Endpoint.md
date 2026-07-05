---
titulo: "{{NOMBRE_ENDPOINT}}"
tipo: Endpoint
fecha: {{FECHA}}
tags: [endpoint, {{MODULO}}]
---

# {{NOMBRE_ENDPOINT}}

## Información General

| Campo | Valor |
|-------|-------|
| Método | {{METODO}} |
| Ruta | {{RUTA}} |
| Descripción | {{DESCRIPCION}} |
| Auth | {{AUTH}} |
| Tags | {{TAGS}} |

## Request

### Headers

```
Authorization: Bearer <token>
Content-Type: application/json
```

### Body

```json
{
  "campo1": "valor1",
  "campo2": 123
}
```

### Parámetros

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|------------|
| `param1` | string | Sí | Descripción |
| `param2` | int | No | Descripción |

## Response

### 200 OK

```json
{
  "campo1": "valor1",
  "campo2": 123
}
```

### 400 Bad Request

```json
{
  "detail": "Error de validación"
}
```

### 401 Unauthorized

```json
{
  "detail": "Credenciales incorrectas"
}
```

## Ejemplo cURL

```bash
curl -X {{METODO}} \
  http://localhost:8000{{RUTA}} \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"campo1": "valor1"}'
```

## Notas

- {{NOTAS_ADICIONALES}}

## Documentos Relacionados

- [[Endpoints]]
- [[Autenticación]]
