"""
Endpoints de procesamiento inteligente sobre incidentes (stubs de IA).
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.infrastructure.external_services.ai_service import ejecutar_pipeline_procesamiento_incidente
from app.models.models import INCIDENTES, USUARIOS
from app.presentation.api.v1.dependencies.auth import get_current_user
from app.presentation.api.v1.routers.incidents import _solo_cliente
from app.presentation.api.v1.schemas.ai_processing import ProcesamientoIAResponse

router = APIRouter(prefix="/incidents", tags=["Inteligencia Artificial"])


@router.post(
    "/{id_incidente}/process",
    response_model=ProcesamientoIAResponse,
    summary="Procesar incidente con IA",
    description=(
        "Ejecuta transccripción, análisis de imágenes (stubs), clasificación y resumen. "
        "Solo el cliente dueño del incidente puede invocarlo."
    ),
)
def procesar_incidente_ia(
    id_incidente: UUID,
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_user),
):
    _solo_cliente(usuario)
    inc = db.query(INCIDENTES).filter(INCIDENTES.ID_INCIDENTE == id_incidente).first()
    if not inc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incidente no encontrado")
    if inc.ID_USUARIO_CLIENTE != usuario.ID_USUARIO:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")

    actualizado = ejecutar_pipeline_procesamiento_incidente(db, id_incidente)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")

    est = actualizado.ESTADO
    est_str = est.value if hasattr(est, "value") else str(est)
    cls = actualizado.CLASIFICACION
    cls_str = cls.value if hasattr(cls, "value") else str(cls)

    return ProcesamientoIAResponse(
        id_incidente=actualizado.ID_INCIDENTE,
        estado=est_str,
        clasificacion=cls_str,
        resumen_ia=actualizado.RESUMEN_IA,
    )
