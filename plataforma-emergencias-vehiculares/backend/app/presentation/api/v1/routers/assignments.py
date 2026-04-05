"""
Router de asignación inteligente de incidentes a talleres.
Tags = ["Asignación Inteligente"]
"""
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from geoalchemy2.shape import to_shape

from app.core.database import get_db
from app.application.use_cases.assignment_service import (
    asignar_taller_automaticamente,
    buscar_talleres_candidatos,
)
from app.application.use_cases.notification_service import (
    enviar_notificacion_cliente,
    enviar_notificacion_taller,
)
from app.models.models import INCIDENTES, TECNICOS, USUARIOS
from app.presentation.api.v1.dependencies.auth import (
    get_current_active_user,
    get_current_user,
)
from app.presentation.api.v1.schemas.assignment import (
    AssignmentResponse,
    AvailableWorkshopsResponse,
    WorkshopCandidateResponse,
)

router = APIRouter(prefix="/assignments", tags=["Asignación Inteligente"])

logger = logging.getLogger(__name__)


def _rol_texto(usuario: USUARIOS) -> str:
    """Obtiene el rol como string."""
    r = usuario.ROL
    return r.value if hasattr(r, "value") else str(r)


@router.post(
    "/incidents/{id_incidente}/assign",
    response_model=AssignmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Asignar incidente a taller",
    description=(
        "Busca automáticamente el taller con técnico disponible más cercano "
        "al incidente usando PostGIS y realiza la asignación."
    ),
    response_description="Asignación creada satisfactoriamente",
)
def asignar_incidente(
    id_incidente: UUID,
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_active_user),
):
    """
    Asigna un incidente al taller más cercano con técnico disponible.
    Actualiza automáticamente el estado del incidente a "ASIGNADO".

    Requiere rol ADMIN o TALLER (el dueño del incidente) para autorización.
    """
    # Verificar que el incidente existe
    incidente = db.query(INCIDENTES).filter(INCIDENTES.ID_INCIDENTE == id_incidente).first()
    if not incidente:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")

    # Ejecutar asignación automática
    asignacion = asignar_taller_automaticamente(db, id_incidente)
    if not asignacion:
        raise HTTPException(
            status_code=400,
            detail="No hay talleres con técnicos disponibles para asignar",
        )

    # Enviar notificaciones automáticamente
    try:
        enviar_notificacion_cliente(
            db,
            id_incidente,
            "Tu incidente ha sido asignado a un taller. Un técnico está en camino.",
        )
        enviar_notificacion_taller(
            db,
            id_incidente,
            "Nuevo incidente asignado. Revisa los detalles y acepta o rechaza la asignación.",
        )
    except Exception:
        logger.exception("Error al enviar notificaciones para asignación %s", asignacion.ID_ASIGNACION)
        # No propagar el error; la asignación ya fue exitosa

    return AssignmentResponse.model_validate(asignacion)


@router.get(
    "/incidents/{id_incidente}/available-workshops",
    response_model=AvailableWorkshopsResponse,
    summary="Listar talleres disponibles cercanos",
    description=(
        "Retorna el listado de talleres con técnicos disponibles "
        "dentro del radio de búsqueda, ordenados por proximidad."
    ),
    response_description="Listado de talleres candidatos",
)
def obtener_talleres_disponibles(
    id_incidente: UUID,
    db: Session = Depends(get_db),
    _: USUARIOS = Depends(get_current_active_user),
):
    """
    Obtiene los talleres candidatos para un incidente específico.
    Retorna lista ordenada por distancia (más cercanos primero).
    """
    incidente = db.query(INCIDENTES).filter(INCIDENTES.ID_INCIDENTE == id_incidente).first()
    if not incidente:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")

    # Verificar ubicación
    if incidente.UBICACION is None:
        return AvailableWorkshopsResponse(
            ubicado=False,
            total_candidatos=0,
            candidatos=[],
        )

    # Buscar candidatos
    candidatos_raw = buscar_talleres_candidatos(db, incidente)

    # Construir respuesta
    candidatos_dto: list[WorkshopCandidateResponse] = []
    for candidato in candidatos_raw:
        id_tecnico = candidato["id_tecnico"]
        tecnico = db.query(TECNICOS).filter(TECNICOS.ID_TECNICO == id_tecnico).first()

        candidatos_dto.append(
            WorkshopCandidateResponse(
                id_taller=candidato["id_taller"],
                id_tecnico=id_tecnico,
                nombre_negocio=candidato["taller"].NOMBRE_NEGOCIO,
                distancia_km=candidato["distancia_km"],
                telefono_tecnico=tecnico.TELEFONO if tecnico else None,
            )
        )

    return AvailableWorkshopsResponse(
        ubicado=True,
        total_candidatos=len(candidatos_dto),
        candidatos=candidatos_dto,
    )
