"""
Reporte y consulta de incidentes (solo rol CLIENTE).
Ubicación + evidencias multimodales (imágenes, audio opcional, texto).
"""
import asyncio
import logging
import re
import shutil
import struct
import uuid
from datetime import datetime
from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from geoalchemy2.elements import WKTElement
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.infrastructure.external_services.ai_service import ejecutar_pipeline_procesamiento_incidente
from app.models.models import (
    ASIGNACIONES,
    EVIDENCIAS,
    INCIDENTES,
    TALLERES,
    TECNICOS,
    USUARIOS,
    VEHICULOS,
)
from app.presentation.api.v1.dependencies.auth import get_current_user
from app.presentation.api.v1.schemas.evidence import EvidenceUploadResponse
from app.presentation.api.v1.schemas.incident import (
    EvidenceItemResponse,
    IncidentListResponse,
    IncidentResponse,
    IncidentSyncItem,
    IncidentSyncResponse,
    ReporteIncidenteResponse,
)

router = APIRouter(prefix="/incidents", tags=["Incidentes"])

logger = logging.getLogger(__name__)

MIME_IMAGENES = frozenset(
    {"image/jpeg", "image/png", "image/webp", "image/gif", "image/jpg"}
)
MIME_AUDIO = frozenset(
    {
        "audio/mpeg",
        "audio/mp3",
        "audio/wav",
        "audio/x-wav",
        "audio/webm",
        "audio/ogg",
        "audio/opus",
    }
)


def _rol_texto(usuario: USUARIOS) -> str:
    r = usuario.ROL
    return r.value if hasattr(r, "value") else str(r)


def _solo_cliente(usuario: USUARIOS) -> None:
    if _rol_texto(usuario) != "CLIENTE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los clientes pueden usar este módulo de incidentes",
        )


def _parse_wkb_point(hex_str: str) -> tuple[float, float] | None:
    """
    Decode a 2D WKB/EWKB POINT hex string into (lon, lat) using only the
    stdlib. PostGIS stores geography points as standard WKB, so the bytes the
    WKBElement already holds are enough — no shapely/GEOS round-trip needed.

    Layout: [byte order:1][geom type:4][optional SRID:4][X:8][Y:8]
    """
    try:
        b = bytes.fromhex(hex_str)
    except (ValueError, TypeError):
        return None
    if len(b) < 21:
        return None
    fmt = "<" if b[0] == 1 else ">"
    geom_type = struct.unpack(fmt + "I", b[1:5])[0]
    has_srid = bool(geom_type & 0x20000000)  # EWKB SRID flag
    offset = 5 + (4 if has_srid else 0)
    if len(b) < offset + 16:
        return None
    lon, lat = struct.unpack(fmt + "dd", b[offset:offset + 16])
    return lon, lat


def _coords_desde_orm(inc: INCIDENTES) -> tuple[float | None, float | None]:
    """Return (lat, lon) for an incident, decoding the PostGIS geography point."""
    raw = inc.UBICACION
    if raw is None:
        return None, None

    # Primary: decode the WKB hex carried by the WKBElement (no native deps).
    hex_str = getattr(raw, "desc", None)
    if hex_str is None:
        data = getattr(raw, "data", None)
        if isinstance(data, (bytes, bytearray, memoryview)):
            hex_str = bytes(data).hex()
        elif isinstance(data, str):
            hex_str = data
    if hex_str is None:
        m = re.search(r"[0-9a-fA-F]{40,}", str(raw))
        hex_str = m.group(0) if m else None
    if hex_str:
        coords = _parse_wkb_point(hex_str)
        if coords is not None:
            lon, lat = coords
            return lat, lon

    # Fallback: WKT string "POINT (lon lat)".
    s = str(raw).strip()
    if "POINT" in s.upper():
        nums = re.findall(r"[-+]?\d+\.?\d*", s)
        if len(nums) >= 2:
            return float(nums[1]), float(nums[0])

    logger.warning(
        "No se pudieron extraer coordenadas — incidente %s, tipo=%s",
        inc.ID_INCIDENTE, type(raw).__name__,
    )
    return None, None


def _nombre_seguro(nombre: str | None) -> str:
    base = Path(nombre or "archivo").name
    if not base or ".." in base:
        return "archivo"
    return re.sub(r"[^a-zA-Z0-9._-]", "_", base)[:120]


def _url_temporal_evidencia(id_evidencia: UUID) -> str:
    """URL lógica provisional (reemplazar por bucket/CDN en producción)."""
    return f"temporal:/evidencias/{id_evidencia}"


def _construir_url_evidencia(ev: EVIDENCIAS) -> str:
    """Convierte URL temporal a URL real servida por StaticFiles."""
    url = ev.URL_ARCHIVO or ""
    if url.startswith("temporal:") and ev.CLAVE_ARCHIVO:
        # CLAVE_ARCHIVO = "evidencias/{incidente_id}/{filename}"
        # URL real      = "/static/evidencias/{incidente_id}/{filename}"
        return f"{settings.EVIDENCIAS_URL_PREFIX}/{ev.CLAVE_ARCHIVO.replace('evidencias/', '', 1)}"
    return url


def _a_lista(inc: INCIDENTES) -> IncidentListResponse:
    lat, lon = _coords_desde_orm(inc)
    base = IncidentListResponse.model_validate(inc)
    return base.model_copy(update={"latitud": lat, "longitud": lon})


def _datos_asignacion(db: Session, id_incidente: UUID) -> dict:
    """Devuelve nombre de taller y técnico asignados (si existe asignación)."""
    asign = (
        db.query(ASIGNACIONES)
        .filter(ASIGNACIONES.ID_INCIDENTE == id_incidente)
        .first()
    )
    if not asign:
        return {}
    datos: dict = {}
    if asign.ID_TALLER:
        taller = db.query(TALLERES).filter(TALLERES.ID_TALLER == asign.ID_TALLER).first()
        if taller:
            datos["taller_asignado"] = taller.NOMBRE_NEGOCIO
    if asign.ID_TECNICO:
        tecnico = db.query(TECNICOS).filter(TECNICOS.ID_TECNICO == asign.ID_TECNICO).first()
        if tecnico:
            datos["tecnico_asignado"] = tecnico.NOMBRE_COMPLETO
            datos["tecnico_telefono"] = tecnico.TELEFONO
    return datos


def _a_detalle(db: Session, inc: INCIDENTES, evidencias: list[EVIDENCIAS]) -> IncidentResponse:
    lat, lon = _coords_desde_orm(inc)
    evs = []
    for e in evidencias:
        ev_response = EvidenceItemResponse.model_validate(e)
        ev_response = ev_response.model_copy(update={"url_archivo": _construir_url_evidencia(e)})
        evs.append(ev_response)
    base = IncidentResponse.model_validate(inc)
    update = {"latitud": lat, "longitud": lon, "evidencias": evs}
    update.update(_datos_asignacion(db, inc.ID_INCIDENTE))
    return base.model_copy(update=update)


@router.post(
    "/report",
    response_model=ReporteIncidenteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Reportar incidente multimodal",
    description=(
        "Cliente autenticado envía **multipart/form-data**: `latitud`, `longitud`, campos opcionales, "
        "varias imágenes (`imagenes`) y opcionalmente un `audio`. "
        "Ejemplo numérico: La Paz aprox. latitud `-16.5`, longitud `-68.15`."
    ),
    response_description="ID del incidente y evidencias con URL temporal",
)
async def reportar_incidente_multimodal(
    latitud: Annotated[
        float,
        Form(
            description="Latitud WGS84 (grados decimales, -90..90)",
            examples=[-16.5],
        ),
    ],
    longitud: Annotated[
        float,
        Form(
            description="Longitud WGS84 (grados decimales, -180..180)",
            examples=[-68.15],
        ),
    ],
    id_vehiculo: Annotated[
        UUID | None,
        Form(description="UUID del vehículo registrado del cliente; omitir si no aplica"),
    ] = None,
    prioridad: Annotated[str | None, Form(description="BAJA | MEDIA | ALTA")] = "MEDIA",
    clasificacion: Annotated[
        str | None,
        Form(description="BATERIA | LLANTA | CHOQUE | MOTOR | OTROS | INCIERTO"),
    ] = "OTROS",
    texto_descripcion: Annotated[
        str | None,
        Form(description="Descripción textual si no hay archivos"),
    ] = None,
    id_local: Annotated[
        str | None,
        Form(description="ID local del incidente (para sincronización offline)", max_length=36),
    ] = None,
    imagenes: Annotated[
        list[UploadFile] | None,
        File(description="Una o más imágenes (JPEG, PNG, WEBP, GIF)"),
    ] = None,
    audio: Annotated[
        UploadFile | None,
        File(description="Un solo archivo de audio opcional (MP3, WAV, WEBM, OGG, …)"),
    ] = None,
    usuario: USUARIOS = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Crea **INCIDENTES** y registros en **EVIDENCIAS** con **URL temporal** (`temporal:/evidencias/{id}`).
    Los archivos se guardan en disco bajo `UPLOADS_DIR` para procesamiento interno (IA, antivirus, etc.).
    """
    _solo_cliente(usuario)

    if id_vehiculo is not None:
        v = (
            db.query(VEHICULOS)
            .filter(
                VEHICULOS.ID_VEHICULO == id_vehiculo,
                VEHICULOS.ID_USUARIO_CLIENTE == usuario.ID_USUARIO,
            )
            .first()
        )
        if not v:
            raise HTTPException(status_code=400, detail="El vehículo no existe o no le pertenece")

    imgs = imagenes or []
    tiene_archivos = bool(imgs) or (audio is not None and bool(audio.filename))
    tiene_texto = bool(texto_descripcion and texto_descripcion.strip())
    if not tiene_archivos and not tiene_texto:
        raise HTTPException(
            status_code=400,
            detail="Debe incluir al menos una imagen, un audio o una descripción en texto",
        )

    punto = WKTElement(f"POINT({longitud} {latitud})", srid=4326)
    incidente = INCIDENTES(
        ID_USUARIO_CLIENTE=usuario.ID_USUARIO,
        ID_VEHICULO=id_vehiculo,
        UBICACION=punto,
        PRIORIDAD=prioridad or "MEDIA",
        CLASIFICACION=clasificacion or "OTROS",
        ID_LOCAL=id_local,
        ID_TENANT=getattr(usuario, "_id_tenant", None),
    )
    db.add(incidente)
    db.flush()

    destino_dir = settings.UPLOADS_DIR / "evidencias" / str(incidente.ID_INCIDENTE)
    destino_dir.mkdir(parents=True, exist_ok=True)
    subidas: list[EvidenceUploadResponse] = []

    try:
        for img in imgs:
            if not img.filename:
                continue
            ct = (img.content_type or "").split(";")[0].strip().lower()
            if ct not in MIME_IMAGENES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Tipo de imagen no permitido: {ct or 'desconocido'}",
                )
            eid = uuid.uuid4()
            nombre_disco = f"{eid.hex}_{_nombre_seguro(img.filename)}"
            ruta = destino_dir / nombre_disco
            contenido = await img.read()
            ruta.write_bytes(contenido)
            url_tmp = _url_temporal_evidencia(eid)
            ev = EVIDENCIAS(
                ID_EVIDENCIA=eid,
                ID_INCIDENTE=incidente.ID_INCIDENTE,
                TIPO="IMAGEN",
                URL_ARCHIVO=url_tmp,
                CLAVE_ARCHIVO=f"evidencias/{incidente.ID_INCIDENTE}/{nombre_disco}",
            )
            db.add(ev)
            db.flush()
            subidas.append(
                EvidenceUploadResponse(
                    id_evidencia=eid,
                    tipo="IMAGEN",
                    url_archivo=url_tmp,
                    nombre_original=img.filename,
                )
            )

        if audio is not None and audio.filename:
            ct = (audio.content_type or "").split(";")[0].strip().lower()
            if ct not in MIME_AUDIO:
                raise HTTPException(
                    status_code=400,
                    detail=f"Tipo de audio no permitido: {ct or 'desconocido'}",
                )
            eid = uuid.uuid4()
            nombre_disco = f"{eid.hex}_{_nombre_seguro(audio.filename)}"
            ruta = destino_dir / nombre_disco
            contenido = await audio.read()
            ruta.write_bytes(contenido)
            url_tmp = _url_temporal_evidencia(eid)
            ev = EVIDENCIAS(
                ID_EVIDENCIA=eid,
                ID_INCIDENTE=incidente.ID_INCIDENTE,
                TIPO="AUDIO",
                URL_ARCHIVO=url_tmp,
                CLAVE_ARCHIVO=f"evidencias/{incidente.ID_INCIDENTE}/{nombre_disco}",
            )
            db.add(ev)
            db.flush()
            subidas.append(
                EvidenceUploadResponse(
                    id_evidencia=eid,
                    tipo="AUDIO",
                    url_archivo=url_tmp,
                    nombre_original=audio.filename,
                )
            )

        if tiene_texto:
            eid = uuid.uuid4()
            url_tmp = _url_temporal_evidencia(eid)
            ev_txt = EVIDENCIAS(
                ID_EVIDENCIA=eid,
                ID_INCIDENTE=incidente.ID_INCIDENTE,
                TIPO="TEXTO",
                URL_ARCHIVO=url_tmp,
                CLAVE_ARCHIVO=None,
                TEXTO_TRANSCRITO=texto_descripcion.strip(),
            )
            db.add(ev_txt)
            db.flush()
            subidas.append(
                EvidenceUploadResponse(
                    id_evidencia=eid,
                    tipo="TEXTO",
                    url_archivo=url_tmp,
                    nombre_original=None,
                )
            )

        db.commit()
        db.refresh(incidente)
        try:
            ejecutar_pipeline_procesamiento_incidente(db, incidente.ID_INCIDENTE)
        except Exception:
            logger.exception(
                "Procesamiento IA automático falló tras el reporte; incidente %s persistido.",
                incidente.ID_INCIDENTE,
            )
    except HTTPException:
        db.rollback()
        if destino_dir.exists():
            shutil.rmtree(destino_dir, ignore_errors=True)
        raise
    except Exception:
        db.rollback()
        if destino_dir.exists():
            shutil.rmtree(destino_dir, ignore_errors=True)
        raise

    # Notificar en tiempo real que se reportó un nuevo incidente
    notif = {
        "tipo": "incidente_reportado",
        "incidente_id": str(incidente.ID_INCIDENTE),
        "clasificacion": str(
            incidente.CLASIFICACION.value if hasattr(incidente.CLASIFICACION, "value")
            else incidente.CLASIFICACION
        ),
        "prioridad": str(
            incidente.PRIORIDAD.value if hasattr(incidente.PRIORIDAD, "value")
            else incidente.PRIORIDAD
        ),
        "mensaje": "Nuevo incidente reportado",
        "timestamp": datetime.utcnow().isoformat(),
    }
    try:
        from app.application.use_cases.notification_service import broadcast_global
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(broadcast_global(notif))
    except Exception:
        pass

    return ReporteIncidenteResponse(
        incidente_id=incidente.ID_INCIDENTE,
        evidencias_subidas=subidas,
    )


@router.post(
    "/sync",
    response_model=IncidentSyncResponse,
    status_code=status.HTTP_200_OK,
    summary="Sincronizar incidentes offline (Cliente)",
    description=(
        "Recibe una lista de incidentes creados offline y los persiste evitando duplicados. "
        "Cada item debe incluir `id_local` único por cliente. "
        "Si un incidente con ese `id_local` ya existe para el cliente, se omite."
    ),
)
def sincronizar_incidentes(
    items: list[IncidentSyncItem],
    usuario: USUARIOS = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _solo_cliente(usuario)

    sincronizados = 0
    omitidos = 0
    errores: list[str] = []

    for item in items:
        try:
            existente = (
                db.query(INCIDENTES)
                .filter(
                    INCIDENTES.ID_LOCAL == item.id_local,
                    INCIDENTES.ID_USUARIO_CLIENTE == usuario.ID_USUARIO,
                )
                .first()
            )
            if existente:
                omitidos += 1
                continue

            punto = WKTElement(f"POINT({item.longitud} {item.latitud})", srid=4326)
            incidente = INCIDENTES(
                ID_USUARIO_CLIENTE=usuario.ID_USUARIO,
                ID_VEHICULO=item.id_vehiculo,
                UBICACION=punto,
                PRIORIDAD=item.prioridad or "MEDIA",
                CLASIFICACION=item.clasificacion or "OTROS",
                ID_LOCAL=item.id_local,
                ID_TENANT=getattr(usuario, "_id_tenant", None),
            )
            db.add(incidente)
            db.flush()

            if item.texto_descripcion and item.texto_descripcion.strip():
                eid = uuid.uuid4()
                ev_txt = EVIDENCIAS(
                    ID_EVIDENCIA=eid,
                    ID_INCIDENTE=incidente.ID_INCIDENTE,
                    TIPO="TEXTO",
                    URL_ARCHIVO=_url_temporal_evidencia(eid),
                    CLAVE_ARCHIVO=None,
                    TEXTO_TRANSCRITO=item.texto_descripcion.strip(),
                )
                db.add(ev_txt)

            db.commit()
            sincronizados += 1
        except Exception as exc:
            db.rollback()
            errores.append(f"{item.id_local}: {exc}")

    return IncidentSyncResponse(sincronizados=sincronizados, omitidos=omitidos, errores=errores)


@router.get(
    "",
    response_model=list[IncidentListResponse],
    summary="Listar todos los incidentes (Taller/Admin)",
    description="Lista todos los incidentes. Solo para roles TALLER y ADMIN.",
)
def listar_todos_incidentes(
    estado: str | None = None,
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_user),
):
    rol = _rol_texto(usuario)
    if rol not in ("TALLER", "ADMIN"):
        raise HTTPException(status_code=403, detail="Solo talleres y admins pueden listar todos los incidentes")
    q = db.query(INCIDENTES)
    if estado:
        q = q.filter(INCIDENTES.ESTADO == estado)
    if rol != "ADMIN":
        id_tenant = getattr(usuario, "_id_tenant", None)
        if id_tenant is not None:
            q = q.filter(INCIDENTES.ID_TENANT == id_tenant)
    filas = q.order_by(INCIDENTES.FECHA_CREACION.desc()).all()
    return [_a_lista(inc) for inc in filas]


@router.patch(
    "/{id_incidente}/estado",
    response_model=IncidentListResponse,
    summary="Actualizar estado de incidente (Taller)",
)
def actualizar_estado_incidente(
    id_incidente: UUID,
    body: dict,
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_user),
):
    rol = _rol_texto(usuario)
    if rol not in ("TALLER", "ADMIN"):
        raise HTTPException(status_code=403, detail="Solo talleres pueden actualizar el estado")
    inc = db.query(INCIDENTES).filter(INCIDENTES.ID_INCIDENTE == id_incidente).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")
    nuevo_estado = body.get("estado")
    if nuevo_estado:
        inc.ESTADO = nuevo_estado
    db.commit()
    db.refresh(inc)

    if nuevo_estado == "ATENDIDO":
        try:
            from app.models.models import ASIGNACIONES
            from app.application.use_cases import payment_service
            asignacion = db.query(ASIGNACIONES).filter(ASIGNACIONES.ID_INCIDENTE == id_incidente).first()
            if asignacion:
                pago = payment_service.crear_pago_pendiente(db, inc, asignacion)
                notif = {
                    "tipo": "pago_creado",
                    "pago_id": str(pago.ID_PAGO),
                    "incidente_id": str(id_incidente),
                    "monto": str(pago.MONTO),
                    "mensaje": "Pago generado por incidente atendido",
                    "timestamp": datetime.utcnow().isoformat(),
                }
                try:
                    from app.application.use_cases.notification_service import broadcast_global
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.ensure_future(broadcast_global(notif))
                except Exception:
                    pass
            else:
                logger.warning("No se encontró asignación para incidente %s al crear pago", id_incidente)
        except Exception:
            logger.exception("Error al crear pago automático para incidente %s", id_incidente)

    return _a_lista(inc)


@router.get(
    "/my",
    response_model=list[IncidentListResponse],
    summary="Mis incidentes",
    description="Lista cronológica de incidentes del cliente autenticado (sin evidencias).",
)
def listar_mis_incidentes(
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_user),
):
    rol = _rol_texto(usuario)
    if rol == "CLIENTE":
        filas = (
            db.query(INCIDENTES)
            .filter(INCIDENTES.ID_USUARIO_CLIENTE == usuario.ID_USUARIO)
            .order_by(INCIDENTES.FECHA_CREACION.desc())
            .all()
        )
    elif rol in ("TALLER", "ADMIN"):
        q = db.query(INCIDENTES)
        if rol != "ADMIN":
            id_tenant = getattr(usuario, "_id_tenant", None)
            if id_tenant is not None:
                q = q.filter(INCIDENTES.ID_TENANT == id_tenant)
        filas = q.order_by(INCIDENTES.FECHA_CREACION.desc()).all()
    else:
        raise HTTPException(status_code=403, detail="Rol no autorizado")
    return [_a_lista(inc) for inc in filas]


@router.get(
    "/{id_incidente}",
    response_model=IncidentResponse,
    summary="Detalle de incidente",
    description="Incluye evidencias. El cliente dueño o un TALLER/ADMIN puede consultarlo.",
)
def obtener_incidente(
    id_incidente: UUID,
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_user),
):
    rol = _rol_texto(usuario)
    inc = db.query(INCIDENTES).filter(INCIDENTES.ID_INCIDENTE == id_incidente).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")
    if rol == "CLIENTE" and inc.ID_USUARIO_CLIENTE != usuario.ID_USUARIO:
        raise HTTPException(status_code=403, detail="No autorizado a ver este incidente")

    evs = (
        db.query(EVIDENCIAS)
        .filter(EVIDENCIAS.ID_INCIDENTE == id_incidente)
        .order_by(EVIDENCIAS.FECHA_CREACION)
        .all()
    )
    return _a_detalle(db, inc, evs)
