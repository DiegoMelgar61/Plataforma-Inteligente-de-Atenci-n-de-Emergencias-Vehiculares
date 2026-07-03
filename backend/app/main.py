import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.config import settings
from app.presentation.api.v1.routers.auth import router as auth_router
from app.presentation.api.v1.routers.tenants import router as tenants_router
from app.presentation.api.v1.routers.users import router as users_router
from app.presentation.api.v1.routers.vehicles import router as vehicles_router
from app.presentation.api.v1.routers.workshops import router as workshops_router
from app.presentation.api.v1.routers.technicians import router as technicians_router
from app.presentation.api.v1.routers.ai_processing import router as ai_processing_router
from app.presentation.api.v1.routers.incidents import router as incidents_router
from app.presentation.api.v1.routers.assignments import router as assignments_router
from app.presentation.api.v1.routers.notifications import router as notifications_router
from app.presentation.api.v1.routers.payments import router as payments_router
from app.presentation.api.v1.routers.tracking import router as tracking_router
from app.presentation.api.v1.routers.stats import router as stats_router
from app.modules.bitacora.router import router as bitacora_router
from app.presentation.api.v1.routers.reports import router as reports_router
from app.modules.backups.router import router as backups_router
from app.modules.dashboards_ia.router import router as dashboards_ia_router

logger = logging.getLogger(__name__)


class WebSocketCORSBypass:
    """
    Strips the Origin header from WebSocket upgrade requests so that
    CORSMiddleware passes them through unconditionally.
    Browser security for WebSocket is enforced via tokens at the endpoint level.
    """
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "websocket":
            scope["headers"] = [
                (k, v) for k, v in scope.get("headers", [])
                if k.lower() != b"origin"
            ]
        await self.app(scope, receive, send)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("%s — arranque (%s)", settings.APP_NAME, settings.ENVIRONMENT)
    uploads = Path(settings.UPLOADS_DIR)
    uploads.mkdir(parents=True, exist_ok=True)
    (uploads / "evidencias").mkdir(parents=True, exist_ok=True)
    (uploads / "comprobantes").mkdir(parents=True, exist_ok=True)
    yield
    logger.info("Aplicación detenida")


app = FastAPI(
    title=settings.APP_NAME,
    description="Plataforma inteligente de atención de emergencias vehiculares",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS para peticiones HTTP ─────────────────────────────────────────────────
# Nota: allow_origins=["*"] + allow_credentials=True es combinación inválida;
# los browsers la rechazan. Se usan orígenes explícitos.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://plataforma-inteligente-de-atenci-n.vercel.app",
        "https://plataforma-inteligente-de-atenci-n-de-vercel.app",
        "http://localhost:4200",
        "http://localhost:4201",
        "http://127.0.0.1:4200",
    ],
    # Cubre cualquier preview/deploy de Vercel con este prefijo de proyecto
    allow_origin_regex=r"https://plataforma-inteligente-de-atenci-n[^.]*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
        "X-Requested-With",
    ],
    expose_headers=["*"],
    max_age=3600,
)

# ── WebSocket bypass (se registra después → se ejecuta primero) ───────────────
# Elimina el header Origin de los upgrades WebSocket para que el CORSMiddleware
# los deje pasar sin restricciones de origen.
app.add_middleware(WebSocketCORSBypass)

app.include_router(auth_router)
app.include_router(tenants_router, prefix="/api/v1")
app.include_router(users_router)
app.include_router(vehicles_router)
app.include_router(workshops_router)
app.include_router(technicians_router)
app.include_router(ai_processing_router)
app.include_router(incidents_router)
app.include_router(assignments_router)
app.include_router(notifications_router)
app.include_router(payments_router)
app.include_router(tracking_router)
app.include_router(stats_router)
app.include_router(bitacora_router)
app.include_router(reports_router)
app.include_router(backups_router)
app.include_router(dashboards_ia_router)


@app.exception_handler(Exception)
async def _unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Captura excepciones no controladas (ej. errores de BD) antes de que lleguen a
    ServerErrorMiddleware de Starlette. Al retornar desde aquí la respuesta pasa por
    CORSMiddleware y recibe las cabeceras Access-Control-Allow-Origin correctas.
    Sin este handler, Starlette devuelve el 500 bypassando el send-callback de CORS
    y el browser lo reporta como bloqueo CORS aunque la config sea correcta.
    """
    logger.exception("Error no controlado en %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor. Intente de nuevo más tarde."},
    )


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

_comprobantes_dir = Path(settings.UPLOADS_DIR) / "comprobantes"
_comprobantes_dir.mkdir(parents=True, exist_ok=True)
app.mount(
    settings.COMPROBANTES_URL_PREFIX,
    StaticFiles(directory=str(_comprobantes_dir)),
    name="comprobantes_estaticos",
)




