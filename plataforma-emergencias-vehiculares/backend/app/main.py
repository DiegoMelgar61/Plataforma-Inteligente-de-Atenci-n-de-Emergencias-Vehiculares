import logging
from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.presentation.api.v1.routers.auth import router as auth_router
from app.presentation.api.v1.routers.users import router as users_router
from app.presentation.api.v1.routers.vehicles import router as vehicles_router
from app.presentation.api.v1.routers.workshops import router as workshops_router
from app.presentation.api.v1.routers.technicians import router as technicians_router
from app.presentation.api.v1.routers.ai_processing import router as ai_processing_router
from app.presentation.api.v1.routers.incidents import router as incidents_router
from app.presentation.api.v1.routers.assignments import router as assignments_router
from app.presentation.api.v1.routers.notifications import router as notifications_router
from app.presentation.api.v1.routers.payments import router as payments_router

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

ALLOWED_ORIGINS = [
    # Vercel production
    "https://plataforma-inteligente-de-atenci-n.vercel.app",
    "https://plataforma-inteligente-de-atenci-n-de-vercel.app",
    "https://www.plataforma-inteligente-de-atenci-n.vercel.app",
    # Local development
    "http://localhost:4200",
    "http://localhost:4201",
    "http://127.0.0.1:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    # Cubre cualquier preview/deploy de Vercel con este prefijo de proyecto
    allow_origin_regex=r"https://plataforma-inteligente-de-atenci-n[^.]*\.(vercel\.app|vercel\.app)",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
        "X-Requested-With",
        "Upgrade",
        "Connection",
        "Sec-WebSocket-Key",
        "Sec-WebSocket-Version",
        "Sec-WebSocket-Extensions",
        "Sec-WebSocket-Protocol",
    ],
    expose_headers=["*"],
    max_age=3600,
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(vehicles_router)
app.include_router(workshops_router)
app.include_router(technicians_router)
app.include_router(ai_processing_router)
app.include_router(incidents_router)
app.include_router(assignments_router)
app.include_router(notifications_router)
app.include_router(payments_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}


_evidencias_dir = Path(settings.UPLOADS_DIR) / "evidencias"
_evidencias_dir.mkdir(parents=True, exist_ok=True)
app.mount(
    settings.EVIDENCIAS_URL_PREFIX,
    StaticFiles(directory=str(_evidencias_dir)),
    name="evidencias_estaticas",
)
