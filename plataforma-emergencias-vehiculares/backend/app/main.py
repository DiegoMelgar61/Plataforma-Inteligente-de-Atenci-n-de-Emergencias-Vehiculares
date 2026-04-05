import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("%s — arranque (%s)", settings.APP_NAME, settings.ENVIRONMENT)
    yield
    logger.info("Aplicación detenida")


app = FastAPI(
    title=settings.APP_NAME,
    description="Plataforma inteligente de atención de emergencias vehiculares",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}

from app.presentation.api.v1.routers.auth import router as auth_router

app.include_router(auth_router)