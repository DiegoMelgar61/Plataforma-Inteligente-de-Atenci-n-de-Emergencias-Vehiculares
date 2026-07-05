---
titulo: "Docker y Containerización"
tipo: Infraestructura
fecha: 2026-07-03
tags: [docker, container, infraestructura]
---

# Docker y Containerización

## Docker Compose

```yaml
services:
  postgres:
    image: postgis/postgis:16-3.5
    container_name: emergencias-postgres
    env_file:
      - ./backend/.env
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    container_name: emergencias-backend
    env_file:
      - ./backend/.env
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    volumes:
      - ./backend:/app
    command: sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

volumes:
  postgres_data:

networks:
  emergencias-net:
    driver: bridge
```

## Dockerfile Backend

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

## Comandos

```bash
# Levantar servicios
docker compose up --build

# Detener servicios
docker compose down

# Detener y eliminar volúmenes
docker compose down -v

# Ver logs
docker compose logs -f backend
```

## Documentos Relacionados

- [[Supabase]]
- [[Setup Local]]
- [[Environment Variables]]
