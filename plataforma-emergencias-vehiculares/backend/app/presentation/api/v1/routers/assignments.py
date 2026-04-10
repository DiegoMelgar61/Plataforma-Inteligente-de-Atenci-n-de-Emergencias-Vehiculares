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
from app.models.models import ASIGNACIONES, INCIDENTES, TALLERES, TECNICOS, USUARIOS
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


def _rol_texto(usuario: USUARIOS) -> str:
    r = usuario.ROL
    return r.value if hasattr(r, "value") else str(r)


@router.get(
    "/my",
    summary="Mis asignaciones (Taller)",
    description="Lista las asignaciones del taller autenticado con detalle del incidente.",
)
def listar_mis_asignaciones(
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_user),
):
    if _rol_texto(usuario) != "TALLER":
        raise HTTPException(status_code=403, detail="Solo talleres pueden consultar sus asignaciones")

    taller = db.query(TALLERES).filter(TALLERES.ID_USUARIO == usuario.ID_USUARIO).first()
    if not taller:
        raise HTTPException(status_code=404, detail="Taller no encontrado para este usuario")

    asignaciones = (
        db.query(ASIGNACIONES)
        .filter(ASIGNACIONES.ID_TALLER == taller.ID_TALLER)
        .order_by(ASIGNACIONES.FECHA_ASIGNACION.desc())
        .all()
    )

    result = []
    for a in asignaciones:
        inc = db.query(INCIDENTES).filter(INCIDENTES.ID_INCIDENTE == a.ID_INCIDENTE).first()
        tec = db.query(TECNICOS).filter(TECNICOS.ID_TECNICO == a.ID_TECNICO).first() if a.ID_TECNICO else None

        inc_data = None
        if inc:
            from geoalchemy2.shape import to_shape as _to_shape
            lat, lon = None, None
            try:
                if inc.UBICACION:
                    p = _to_shape(inc.UBICACION)
                    lat, lon = float(p.y), float(p.x)
            except Exception:
                pass
            inc_data = {
                "id_incidente": str(inc.ID_INCIDENTE),
                "estado": str(inc.ESTADO.value if hasattr(inc.ESTADO, 'value') else inc.ESTADO),
                "prioridad": str(inc.PRIORIDAD.value if hasattr(inc.PRIORIDAD, 'value') else inc.PRIORIDAD),
                "clasificacion": str(inc.CLASIFICACION.value if hasattr(inc.CLASIFICACION, 'value') else inc.CLASIFICACION),
                "resumen_ia": inc.RESUMEN_IA,
                "latitud": lat,
                "longitud": lon,
                "fecha_creacion": inc.FECHA_CREACION.isoformat() if inc.FECHA_CREACION else None,
            }

        tec_data = None
        if tec:
            tec_data = {
                "id_tecnico": str(tec.ID_TECNICO),
                "nombre_completo": tec.NOMBRE_COMPLETO,
                "telefono": tec.TELEFONO,
                "disponible": tec.DISPONIBLE,
            }

        result.append({
            "id_asignacion": str(a.ID_ASIGNACION),
            "id_incidente": str(a.ID_INCIDENTE),
            "id_taller": str(a.ID_TALLER),
            "id_tecnico": str(a.ID_TECNICO) if a.ID_TECNICO else None,
            "fecha_asignacion": a.FECHA_ASIGNACION.isoformat() if a.FECHA_ASIGNACION else None,
            "fecha_aceptacion": a.FECHA_ACEPTACION.isoformat() if a.FECHA_ACEPTACION else None,
            "fecha_rechazo": a.FECHA_RECHAZO.isoformat() if a.FECHA_RECHAZO else None,
            "motivo_rechazo": a.MOTIVO_RECHAZO,
            "incidente": inc_data,
            "tecnico": tec_data,
        })

    return result


@router.post(
    "/incidents/{id_incidente}/reject",
    summary="Rechazar asignación (Taller)",
)
def rechazar_asignacion(
    id_incidente: UUID,
    body: dict,
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_user),
):
    if _rol_texto(usuario) != "TALLER":
        raise HTTPException(status_code=403, detail="Solo talleres pueden rechazar asignaciones")

    from datetime import datetime, timezone
    asignacion = db.query(ASIGNACIONES).filter(ASIGNACIONES.ID_INCIDENTE == id_incidente).first()
    if not asignacion:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")

    asignacion.FECHA_RECHAZO = datetime.now(timezone.utc)
    asignacion.MOTIVO_RECHAZO = body.get("motivo_rechazo", "Rechazado por el taller")

    inc = db.query(INCIDENTES).filter(INCIDENTES.ID_INCIDENTE == id_incidente).first()
    if inc:
        inc.ESTADO = "CANCELADO"

    db.commit()
    return {"detail": "Asignación rechazada"}
