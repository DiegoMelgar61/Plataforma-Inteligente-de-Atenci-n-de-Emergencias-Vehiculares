---
titulo: "Convenciones de Código"
tipo: Desarrollo
fecha: 2026-07-05
tags: [convenciones, estilo, naming, code-style]
---

# Convenciones de Código

## Backend (Python)

### Naming

| Tipo | Convención | Ejemplo |
|------|-----------|---------|
| Clases | UPPER_CASE | `USUARIOS`, `INCIDENTES` |
| Funciones | snake_case | `obtener_usuario()` |
| Variables | snake_case | `id_usuario` |
| Constantes | UPPER_CASE | `TENANT_DEFAULT_ID` |
| Enums | UPPER_CASE | `CLIENTE`, `PENDIENTE` |

### Archivos

```
models.py      ← Modelos SQLAlchemy (UPPER_CASE classes)
schemas.py     ← Pydantic schemas (PascalCase)
router.py      ← Endpoints FastAPI (snake_case)
service.py     ← Lógica de negocio (snake_case)
```

### Importaciones

```python
# FastAPI
from fastapi import APIRouter, Depends, HTTPException

# SQLAlchemy
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

# Módulos internos
from app.core.database import get_db
from app.modules.users.models import USUARIOS
```

## Frontend (TypeScript)

### Naming

| Tipo | Convención | Ejemplo |
|------|-----------|---------|
| Componentes | PascalCase | `DashboardComponent` |
| Servicios | PascalCase | `AuthService` |
| Interfaces | PascalCase | `UserProfile` |
| Variables | camelCase | `currentUser` |
| Funciones | camelCase | `loginUser()` |

### Archivos

```
*.component.ts      ← Componentes
*.service.ts        ← Servicios
*.guard.ts          ← Guards
*.interceptor.ts    ← Interceptors
*.model.ts          ← Modelos
```

## Mobile (Dart)

### Naming

| Tipo | Convención | Ejemplo |
|------|-----------|---------|
| Clases | PascalCase | `IncidenteModel` |
| Variables | camelCase | `currentUser` |
| Funciones | camelCase | `fetchIncidents()` |
| Constantes | camelCase | `apiBaseUrl` |

### Archivos

```
*_models.dart       ← Modelos
*_repository.dart   ← Repositorios
*_provider.dart     ← Providers
*_screen.dart       ← Pantallas
```

## Git

### Workflow

| Paso | Regla |
|------|-------|
| Desarrollo | Todo cambio nuevo se implementa en `dev` |
| Validación | Compilar/testear en `dev` antes de integrar |
| Producción | `main` solo recibe cambios por Pull Request |
| Documentación | El vault `docs/` se versiona junto al código |
| Config local | `.vscode/` no se versiona |

Flujo estándar:

```bash
git checkout dev
# implementar cambios
# verificar backend/frontend/mobile según corresponda
git add <archivos>
git commit -m "tipo(scope): descripcion"
git push origin dev
# abrir PR dev -> main
```

### Commits

```
tipo(alcance): descripción corta

tipo: feat, fix, refactor, chore, docs
alcance: backend, frontend, mobile, api
```

### Branches

```
dev         ← Desarrollo
main        ← Producción
feature/*   ← Features
fix/*       ← Bugs
reorg/*     ← Refactoring
```

## Documentos Relacionados

- [[Stack Tecnológico]]
- [[Setup Local]]
