"""
Router de asignación inteligente de incidentes a talleres.
Tags = ["Asignación Inteligente"]
"""
import asyncio
import logging
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from geoalchemy2.shape import to_shape

from app.core.database import get_db
from app.models.models import INCIDENTES
from app.modules.assignments.models import ASIGNACIONES
from app.modules.assignments.schemas import (
    AssignmentResponse,
    AvailableWorkshopsResponse,
    CotizacionCreate,
    CotizacionDetalleResponse,
    CotizacionRespuesta,
    WorkshopCandidateResponse,
)
from app.modules.assignments.service import (
    asignar_taller_automaticamente,
    buscar_talleres_candidatos,
)
from app.modules.auth.dependencies import (
    get_current_active_user,
    get_current_user,
    verificar_acceso_incidente,
)
from app.modules.notifications.service import (
    enviar_notificacion_cliente,
    enviar_notificacion_taller,
)
from app.modules.technicians.models import TECNICOS
from app.modules.users.models import USUARIOS
from app.modules.workshops.models import TALLERES

router = APIRouter(prefix="/assignments", tags=["Asignación Inteligente"])

logger = logging.getLogger(__name__)


class AssignRequest(BaseModel):
    id_tecnico: UUID | None = None


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
    body: AssignRequest = None,
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_active_user),
):
    """
    Asigna un incidente al taller más cercano con técnico disponible.
    Si el body incluye `id_tecnico`, se asigna directamente a ese técnico.
    De lo contrario, se usa asignación automática por GPS.

    Requiere rol ADMIN o TALLER (el dueño del incidente) para autorización.
    """
    from datetime import datetime, timezone

    # Verificar que el incidente existe
    incidente = db.query(INCIDENTES).filter(INCIDENTES.ID_INCIDENTE == id_incidente).first()
    if not incidente:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")

    if _rol_texto(usuario) not in ("TALLER", "ADMIN"):
        raise HTTPException(status_code=403, detail="Solo talleres y admins pueden asignar")
    verificar_acceso_incidente(usuario, incidente)

    id_tecnico_manual = body.id_tecnico if body else None

    if id_tecnico_manual:
        # Asignación directa al técnico especificado por el frontend
        tecnico = db.query(TECNICOS).filter(
            TECNICOS.ID_TECNICO == id_tecnico_manual,
            TECNICOS.DISPONIBLE.is_(True),
        ).first()
        if not tecnico:
            raise HTTPException(
                status_code=400,
                detail="El técnico no existe o no está disponible",
            )

        taller = db.query(TALLERES).filter(TALLERES.ID_TALLER == tecnico.ID_TALLER).first()
        if not taller:
            raise HTTPException(status_code=400, detail="Taller no encontrado")

        asignacion = ASIGNACIONES(
            ID_INCIDENTE=id_incidente,
            ID_TALLER=taller.ID_TALLER,
            ID_TECNICO=tecnico.ID_TECNICO,
        )
        db.add(asignacion)

        tecnico.DISPONIBLE = False
        db.add(tecnico)

        incidente.ESTADO = "ASIGNADO"
        db.add(incidente)

        db.commit()
        db.refresh(asignacion)
    else:
        # Fallback: asignación automática por GPS
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

    # Notificar en tiempo real que hay una nueva asignación
    notif = {
        "tipo": "nueva_asignacion",
        "incidente_id": str(id_incidente),
        "mensaje": "Incidente asignado a taller",
        "timestamp": datetime.utcnow().isoformat(),
    }
    try:
        from app.modules.notifications.service import broadcast_global
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(broadcast_global(notif))
    except Exception:
        pass

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


@router.get(
    "/my",
    summary="Mis asignaciones (Taller)",
    description="Lista las asignaciones del taller autenticado con detalle del incidente.",
)
def listar_mis_asignaciones(
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_user),
):
    rol = _rol_texto(usuario)
    if rol not in ("TALLER", "ADMIN"):
        raise HTTPException(status_code=403, detail="Solo talleres y admins pueden consultar asignaciones")

    if rol == "ADMIN":
        asignaciones = (
            db.query(ASIGNACIONES)
            .order_by(ASIGNACIONES.FECHA_ASIGNACION.desc())
            .all()
        )
    else:
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

    inc = db.query(INCIDENTES).filter(INCIDENTES.ID_INCIDENTE == id_incidente).first()
    if inc:
        verificar_acceso_incidente(usuario, inc)

    asignacion.FECHA_RECHAZO = datetime.now(timezone.utc)
    asignacion.MOTIVO_RECHAZO = body.get("motivo_rechazo", "Rechazado por el taller")

    if inc:
        inc.ESTADO = "CANCELADO"

    db.commit()
    return {"detail": "Asignación rechazada"}


# ─── helpers ────────────────────────────────────────────────────────────────

def _notify_incidente(incidente_id: UUID, payload: dict) -> None:
    """Encola un broadcast al canal WebSocket del incidente."""
    try:
        from app.modules.notifications.service import broadcast_incidente_async
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(broadcast_incidente_async(incidente_id, payload))
    except Exception:
        pass


# ─── CU21 — Cotizaciones ─────────────────────────────────────────────────────

@router.get(
    "/incidents/{id_incidente}/cotizacion",
    response_model=CotizacionDetalleResponse,
    summary="Ver cotización del incidente",
    description="Devuelve el estado actual de la cotización: propuesta, aceptada o sin respuesta.",
)
def ver_cotizacion(
    id_incidente: UUID,
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_active_user),
):
    inc = db.query(INCIDENTES).filter(INCIDENTES.ID_INCIDENTE == id_incidente).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")

    # Aislamiento por tenant (CLIENTE dueño / TALLER-TECNICO mismo tenant / ADMIN todo).
    verificar_acceso_incidente(usuario, inc)

    asignacion = (
        db.query(ASIGNACIONES)
        .filter(
            ASIGNACIONES.ID_INCIDENTE == id_incidente,
            ASIGNACIONES.FECHA_RECHAZO.is_(None),
        )
        .first()
    )
    if not asignacion:
        raise HTTPException(status_code=404, detail="Sin asignación activa para este incidente")

    estado_str = inc.ESTADO.value if hasattr(inc.ESTADO, "value") else str(inc.ESTADO)
    return CotizacionDetalleResponse(
        id_asignacion=asignacion.ID_ASIGNACION,
        id_incidente=inc.ID_INCIDENTE,
        monto_cotizado=float(asignacion.MONTO_COTIZADO) if asignacion.MONTO_COTIZADO else None,
        tiempo_estimado_reparacion=asignacion.TIEMPO_ESTIMADO_REPARACION,
        notas_cotizacion=asignacion.NOTAS_COTIZACION,
        cotizacion_aceptada=asignacion.COTIZACION_ACEPTADA,
        estado_incidente=estado_str,
        timestamp=datetime.utcnow().isoformat(),
    )


@router.post(
    "/incidents/{id_incidente}/cotizacion",
    response_model=CotizacionDetalleResponse,
    summary="Proponer cotización (Taller)",
    description=(
        "El taller asignado propone el monto, tiempo estimado y notas de cotización. "
        "Solo disponible cuando el incidente está en estado ASIGNADO y sin respuesta del cliente."
    ),
)
def proponer_cotizacion(
    id_incidente: UUID,
    body: CotizacionCreate,
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_active_user),
):
    if _rol_texto(usuario) != "TALLER":
        raise HTTPException(status_code=403, detail="Solo talleres pueden proponer cotizaciones")

    inc = db.query(INCIDENTES).filter(INCIDENTES.ID_INCIDENTE == id_incidente).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")
    verificar_acceso_incidente(usuario, inc)

    estado_str = inc.ESTADO.value if hasattr(inc.ESTADO, "value") else str(inc.ESTADO)
    if estado_str != "ASIGNADO":
        raise HTTPException(
            status_code=400,
            detail=f"Solo se puede cotizar en estado ASIGNADO (estado actual: {estado_str})",
        )

    taller = db.query(TALLERES).filter(TALLERES.ID_USUARIO == usuario.ID_USUARIO).first()
    if not taller:
        raise HTTPException(status_code=404, detail="Taller no encontrado")

    asignacion = (
        db.query(ASIGNACIONES)
        .filter(
            ASIGNACIONES.ID_INCIDENTE == id_incidente,
            ASIGNACIONES.ID_TALLER == taller.ID_TALLER,
            ASIGNACIONES.FECHA_RECHAZO.is_(None),
        )
        .first()
    )
    if not asignacion:
        raise HTTPException(status_code=403, detail="No sos el taller asignado a este incidente")

    if asignacion.COTIZACION_ACEPTADA is not None:
        raise HTTPException(
            status_code=400,
            detail="El cliente ya respondió a la cotización — no se puede modificar",
        )

    asignacion.MONTO_COTIZADO = body.monto_cotizado
    asignacion.TIEMPO_ESTIMADO_REPARACION = body.tiempo_estimado_reparacion
    asignacion.NOTAS_COTIZACION = body.notas_cotizacion
    db.add(asignacion)
    db.commit()
    db.refresh(asignacion)

    payload = {
        "tipo": "cotizacion_propuesta",
        "incidente_id": str(id_incidente),
        "asignacion_id": str(asignacion.ID_ASIGNACION),
        "monto_cotizado": float(body.monto_cotizado),
        "tiempo_estimado_reparacion": body.tiempo_estimado_reparacion,
        "notas_cotizacion": body.notas_cotizacion,
        "mensaje": "El taller propuso una cotización. Por favor revisá y respondé.",
        "timestamp": datetime.utcnow().isoformat(),
    }
    _notify_incidente(id_incidente, payload)

    return CotizacionDetalleResponse(
        id_asignacion=asignacion.ID_ASIGNACION,
        id_incidente=inc.ID_INCIDENTE,
        monto_cotizado=float(asignacion.MONTO_COTIZADO),
        tiempo_estimado_reparacion=asignacion.TIEMPO_ESTIMADO_REPARACION,
        notas_cotizacion=asignacion.NOTAS_COTIZACION,
        cotizacion_aceptada=asignacion.COTIZACION_ACEPTADA,
        estado_incidente=estado_str,
        timestamp=payload["timestamp"],
    )


@router.post(
    "/incidents/{id_incidente}/cotizacion/respuesta",
    response_model=CotizacionDetalleResponse,
    summary="Responder cotización (Cliente)",
    description=(
        "El cliente acepta o rechaza la cotización propuesta por el taller.\n\n"
        "- **Aceptar**: el incidente avanza automáticamente a EN_CAMINO.\n"
        "- **Rechazar**: el incidente vuelve a CLASIFICADO para reasignación; "
        "el técnico queda disponible nuevamente."
    ),
)
def responder_cotizacion(
    id_incidente: UUID,
    body: CotizacionRespuesta,
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_active_user),
):
    from app.models.models import HISTORIAL_INCIDENTES

    if _rol_texto(usuario) != "CLIENTE":
        raise HTTPException(status_code=403, detail="Solo clientes pueden responder cotizaciones")

    inc = db.query(INCIDENTES).filter(INCIDENTES.ID_INCIDENTE == id_incidente).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")

    if inc.ID_USUARIO_CLIENTE != usuario.ID_USUARIO:
        raise HTTPException(status_code=403, detail="No autorizado a responder este incidente")

    estado_str = inc.ESTADO.value if hasattr(inc.ESTADO, "value") else str(inc.ESTADO)
    if estado_str != "ASIGNADO":
        raise HTTPException(
            status_code=400,
            detail=f"Solo se puede responder en estado ASIGNADO (estado actual: {estado_str})",
        )

    asignacion = (
        db.query(ASIGNACIONES)
        .filter(
            ASIGNACIONES.ID_INCIDENTE == id_incidente,
            ASIGNACIONES.FECHA_RECHAZO.is_(None),
        )
        .first()
    )
    if not asignacion:
        raise HTTPException(status_code=404, detail="Sin asignación activa para este incidente")

    if asignacion.MONTO_COTIZADO is None:
        raise HTTPException(
            status_code=400,
            detail="El taller todavía no envió una cotización",
        )

    if asignacion.COTIZACION_ACEPTADA is not None:
        raise HTTPException(
            status_code=400,
            detail="Ya respondiste a esta cotización — no se puede cambiar",
        )

    if body.aceptada:
        asignacion.COTIZACION_ACEPTADA = True
        asignacion.FECHA_ACEPTACION = datetime.utcnow()
        inc.ESTADO = "EN_CAMINO"
        db.add(asignacion)
        db.add(inc)
        db.add(
            HISTORIAL_INCIDENTES(
                ID_INCIDENTE=id_incidente,
                ESTADO="EN_CAMINO",
                NOTAS="Cliente aceptó la cotización. Técnico en camino.",
                ID_USUARIO_CAMBIO=usuario.ID_USUARIO,
            )
        )
        db.commit()
        db.refresh(asignacion)

        nuevo_estado = "EN_CAMINO"
        payload = {
            "tipo": "cotizacion_aceptada",
            "incidente_id": str(id_incidente),
            "asignacion_id": str(asignacion.ID_ASIGNACION),
            "nuevo_estado": nuevo_estado,
            "monto_cotizado": float(asignacion.MONTO_COTIZADO),
            "mensaje": "Cotización aceptada. El técnico se dirige al lugar.",
            "timestamp": datetime.utcnow().isoformat(),
        }
    else:
        # Rechazar: liberar técnico y eliminar asignación para permitir reasignación
        if asignacion.ID_TECNICO:
            tecnico = db.query(TECNICOS).filter(
                TECNICOS.ID_TECNICO == asignacion.ID_TECNICO
            ).first()
            if tecnico:
                tecnico.DISPONIBLE = True
                db.add(tecnico)

        db.add(
            HISTORIAL_INCIDENTES(
                ID_INCIDENTE=id_incidente,
                ESTADO="CLASIFICADO",
                NOTAS=f"Cliente rechazó la cotización. Motivo: {body.motivo_rechazo or 'sin especificar'}",
                ID_USUARIO_CAMBIO=usuario.ID_USUARIO,
            )
        )
        db.delete(asignacion)
        inc.ESTADO = "CLASIFICADO"
        db.add(inc)
        db.commit()

        nuevo_estado = "CLASIFICADO"
        payload = {
            "tipo": "cotizacion_rechazada",
            "incidente_id": str(id_incidente),
            "nuevo_estado": nuevo_estado,
            "motivo_rechazo": body.motivo_rechazo,
            "mensaje": "Cotización rechazada. El incidente vuelve a CLASIFICADO para reasignación.",
            "timestamp": datetime.utcnow().isoformat(),
        }
        asignacion = None  # fue eliminado

    _notify_incidente(id_incidente, payload)

    # También notificar al canal global para actualizar dashboards con el cambio de estado
    try:
        from app.modules.notifications.service import broadcast_global
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(broadcast_global({
                "tipo": "estado_actualizado",
                "incidente_id": str(id_incidente),
                "nuevo_estado": nuevo_estado,
                "mensaje": f"Incidente {id_incidente} cambió a {nuevo_estado}",
                "timestamp": datetime.utcnow().isoformat(),
            }))
    except Exception:
        pass

    monto = float(asignacion.MONTO_COTIZADO) if asignacion else None
    tiempo = asignacion.TIEMPO_ESTIMADO_REPARACION if asignacion else None
    notas = asignacion.NOTAS_COTIZACION if asignacion else None
    id_asig = asignacion.ID_ASIGNACION if asignacion else UUID("00000000-0000-0000-0000-000000000000")

    return CotizacionDetalleResponse(
        id_asignacion=id_asig,
        id_incidente=id_incidente,
        monto_cotizado=monto,
        tiempo_estimado_reparacion=tiempo,
        notas_cotizacion=notas,
        cotizacion_aceptada=body.aceptada,
        estado_incidente=nuevo_estado,
        timestamp=payload["timestamp"],
    )
