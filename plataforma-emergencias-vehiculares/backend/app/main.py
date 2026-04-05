import logging
from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.presentation.api.v1.routers.auth import router as auth_router
from app.presentation.api.v1.routers.users import router as users_router
from app.presentation.api.v1.routers.vehicles import router as vehicles_router
from app.presentation.api.v1.routers.workshops import router as workshops_router
from app.presentation.api.v1.routers.technicians import router as technicians_router
from app.presentation.api.v1.routers.ai_processing import router as ai_processing_router
from app.presentation.api.v1.routers.incidents import router as incidents_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("%s — arranque (%s)", settings.APP_NAME, settings.ENVIRONMENT)
    uploads = Path(settings.UPLOADS_DIR)
    uploads.mkdir(parents=True, exist_ok=True)
    (uploads / "evidencias").mkdir(parents=True, exist_ok=True)
    yield
    logger.info("Aplicación detenida")


app = FastAPI(
    title=settings.APP_NAME,
    description="Plataforma inteligente de atención de emergencias vehiculares",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(vehicles_router)
app.include_router(workshops_router)
app.include_router(technicians_router)
app.include_router(ai_processing_router)
app.include_router(incidents_router)

_evidencias_dir = Path(settings.UPLOADS_DIR) / "evidencias"
_evidencias_dir.mkdir(parents=True, exist_ok=True)
app.mount(
    settings.EVIDENCIAS_URL_PREFIX,
    StaticFiles(directory=str(_evidencias_dir)),
    name="evidencias_estaticas",
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}
