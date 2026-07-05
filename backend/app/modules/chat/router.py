"""
Chat de IA por incidente: hilo del cliente (mecánico de emergencias) e hilo
del técnico asignado (copiloto de taller), conectados por un puente de
contexto y notificaciones en tiempo real.
"""
import logging
import re
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.modules.assignments.models import ASIGNACIONES
from app.modules.auth.dependencies import (
    get_current_cliente,
    get_current_tecnico,
    get_current_user,
    verificar_acceso_incidente,
)
from app.modules.chat import service as chat_service
from app.modules.chat.models import MENSAJES_CHAT
from app.modules.incidents.models import INCIDENTES
from app.modules.technicians.models import TECNICOS
from app.modules.users.models import USUARIOS
from app.modules.chat.schemas import (
    ConversacionResponse,
    EnviarMensajeResponse,
    MensajeChatResponse,
)

router = APIRouter(prefix="/chat", tags=["Chat"])

logger = logging.getLogger(__name__)

MIME_IMAGENES = frozenset({"image/jpeg", "image/png", "image/webp", "image/gif", "image/jpg"})

ESTADOS_CHAT_HABILITADO = {"ASIGNADO", "EN_CAMINO", "EN_PROCESO"}


class EnviarMensajeTecnicoRequest(BaseModel):
    contenido: str


def _rol_texto(usuario: USUARIOS) -> str:
    r = usuario.ROL
    return r.value if hasattr(r, "value") else str(r)


def _estado_texto(incidente: INCIDENTES) -> str:
    return incidente.ESTADO.value if hasattr(incidente.ESTADO, "value") else str(incidente.ESTADO)


def _nombre_seguro(nombre: str | None) -> str:
    base = Path(nombre or "archivo").name
    if not base or ".." in base:
        return "archivo"
    return re.sub(r"[^a-zA-Z0-9._-]", "_", base)[:120]


def _obtener_incidente_o_404(db: Session, id_incidente: int) -> INCIDENTES:
    incidente = db.query(INCIDENTES).filter(INCIDENTES.ID_INCIDENTE == id_incidente).first()
    if incidente is None:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")
    return incidente


def _exigir_estado_chat_habilitado(incidente: INCIDENTES) -> None:
    estado_actual = _estado_texto(incidente)
    if estado_actual not in ESTADOS_CHAT_HABILITADO:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "El chat no está disponible en el estado actual del incidente "
                f"({estado_actual}). Debe estar ASIGNADO, EN_CAMINO o EN_PROCESO."
            ),
        )


def _resolver_tecnico_asignado(db: Session, id_incidente: int) -> TECNICOS | None:
    asignacion = (
        db.query(ASIGNACIONES).filter(ASIGNACIONES.ID_INCIDENTE == id_incidente).first()
    )
    if asignacion is None or asignacion.ID_TECNICO is None:
        return None
    return db.query(TECNICOS).filter(TECNICOS.ID_TECNICO == asignacion.ID_TECNICO).first()


def _exigir_tecnico_asignado(db: Session, id_incidente: int, tecnico: TECNICOS) -> None:
    asignado = _resolver_tecnico_asignado(db, id_incidente)
    if asignado is None or asignado.ID_TECNICO != tecnico.ID_TECNICO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No sos el técnico asignado a este incidente",
        )


def _guardar_adjunto(id_incidente: int, adjunto: UploadFile, contenido: bytes) -> tuple[str, str]:
    """Guarda el adjunto en disco y devuelve (url_publica, clave_archivo)."""
    destino_dir = settings.UPLOADS_DIR / "chat" / str(id_incidente)
    destino_dir.mkdir(parents=True, exist_ok=True)
    filename_hex = uuid.uuid4().hex
    nombre_disco = f"{filename_hex}_{_nombre_seguro(adjunto.filename)}"
    ruta = destino_dir / nombre_disco
    ruta.write_bytes(contenido)
    clave = f"chat/{id_incidente}/{nombre_disco}"
    url = f"{settings.EVIDENCIAS_URL_PREFIX.rsplit('/', 1)[0]}/{clave}"
    return url, clave


@router.post(
    "/incidents/{id_incidente}/cliente/mensajes",
    response_model=EnviarMensajeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enviar mensaje al chat de emergencia (cliente)",
)
async def enviar_mensaje_cliente(
    id_incidente: int,
    contenido: Annotated[str | None, Form()] = None,
    adjunto: Annotated[UploadFile | None, File()] = None,
    usuario: USUARIOS = Depends(get_current_cliente),
    db: Session = Depends(get_db),
):
    incidente = _obtener_incidente_o_404(db, id_incidente)
    verificar_acceso_incidente(usuario, incidente)
    if incidente.ID_USUARIO_CLIENTE != usuario.ID_USUARIO:
        raise HTTPException(status_code=403, detail="No autorizado sobre este incidente")
    _exigir_estado_chat_habilitado(incidente)

    tiene_texto = bool(contenido and contenido.strip())
    tiene_adjunto = adjunto is not None and bool(adjunto.filename)
    if not tiene_texto and not tiene_adjunto:
        raise HTTPException(
            status_code=422,
            detail="Debe incluir un mensaje de texto o un adjunto",
        )

    image_part: dict | None = None
    url_adjunto: str | None = None
    clave_adjunto: str | None = None
    tipo_adjunto: str | None = None

    if tiene_adjunto:
        ct = (adjunto.content_type or "").split(";")[0].strip().lower()
        if ct not in MIME_IMAGENES:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de adjunto no permitido: {ct or 'desconocido'}",
            )
        datos = await adjunto.read()
        url_adjunto, clave_adjunto = _guardar_adjunto(id_incidente, adjunto, datos)
        tipo_adjunto = "IMAGEN"
        mime = ct if ct != "image/jpg" else "image/jpeg"
        image_part = {"mime_type": mime, "data": datos}

    conversacion, _ = chat_service.obtener_o_crear_conversacion(db, incidente, "CLIENTE")

    mensaje_cliente = MENSAJES_CHAT(
        ID_CONVERSACION=conversacion.ID_CONVERSACION,
        ROL_EMISOR="CLIENTE",
        ID_USUARIO_EMISOR=usuario.ID_USUARIO,
        CONTENIDO=contenido.strip() if tiene_texto else None,
        URL_ADJUNTO=url_adjunto,
        CLAVE_ADJUNTO=clave_adjunto,
        TIPO_ADJUNTO=tipo_adjunto,
    )
    db.add(mensaje_cliente)
    db.flush()

    respuesta_texto, relevante = chat_service.generar_respuesta_cliente(
        db, incidente, conversacion, contenido, image_part=image_part
    )

    mensaje_ia = MENSAJES_CHAT(
        ID_CONVERSACION=conversacion.ID_CONVERSACION,
        ROL_EMISOR="IA",
        ID_USUARIO_EMISOR=None,
        CONTENIDO=respuesta_texto,
    )
    db.add(mensaje_ia)

    if relevante:
        mensaje_cliente.RELEVANTE_TECNICO = True
        db.add(mensaje_cliente)

    db.commit()
    db.refresh(mensaje_cliente)
    db.refresh(mensaje_ia)

    if relevante:
        resumen = mensaje_cliente.CONTENIDO or "El cliente compartió un adjunto relevante"
        chat_service.notificar_tecnico_info_relevante(db, id_incidente, resumen)

    return EnviarMensajeResponse(
        mensaje_usuario=MensajeChatResponse.model_validate(mensaje_cliente),
        mensaje_ia=MensajeChatResponse.model_validate(mensaje_ia),
    )


@router.get(
    "/incidents/{id_incidente}/cliente/mensajes",
    response_model=ConversacionResponse,
    summary="Historial del chat de emergencia (cliente/técnico asignado/admin)",
)
def obtener_historial_cliente(
    id_incidente: int,
    usuario: USUARIOS = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    incidente = _obtener_incidente_o_404(db, id_incidente)
    verificar_acceso_incidente(usuario, incidente)

    rol = _rol_texto(usuario)
    if rol == "CLIENTE" and incidente.ID_USUARIO_CLIENTE != usuario.ID_USUARIO:
        raise HTTPException(status_code=403, detail="No autorizado sobre este incidente")
    if rol == "TECNICO":
        tecnico = (
            db.query(TECNICOS).filter(TECNICOS.ID_USUARIO == usuario.ID_USUARIO).first()
        )
        if tecnico is None:
            raise HTTPException(status_code=404, detail="Perfil de técnico no encontrado")
        _exigir_tecnico_asignado(db, id_incidente, tecnico)

    conversacion, _ = chat_service.obtener_o_crear_conversacion(db, incidente, "CLIENTE")
    db.commit()
    mensajes = (
        db.query(MENSAJES_CHAT)
        .filter(MENSAJES_CHAT.ID_CONVERSACION == conversacion.ID_CONVERSACION)
        .order_by(MENSAJES_CHAT.FECHA_CREACION.asc())
        .all()
    )
    return ConversacionResponse(
        id_conversacion=conversacion.ID_CONVERSACION,
        tipo="CLIENTE",
        mensajes=[MensajeChatResponse.model_validate(m) for m in mensajes],
    )


@router.post(
    "/incidents/{id_incidente}/tecnico/mensajes",
    response_model=EnviarMensajeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enviar mensaje al copiloto de taller (técnico asignado)",
)
def enviar_mensaje_tecnico(
    id_incidente: int,
    body: EnviarMensajeTecnicoRequest,
    tecnico: TECNICOS = Depends(get_current_tecnico),
    usuario: USUARIOS = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    incidente = _obtener_incidente_o_404(db, id_incidente)
    verificar_acceso_incidente(usuario, incidente)
    _exigir_tecnico_asignado(db, id_incidente, tecnico)
    _exigir_estado_chat_habilitado(incidente)

    if not body.contenido or not body.contenido.strip():
        raise HTTPException(status_code=422, detail="El mensaje no puede estar vacío")

    conversacion, _ = chat_service.obtener_o_crear_conversacion(db, incidente, "TECNICO")

    mensaje_tecnico = MENSAJES_CHAT(
        ID_CONVERSACION=conversacion.ID_CONVERSACION,
        ROL_EMISOR="TECNICO",
        ID_USUARIO_EMISOR=usuario.ID_USUARIO,
        CONTENIDO=body.contenido.strip(),
    )
    db.add(mensaje_tecnico)
    db.flush()

    respuesta_texto = chat_service.generar_respuesta_tecnico(
        db, incidente, conversacion, body.contenido.strip()
    )

    mensaje_ia = MENSAJES_CHAT(
        ID_CONVERSACION=conversacion.ID_CONVERSACION,
        ROL_EMISOR="IA",
        ID_USUARIO_EMISOR=None,
        CONTENIDO=respuesta_texto,
    )
    db.add(mensaje_ia)
    db.commit()
    db.refresh(mensaje_tecnico)
    db.refresh(mensaje_ia)

    return EnviarMensajeResponse(
        mensaje_usuario=MensajeChatResponse.model_validate(mensaje_tecnico),
        mensaje_ia=MensajeChatResponse.model_validate(mensaje_ia),
    )


@router.get(
    "/incidents/{id_incidente}/tecnico/mensajes",
    response_model=ConversacionResponse,
    summary="Historial del copiloto de taller (técnico asignado/admin)",
    description=(
        "Si el hilo del técnico no existe todavía, se crea junto con el mensaje "
        "de apertura autogenerado por la IA (sugerencia de herramientas/repuestos)."
    ),
)
def obtener_historial_tecnico(
    id_incidente: int,
    usuario: USUARIOS = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    incidente = _obtener_incidente_o_404(db, id_incidente)
    verificar_acceso_incidente(usuario, incidente)

    rol = _rol_texto(usuario)
    if rol == "TECNICO":
        tecnico = (
            db.query(TECNICOS).filter(TECNICOS.ID_USUARIO == usuario.ID_USUARIO).first()
        )
        if tecnico is None:
            raise HTTPException(status_code=404, detail="Perfil de técnico no encontrado")
        _exigir_tecnico_asignado(db, id_incidente, tecnico)
    elif rol != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Solo el técnico asignado o un administrador pueden ver este copiloto",
        )

    conversacion, fue_creada = chat_service.obtener_o_crear_conversacion(db, incidente, "TECNICO")

    if fue_creada:
        _exigir_estado_chat_habilitado(incidente)
        respuesta_apertura = chat_service.generar_respuesta_tecnico(db, incidente, conversacion, None)
        mensaje_ia = MENSAJES_CHAT(
            ID_CONVERSACION=conversacion.ID_CONVERSACION,
            ROL_EMISOR="IA",
            ID_USUARIO_EMISOR=None,
            CONTENIDO=respuesta_apertura,
        )
        db.add(mensaje_ia)
    db.commit()

    mensajes = (
        db.query(MENSAJES_CHAT)
        .filter(MENSAJES_CHAT.ID_CONVERSACION == conversacion.ID_CONVERSACION)
        .order_by(MENSAJES_CHAT.FECHA_CREACION.asc())
        .all()
    )
    return ConversacionResponse(
        id_conversacion=conversacion.ID_CONVERSACION,
        tipo="TECNICO",
        mensajes=[MensajeChatResponse.model_validate(m) for m in mensajes],
    )
