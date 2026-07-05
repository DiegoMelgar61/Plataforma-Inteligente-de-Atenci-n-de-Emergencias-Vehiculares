---
titulo: "Variables de Entorno"
tipo: Infraestructura
fecha: 2026-07-03
tags: [env, config, variables, secrets]
---

# Variables de Entorno

## Backend (`.env`)

```bash
# App
APP_NAME="Plataforma de Emergencias"
ENVIRONMENT="development"

# Database (Supabase)
DATABASE_URL="postgresql://user:password@host:5432/dbname"

# JWT
SECRET_KEY="tu-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Uploads
UPLOADS_DIR="uploads"
EVIDENCIAS_URL_PREFIX="/static/evidencias"
COMPROBANTES_URL_PREFIX="/static/comprobantes"

# IA Service
AI_SERVICE_URL="https://ai-service.example.com"
AI_SERVICE_API_KEY="tu-api-key"
```

## Frontend

```typescript
// environments/environment.ts
export const environment = {
  production: false,
  apiBase: 'http://localhost:8000',
  wsBase: 'ws://localhost:8000',
};

// environments/environment.prod.ts
export const environment = {
  production: true,
  apiBase: 'https://api.plataforma-emergencias.com',
  wsBase: 'wss://api.plataforma-emergencias.com',
};
```

## Mobile

```dart
// lib/core/config.dart
class AppConfig {
  static const String apiBase = 'http://10.0.2.2:8000'; // Android emulator
  static const String wsBase = 'ws://10.0.2.2:8000';
}
```

## .gitignore

```
# Nunca commitear .env
.env
.env.local
.env.production
```

## Documentos Relacionados

- [[Docker]]
- [[Supabase]]
- [[Setup Local]]
