"""
CRUD de técnicos del taller + flujo de trabajo del técnico autenticado.

ORDEN de rutas (importante: rutas estáticas antes que /{id_tecnico}):
  GET    /tecnicos/mi-asignacion              → orden activa del TECNICO
  PATCH  /tecnicos/incidente/{id}/estado      → máquina de estados del TECNICO
  GET    /tecnicos                            → listar (TALLER/ADMIN)
  POST   /tecnicos                            → crear sin login (TALLER)
  POST   /tecnicos/crear-con-usuario          → crear con login (TALLER)
  GET    /tecnicos/{id_tecnico}               → detalle (TALLER)
  PUT    /tecnicos/{id_tecnico}               → actualizar (TALLER)
  DELETE /tecnicos/{id_tecnico}               → eliminar (TALLER)
"""
import asyncio
import logging
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from geoalchemy2.shape import to_shape
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hashear_contrasena
from app.models.models import (
    ASIGNACIONES,
    HISTORIAL_INCIDENTES,
    INCIDENTES,
    TALLERES,
    TECNICOS,
    USUARIOS,
)
from app.presentation.api.v1.dependencies.auth import (
    get_current_tecnico,
    get_current_taller,
    get_current_user,
)
from app.presentation.api.v1.schemas.incident import IncidentListResponse
from app.presentation.api.v1.schemas.technician import (
    TechnicianActiveAssignmentResponse,
    TechnicianCreate,
    TechnicianResponse,
    TechnicianUpdate,
    TechnicianWithUserCreate,
    UpdateIncidentStateRequest,
)

router = APIRouter(prefix="/tecnicos", tags=["Técnicos"])

logger = logging.getLogger(__name__)

# Máquina de estados: estado_actual → estado_siguiente permitido
_TRANSICIONES_VALIDAS: dict[str, str] = {
    "ASIGNADO": "EN_CAMINO",
    "EN_CAMINO": "EN_PROCESO",
    "EN_PROCESO": "ATENDIDO",
}

_ESTADOS_ACTIVOS = {"ASIGNADO", "EN_CAMINO", "EN_PROCESO"}


# ─────────────────────── helpers ─────────────────────────────────────────────

def _taller_del_token(db: Session, usuario: USUARIOS) -> TALLERES:
    t = db.query(TALLERES).filter(TALLERES.ID_USUARIO == usuario.ID_USUARIO).first()
    if not t:
        raise HTTPException(
            status_code=400,
            detail="Debe registrar su taller antes de gestionar técnicos",
        )
    return t


def _tecnico_en_taller(db: Session, id_tecnico: UUID, id_taller: UUID) -> TECNICOS | None:
    return (
        db.query(TECNICOS)
        .filter(TECNICOS.ID_TECNICO == id_tecnico, TECNICOS.ID_TALLER == id_taller)
        .first()
    )


def _rol_texto(usuario: USUARIOS) -> str:
    r = usuario.ROL
    return r.value if hasattr(r, "value") else str(r)


def _val_texto(val) -> str:
    return val.value if hasattr(val, "value") else str(val)


def _coords(inc: INCIDENTES) -> tuple[float | None, float | None]:
    if inc.UBICACION is None:
        return None, None
    try:
        p = to_shape(inc.UBICACION)
        return float(p.y), float(p.x)
    except Exception:
        return None, None


def _a_lista(inc: INCIDENTES) -> IncidentListResponse:
    lat, lon = _coords(inc)
    base = IncidentListResponse.model_validate(inc)
    return base.model_copy(update={"latitud": lat, "longitud": lon})


# ═════════════════════ FLUJO TÉCNICO AUTENTICADO ══════════════════════════════
# Estas rutas DEBEN ir antes de /{id_tecnico} para que FastAPI no intente
# parsear "mi-asignacion" como UUID.

@router.get(
    "/mi-asignacion",
    response_model=TechnicianActiveAssignmentResponse | None,
    summary="Orden activa del técnico",
    description=(
        "Devuelve la asignación activa del técnico autenticado con todos los "
        "datos del incidente, ubicación GPS y datos del cliente. "
        "Retorna null si el técnico está libre (sin orden activa)."
    ),
)
def obtener_mi_asignacion(
    db: Session = Depends(get_db),
    tecnico: TECNICOS = Depends(get_current_tecnico),
):
    """Asignación activa (ASIGNADO / EN_CAMINO / EN_PROCESO) del técnico."""
    asignacion = (
        db.query(ASIGNACIONES)
        .join(INCIDENTES, ASIGNACIONES.ID_INCIDENTE == INCIDENTES.ID_INCIDENTE)
        .filter(
            ASIGNACIONES.ID_TECNICO == tecnico.ID_TECNICO,
            ASIGNACIONES.FECHA_RECHAZO.is_(None),
            INCIDENTES.ESTADO.in_(list(_ESTADOS_ACTIVOS)),
        )
        .first()
    )
    if asignacion is None:
        return None

    incidente = db.query(INCIDENTES).filter(
        INCIDENTES.ID_INCIDENTE == asignacion.ID_INCIDENTE
    ).first()

    cliente = db.query(USUARIOS).filter(
        USUARIOS.ID_USUARIO == incidente.ID_USUARIO_CLIENTE
    ).first()

    lat, lng = _coords(incidente)

    return TechnicianActiveAssignmentResponse(
        id_asignacion=asignacion.ID_ASIGNACION,
        id_incidente=incidente.ID_INCIDENTE,
        id_taller=asignacion.ID_TALLER,
        id_tecnico=tecnico.ID_TECNICO,
        estado_incidente=_val_texto(incidente.ESTADO),
        clasificacion=_val_texto(incidente.CLASIFICACION),
        prioridad=_val_texto(incidente.PRIORIDAD),
        resumen_ia=incidente.RESUMEN_IA,
        latitud=lat,
        longitud=lng,
        tiempo_estimado_llegada_minutos=incidente.TIEMPO_ESTIMADO_LLEGADA_MINUTOS,
        cliente_nombre=cliente.NOMBRE_COMPLETO if cliente else None,
        cliente_telefono=cliente.TELEFONO if cliente else None,
        fecha_asignacion=asignacion.FECHA_ASIGNACION,
        fecha_creacion_incidente=incidente.FECHA_CREACION,
    )


@router.patch(
    "/incidente/{id_incidente}/estado",
    response_model=IncidentListResponse,
    summary="Actualizar estado del incidente (técnico)",
    description=(
        "Máquina de estados exclusiva del técnico asignado:\n"
        "- ASIGNADO → EN_CAMINO\n"
        "- EN_CAMINO → EN_PROCESO\n"
        "- EN_PROCESO → ATENDIDO\n\n"
        "Al pasar a ATENDIDO: técnico queda DISPONIBLE y se genera el pago."
    ),
)
def actualizar_estado_incidente_tecnico(
    id_incidente: UUID,
    body: UpdateIncidentStateRequest,
    db: Session = Depends(get_db),
    tecnico: TECNICOS = Depends(get_current_tecnico),
):
    """Solo el técnico asignado puede avanzar el estado de su incidente."""
    # Verificar que este técnico está asignado al incidente
    asignacion = (
        db.query(ASIGNACIONES)
        .filter(
            ASIGNACIONES.ID_INCIDENTE == id_incidente,
            ASIGNACIONES.ID_TECNICO == tecnico.ID_TECNICO,
            ASIGNACIONES.FECHA_RECHAZO.is_(None),
        )
        .first()
    )
    if not asignacion:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No estás asignado a este incidente",
        )

    incidente = db.query(INCIDENTES).filter(
        INCIDENTES.ID_INCIDENTE == id_incidente
    ).first()
    if not incidente:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")

    estado_actual = _val_texto(incidente.ESTADO)
    nuevo_estado = body.nuevo_estado

    # Validar transición de la máquina de estados
    siguiente_permitido = _TRANSICIONES_VALIDAS.get(estado_actual)
    if siguiente_permitido is None or siguiente_permitido != nuevo_estado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Transición inválida: '{estado_actual}' → '{nuevo_estado}'. "
                f"Transición permitida desde '{estado_actual}': "
                f"'{siguiente_permitido or 'ninguna'}'."
            ),
        )

    incidente.ESTADO = nuevo_estado
    db.add(incidente)

    historial = HISTORIAL_INCIDENTES(
        ID_INCIDENTE=id_incidente,
        ESTADO=nuevo_estado,
        NOTAS=f"Técnico cambió estado: {estado_actual} → {nuevo_estado}",
        ID_USUARIO_CAMBIO=tecnico.ID_USUARIO,
    )
    db.add(historial)

    if nuevo_estado == "ATENDIDO":
        tecnico.DISPONIBLE = True
        db.add(tecnico)
        db.flush()

        # Crear pago y notificar (reutiliza lógica existente)
        try:
            from app.application.use_cases import payment_service
            pago = payment_service.crear_pago_pendiente(db, incidente, asignacion)
            _broadcast({
                "tipo": "pago_creado",
                "pago_id": str(pago.ID_PAGO),
                "incidente_id": str(id_incidente),
                "monto": str(pago.MONTO),
                "mensaje": "Pago generado por incidente atendido",
                "timestamp": datetime.utcnow().isoformat(),
            })
        except Exception:
            logger.exception("Error al crear pago para incidente %s", id_incidente)

    db.commit()
    db.refresh(incidente)

    _broadcast({
        "tipo": "estado_actualizado",
        "incidente_id": str(id_incidente),
        "nuevo_estado": nuevo_estado,
        "mensaje": f"Técnico actualizó estado a {nuevo_estado}",
        "timestamp": datetime.utcnow().isoformat(),
    })

    return _a_lista(incidente)


def _broadcast(payload: dict) -> None:
    try:
        from app.application.use_cases.notification_service import broadcast_global
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(broadcast_global(payload))
    except Exception:
        pass


# ═════════════════════ TALLER / ADMIN CRUD ═══════════════════════════════════

@router.get("", response_model=list[TechnicianResponse])
def listar_tecnicos(
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_user),
):
    """Lista técnicos. TALLER: solo los de su taller. ADMIN: todos."""
    rol = _rol_texto(usuario)
    if rol == "ADMIN":
        items = db.query(TECNICOS).order_by(TECNICOS.NOMBRE_COMPLETO).all()
    elif rol == "TALLER":
        taller = _taller_del_token(db, usuario)
        items = (
            db.query(TECNICOS)
            .filter(TECNICOS.ID_TALLER == taller.ID_TALLER)
            .order_by(TECNICOS.NOMBRE_COMPLETO)
            .all()
        )
    else:
        raise HTTPException(status_code=403, detail="Solo talleres y admins pueden listar técnicos")
    return [TechnicianResponse.model_validate(x) for x in items]


@router.post("", response_model=TechnicianResponse, status_code=status.HTTP_201_CREATED)
def crear_tecnico(
    datos: TechnicianCreate,
    db: Session = Depends(get_db),
    dueno: USUARIOS = Depends(get_current_taller),
):
    """Alta de técnico en el taller del usuario (sin cuenta de login)."""
    taller = _taller_del_token(db, dueno)
    tecnico = TECNICOS(
        ID_TALLER=taller.ID_TALLER,
        NOMBRE_COMPLETO=datos.nombre_completo,
        TELEFONO=datos.telefono,
        DISPONIBLE=datos.disponible,
    )
    db.add(tecnico)
    db.commit()
    db.refresh(tecnico)
    return TechnicianResponse.model_validate(tecnico)


@router.post(
    "/crear-con-usuario",
    response_model=TechnicianResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear técnico con cuenta de login",
    description=(
        "Crea atómicamente un USUARIO con rol=TECNICO (contraseña hasheada con bcrypt) "
        "y el registro TECNICOS vinculado. El técnico podrá autenticarse desde la app móvil."
    ),
)
def crear_tecnico_con_usuario(
    datos: TechnicianWithUserCreate,
    db: Session = Depends(get_db),
    dueno: USUARIOS = Depends(get_current_taller),
):
    """Alta de técnico con cuenta de login propia (rol TECNICO)."""
    taller = _taller_del_token(db, dueno)

    if db.query(USUARIOS).filter(USUARIOS.CORREO_ELECTRONICO == datos.correo_electronico).first():
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    usuario = USUARIOS(
        CORREO_ELECTRONICO=datos.correo_electronico,
        HASH_CONTRASENA=hashear_contrasena(datos.contrasena),
        NOMBRE_COMPLETO=datos.nombre_completo,
        TELEFONO=datos.telefono,
        ROL="TECNICO",
        ACTIVO=True,
    )
    db.add(usuario)
    db.flush()

    tecnico = TECNICOS(
        ID_TALLER=taller.ID_TALLER,
        ID_USUARIO=usuario.ID_USUARIO,
        NOMBRE_COMPLETO=datos.nombre_completo,
        TELEFONO=datos.telefono,
        DISPONIBLE=True,
    )
    db.add(tecnico)
    db.commit()
    db.refresh(tecnico)
    return TechnicianResponse.model_validate(tecnico)


@router.get("/{id_tecnico}", response_model=TechnicianResponse)
def obtener_tecnico(
    id_tecnico: UUID,
    db: Session = Depends(get_db),
    dueno: USUARIOS = Depends(get_current_taller),
):
    """Detalle de un técnico del propio taller."""
    taller = _taller_del_token(db, dueno)
    t = _tecnico_en_taller(db, id_tecnico, taller.ID_TALLER)
    if not t:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")
    return TechnicianResponse.model_validate(t)


@router.put("/{id_tecnico}", response_model=TechnicianResponse)
def actualizar_tecnico(
    id_tecnico: UUID,
    datos: TechnicianUpdate,
    db: Session = Depends(get_db),
    dueno: USUARIOS = Depends(get_current_taller),
):
    """Actualiza datos del técnico."""
    taller = _taller_del_token(db, dueno)
    t = _tecnico_en_taller(db, id_tecnico, taller.ID_TALLER)
    if not t:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")

    if datos.nombre_completo is not None:
        t.NOMBRE_COMPLETO = datos.nombre_completo
    if datos.telefono is not None:
        t.TELEFONO = datos.telefono
    if datos.disponible is not None:
        t.DISPONIBLE = datos.disponible

    db.add(t)
    db.commit()
    db.refresh(t)
    return TechnicianResponse.model_validate(t)


@router.delete("/{id_tecnico}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_tecnico(
    id_tecnico: UUID,
    db: Session = Depends(get_db),
    dueno: USUARIOS = Depends(get_current_taller),
):
    """Elimina un técnico del taller."""
    taller = _taller_del_token(db, dueno)
    t = _tecnico_en_taller(db, id_tecnico, taller.ID_TALLER)
    if not t:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")
    db.delete(t)
    db.commit()
    return None
