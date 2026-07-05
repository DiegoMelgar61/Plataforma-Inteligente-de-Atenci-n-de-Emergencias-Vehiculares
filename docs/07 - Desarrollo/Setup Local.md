---
titulo: "Setup Local"
tipo: Desarrollo
fecha: 2026-07-03
tags: [setup, desarrollo, local, guía]
---

# Setup Local

## Prerrequisitos

- Python 3.11+
- Node.js 18+
- Flutter 3.x
- Docker + Docker Compose
- Git

## Backend

```bash
cd backend

# Crear virtualenv
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# Aplicar migraciones
alembic upgrade head

# Ejecutar servidor
uvicorn app.main:app --reload
```

API docs: `http://localhost:8000/docs`
Health check: `http://localhost:8000/health`

## Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Ejecutar en desarrollo
npm start
```

Frontend: `http://localhost:4200`

## Mobile

```bash
cd mobile

# Instalar dependencias
flutter pub get

# Ejecutar en emulador
flutter run
```

## Docker (alternativa)

```bash
# Desde la raíz del proyecto
docker compose up --build
```

Esto levanta:
- Backend en `http://localhost:8000`
- PostgreSQL en `http://localhost:5432`

## Documentos Relacionados

- [[Stack Tecnológico]]
- [[Docker]]
- [[Environment Variables]]
