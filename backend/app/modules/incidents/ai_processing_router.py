"""
Endpoints de procesamiento inteligente sobre incidentes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.infrastructure.external_services.ai_service import ejecutar_pipeline_procesamiento_incidente
from app.modules.incidents.models import INCIDENTES
from app.modules.users.models import USUARIOS
from app.modules.auth.dependencies import get_current_user
from app.modules.incidents.router import _solo_cliente
from app.modules.incidents.ai_schemas import ProcesamientoIAResponse

router = APIRouter(prefix="/incidents", tags=["Inteligencia Artificial"])


@router.post(
    "/{id_incidente}/process",
    response_model=ProcesamientoIAResponse,
    summary="Procesar incidente con IA",
    description=(
        "Ejecuta transcripcion, analisis de imagen/audio, clasificacion y resumen. "
        "Solo el cliente dueno del incidente puede invocarlo."
    ),
)
def procesar_incidente_ia(
    id_incidente: int,
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
    pr = actualizado.PRIORIDAD
    pr_str = pr.value if hasattr(pr, "value") else str(pr)

    return ProcesamientoIAResponse(
        id_incidente=actualizado.ID_INCIDENTE,
        estado=est_str,
        clasificacion=cls_str,
        prioridad=pr_str,
        resumen_ia=actualizado.RESUMEN_IA,
    )
