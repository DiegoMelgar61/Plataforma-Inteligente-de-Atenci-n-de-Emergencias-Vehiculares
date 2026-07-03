# Plataforma Inteligente de Atención de Emergencias Vehiculares

Monorepo para coordinar emergencias vehiculares: reporte de incidentes, evidencias, talleres, técnicos, asignaciones, pagos, procesamiento con IA y notificaciones en tiempo real.

## Estructura

| Carpeta | Rol |
|--------|-----|
| `backend/` | API FastAPI, PostgreSQL/PostGIS, Alembic, JWT, IA y WebSockets. |
| `frontend/` | Panel Angular para talleres y administración. |
| `mobile/` | Cliente Flutter para usuarios y técnicos. |

## Backend Con Docker

1. Crear el archivo local de variables:

   ```bash
   cp backend/.env.example backend/.env
   ```

2. Ajustar los valores sensibles en `backend/.env`.

3. Levantar servicios:

   ```bash
   docker compose up --build
   ```

4. Verificar:

   ```bash
   curl http://localhost:8000/health
   ```

API docs: `http://localhost:8000/docs`

## Desarrollo Local

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm start
```

Frontend local: `http://localhost:4200`

## Notas De Seguridad

- No commitear `.env`; usar `backend/.env.example` como plantilla.
- Los WebSockets requieren JWT por query string: `?token=<jwt>`.
- El registro público crea usuarios `CLIENTE`; roles privilegiados deben gestionarse desde endpoints protegidos.
