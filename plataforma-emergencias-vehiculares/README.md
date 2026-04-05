# Plataforma Inteligente de Atención de Emergencias Vehiculares

Plataforma para coordinar emergencias vehiculares: gestión de incidentes, talleres, técnicos, evidencias, asignaciones, pagos e integración con procesamiento asistido por IA y notificaciones. Este repositorio incluye el **backend** en FastAPI; las carpetas `web/` y `mobile/` están reservadas para futuros clientes.

## Requisitos

- [Docker](https://docs.docker.com/get-docker/) y Docker Compose

## Ejecutar con Docker Compose

1. Copia las variables de entorno del backend (si aún no existe tu `.env`):

   ```bash
   cp backend/.env.example backend/.env
   ```

2. Desde la raíz del proyecto (`plataforma-emergencias-vehiculares`):

   ```bash
   docker compose up --build
   ```

3. API: [http://localhost:8000](http://localhost:8000)  
   Documentación interactiva: [http://localhost:8000/docs](http://localhost:8000/docs)  
   Salud del servicio: [http://localhost:8000/health](http://localhost:8000/health)

Para detener los contenedores: `docker compose down`. Para eliminar también el volumen de PostgreSQL: `docker compose down -v`.
