"""
Informe de servicio por incidente. La generación es automática al finalizar el
incidente (transición a ATENDIDO); acá solo se expone la consulta del informe
ya persistido, respetando el aislamiento por tenant.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import (
    get_current_user,
    verificar_acceso_incidente,
)
from app.modules.incidents.models import INCIDENTES
from app.modules.informes.models import INFORMES_SERVICIO
from app.modules.informes.schemas import InformeServicioResponse
from app.modules.users.models import USUARIOS

router = APIRouter(prefix="/informes", tags=["Informes"])

logger = logging.getLogger(__name__)


@router.get(
    "/incidents/{id_incidente}",
    response_model=InformeServicioResponse,
    summary="Obtener el estado y el informe de servicio de un incidente",
    description=(
        "Lee el informe desde la tabla `informes_servicio` (fuente de verdad, "
        "nunca regenera). Devuelve siempre el estado (GENERANDO / LISTO / "
        "FALLIDO); `url_archivo` está disponible solo cuando el estado es LISTO. "
        "404 únicamente si la generación todavía no fue disparada."
    ),
)
def obtener_informe_incidente(
    id_incidente: int,
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_user),
):
    incidente = (
        db.query(INCIDENTES).filter(INCIDENTES.ID_INCIDENTE == id_incidente).first()
    )
    if incidente is None:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")

    # Reutiliza la verificación de tenant/propiedad estándar del proyecto.
    verificar_acceso_incidente(usuario, incidente)

    informe = (
        db.query(INFORMES_SERVICIO)
        .filter(INFORMES_SERVICIO.ID_INCIDENTE == id_incidente)
        .first()
    )
    if informe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El informe de servicio aún no está disponible para este incidente",
        )
    return informe
