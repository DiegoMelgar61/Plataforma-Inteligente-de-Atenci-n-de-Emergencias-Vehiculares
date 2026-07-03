"""
Dashboards IA: genera paneles/gráficos a partir de un pedido en texto o audio.
Solo ADMIN (puede elegir el tenant). Los datos son reales (tenant-scoped); la IA
solo decide qué métricas y qué gráficos mostrar.
"""
import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.application.use_cases import dashboard_ia_service
from app.core.database import get_db
from app.models.models import USUARIOS
from app.modules.bitacora import service as bitacora_service
from app.presentation.api.v1.dependencies.auth import get_current_admin

router = APIRouter(prefix="/dashboards-ia", tags=["Dashboards IA"])

logger = logging.getLogger(__name__)

_MIME_AUDIO = {
    "audio/mpeg", "audio/mp3", "audio/wav", "audio/x-wav", "audio/webm",
    "audio/ogg", "audio/mp4", "audio/m4a", "audio/aac",
}


@router.get(
    "/metricas",
    summary="Catálogo de métricas disponibles",
)
def listar_metricas(_: USUARIOS = Depends(get_current_admin)):
    return [
        {"clave": k, "descripcion": v["desc"], "tipo_sugerido": v["tipo"]}
        for k, v in dashboard_ia_service.CATALOGO.items()
    ]


@router.post(
    "/generar",
    summary="Generar dashboard desde texto o audio (Admin)",
    description=(
        "Recibe un pedido en lenguaje natural (texto o audio) y un tenant. La IA "
        "decide qué gráficos mostrar; el backend los llena con datos reales."
    ),
)
async def generar_dashboard(
    id_tenant: Annotated[UUID | None, Form(description="Tenant a analizar (ADMIN). Omitir = todos.")] = None,
    texto: Annotated[str | None, Form(description="Pedido en texto")] = None,
    audio: Annotated[UploadFile | None, File(description="Pedido en audio (opcional)")] = None,
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_admin),
):
    audio_part = None
    if audio is not None and audio.filename:
        ct = (audio.content_type or "").split(";")[0].strip().lower()
        if ct not in _MIME_AUDIO:
            raise HTTPException(status_code=400, detail=f"Tipo de audio no permitido: {ct or 'desconocido'}")
        audio_part = {"mime_type": ct, "data": await audio.read()}

    if audio_part is None and not (texto and texto.strip()):
        raise HTTPException(status_code=400, detail="Enviá un pedido en texto o un audio")

    dashboard = dashboard_ia_service.generar_dashboard(
        db, tenant=id_tenant, texto=texto, audio_part=audio_part,
    )

    bitacora_service.registrar(
        "DASHBOARD_IA_GENERADO",
        f"Admin generó dashboard IA ({len(dashboard.get('paneles', []))} paneles, origen {dashboard.get('origen')})",
        usuario=usuario,
        id_tenant=id_tenant,
        entidad="DASHBOARD",
    )

    return dashboard
