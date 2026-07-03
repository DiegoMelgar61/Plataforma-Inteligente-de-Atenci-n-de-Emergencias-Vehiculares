"""
Router del sistema de pagos manuales con QR (CU13).
Tags = ["Pagos"]
"""
import asyncio
import logging
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.application.use_cases import payment_service
from app.models.models import ASIGNACIONES, INCIDENTES, PAGOS
from app.modules.workshops.models import TALLERES
from app.modules.users.models import USUARIOS
from app.modules.auth.dependencies import get_current_user
from app.presentation.api.v1.schemas.payment import (
    PaymentListItem,
    PaymentReject,
    PaymentResponse,
    PaymentStats,
)

router = APIRouter(prefix="/payments", tags=["Pagos"])

logger = logging.getLogger(__name__)

MIME_IMAGENES_COMPROBANTE = frozenset(
    {"image/jpeg", "image/png", "image/webp", "image/jpg", "application/pdf"}
)


def _rol_texto(usuario: USUARIOS) -> str:
    r = usuario.ROL
    return r.value if hasattr(r, "value") else str(r)


def _nombre_seguro(nombre: str | None) -> str:
    base = Path(nombre or "comprobante").name
    if not base or ".." in base:
        return "comprobante"
    return re.sub(r"[^a-zA-Z0-9._-]", "_", base)[:120]


def _construir_url_comprobante(clave: str) -> str:
    """Convierte clave de disco a URL pública vía StaticFiles."""
    # clave = "comprobantes/{id_pago}/{filename}"
    # URL   = "/static/comprobantes/{id_pago}/{filename}"
    return f"{settings.COMPROBANTES_URL_PREFIX}/{clave.replace('comprobantes/', '', 1)}"


def _taller_de_usuario(db: Session, usuario: USUARIOS) -> TALLERES | None:
    return db.query(TALLERES).filter(TALLERES.ID_USUARIO == usuario.ID_USUARIO).first()


async def _guardar_comprobante(comprobante: UploadFile, id_pago: UUID) -> tuple[str, str]:
    """
    Guarda el archivo en disco y retorna (url, clave).
    Lanza HTTPException si el tipo MIME no está permitido.
    """
    ct = (comprobante.content_type or "").split(";")[0].strip().lower()
    if ct not in MIME_IMAGENES_COMPROBANTE:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no permitido: {ct or 'desconocido'}. Use JPEG, PNG, WEBP o PDF.",
        )
    destino_dir = settings.UPLOADS_DIR / "comprobantes" / str(id_pago)
    destino_dir.mkdir(parents=True, exist_ok=True)
    nombre_disco = f"{uuid.uuid4().hex}_{_nombre_seguro(comprobante.filename)}"
    ruta = destino_dir / nombre_disco
    contenido = await comprobante.read()
    ruta.write_bytes(contenido)
    clave = f"comprobantes/{id_pago}/{nombre_disco}"
    url = _construir_url_comprobante(clave)
    return url, clave


async def _broadcast(datos: dict) -> None:
    try:
        from app.application.use_cases.notification_service import broadcast_global
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(broadcast_global(datos))
    except Exception:
        pass


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get(
    "/stats",
    response_model=PaymentStats,
    summary="Estadísticas de pagos (Taller/Admin)",
)
def obtener_stats(
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_user),
):
    rol = _rol_texto(usuario)
    if rol not in ("TALLER", "ADMIN"):
        raise HTTPException(status_code=403, detail="Solo talleres y admins pueden ver estadísticas")

    id_taller = None
    if rol == "TALLER":
        taller = _taller_de_usuario(db, usuario)
        if not taller:
            raise HTTPException(status_code=404, detail="Taller no encontrado para este usuario")
        id_taller = taller.ID_TALLER

    stats = payment_service.obtener_estadisticas(db, id_taller=id_taller)
    return PaymentStats(**stats)


@router.get(
    "/my",
    response_model=list[PaymentListItem],
    summary="Mis pagos",
    description="CLIENTE: sus pagos. TALLER: pagos de su taller. ADMIN: todos.",
)
def listar_mis_pagos(
    estado: str | None = None,
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_user),
):
    rol = _rol_texto(usuario)
    query = db.query(PAGOS)

    if rol == "CLIENTE":
        query = query.filter(PAGOS.ID_USUARIO_CLIENTE == usuario.ID_USUARIO)
    elif rol == "TALLER":
        taller = _taller_de_usuario(db, usuario)
        if not taller:
            raise HTTPException(status_code=404, detail="Taller no encontrado")
        query = query.filter(PAGOS.ID_TALLER == taller.ID_TALLER)
    elif rol == "ADMIN":
        pass
    else:
        raise HTTPException(status_code=403, detail="Rol no autorizado")

    if rol != "ADMIN":
        id_tenant = getattr(usuario, "_id_tenant", None)
        if id_tenant is not None:
            query = query.filter(PAGOS.ID_TENANT == id_tenant)

    if estado:
        query = query.filter(PAGOS.ESTADO == estado)

    pagos = query.order_by(PAGOS.FECHA_CREACION.desc()).all()
    return [PaymentListItem.model_validate(p) for p in pagos]


@router.get(
    "",
    response_model=list[PaymentListItem],
    summary="Todos los pagos (Taller/Admin)",
)
def listar_pagos(
    estado: str | None = None,
    id_taller: UUID | None = None,
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_user),
):
    rol = _rol_texto(usuario)
    if rol not in ("TALLER", "ADMIN"):
        raise HTTPException(status_code=403, detail="Solo talleres y admins pueden listar todos los pagos")

    query = db.query(PAGOS)

    if rol == "TALLER":
        taller = _taller_de_usuario(db, usuario)
        if not taller:
            raise HTTPException(status_code=404, detail="Taller no encontrado")
        query = query.filter(PAGOS.ID_TALLER == taller.ID_TALLER)
    elif id_taller:
        query = query.filter(PAGOS.ID_TALLER == id_taller)

    if rol != "ADMIN":
        id_tenant = getattr(usuario, "_id_tenant", None)
        if id_tenant is not None:
            query = query.filter(PAGOS.ID_TENANT == id_tenant)

    if estado:
        query = query.filter(PAGOS.ESTADO == estado)

    pagos = query.order_by(PAGOS.FECHA_CREACION.desc()).all()
    return [PaymentListItem.model_validate(p) for p in pagos]


@router.get(
    "/{id_pago}",
    response_model=PaymentResponse,
    summary="Detalle de pago",
)
def obtener_pago(
    id_pago: UUID,
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_user),
):
    pago = db.query(PAGOS).filter(PAGOS.ID_PAGO == id_pago).first()
    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")

    rol = _rol_texto(usuario)
    if rol == "CLIENTE" and pago.ID_USUARIO_CLIENTE != usuario.ID_USUARIO:
        raise HTTPException(status_code=403, detail="No autorizado a ver este pago")
    if rol == "TALLER":
        taller = _taller_de_usuario(db, usuario)
        if not taller or taller.ID_TALLER != pago.ID_TALLER:
            raise HTTPException(status_code=403, detail="No autorizado a ver este pago")

    return PaymentResponse.model_validate(pago)


@router.post(
    "/{id_pago}/mark-paid",
    response_model=PaymentResponse,
    status_code=status.HTTP_200_OK,
    summary="Subir comprobante de pago (Cliente)",
)
async def marcar_pago(
    id_pago: UUID,
    comprobante: Annotated[UploadFile, File(description="Imagen o PDF del comprobante de transferencia")],
    notas_cliente: Annotated[str | None, Form(description="Notas opcionales del cliente")] = None,
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_user),
):
    if _rol_texto(usuario) != "CLIENTE":
        raise HTTPException(status_code=403, detail="Solo los clientes pueden subir comprobantes")

    url, clave = await _guardar_comprobante(comprobante, id_pago)

    pago = payment_service.marcar_como_pagado(
        db,
        id_pago=id_pago,
        id_usuario_cliente=usuario.ID_USUARIO,
        comprobante_url=url,
        comprobante_clave=clave,
        notas=notas_cliente,
    )

    await _broadcast({
        "tipo": "pago_pendiente",
        "pago_id": str(pago.ID_PAGO),
        "incidente_id": str(pago.ID_INCIDENTE),
        "mensaje": "El cliente ha subido un comprobante de pago",
        "timestamp": datetime.utcnow().isoformat(),
    })

    return PaymentResponse.model_validate(pago)


@router.post(
    "/{id_pago}/confirm",
    response_model=PaymentResponse,
    status_code=status.HTTP_200_OK,
    summary="Confirmar pago (Taller/Admin)",
)
async def confirmar_pago(
    id_pago: UUID,
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_user),
):
    if _rol_texto(usuario) not in ("TALLER", "ADMIN"):
        raise HTTPException(status_code=403, detail="Solo talleres y admins pueden confirmar pagos")

    pago = payment_service.confirmar_pago(db, id_pago=id_pago, id_usuario_confirma=usuario.ID_USUARIO)

    from app.modules.bitacora import service as bitacora_service
    bitacora_service.registrar(
        "PAGO_CONFIRMADO",
        f"Pago Bs.{pago.MONTO} confirmado",
        usuario=usuario,
        entidad="PAGO",
        id_entidad=pago.ID_PAGO,
    )

    await _broadcast({
        "tipo": "pago_confirmado",
        "pago_id": str(pago.ID_PAGO),
        "incidente_id": str(pago.ID_INCIDENTE),
        "mensaje": "El pago ha sido confirmado",
        "timestamp": datetime.utcnow().isoformat(),
    })

    return PaymentResponse.model_validate(pago)


@router.post(
    "/{id_pago}/reject",
    response_model=PaymentResponse,
    status_code=status.HTTP_200_OK,
    summary="Rechazar comprobante (Taller/Admin)",
)
async def rechazar_pago(
    id_pago: UUID,
    body: PaymentReject,
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_user),
):
    if _rol_texto(usuario) not in ("TALLER", "ADMIN"):
        raise HTTPException(status_code=403, detail="Solo talleres y admins pueden rechazar pagos")

    pago = payment_service.rechazar_pago(
        db,
        id_pago=id_pago,
        id_usuario_confirma=usuario.ID_USUARIO,
        motivo=body.motivo_rechazo,
    )

    from app.modules.bitacora import service as bitacora_service
    bitacora_service.registrar(
        "PAGO_RECHAZADO",
        f"Pago Bs.{pago.MONTO} rechazado: {body.motivo_rechazo}",
        usuario=usuario,
        entidad="PAGO",
        id_entidad=pago.ID_PAGO,
    )

    await _broadcast({
        "tipo": "pago_rechazado",
        "pago_id": str(pago.ID_PAGO),
        "incidente_id": str(pago.ID_INCIDENTE),
        "motivo": body.motivo_rechazo,
        "mensaje": "El comprobante de pago fue rechazado",
        "timestamp": datetime.utcnow().isoformat(),
    })

    return PaymentResponse.model_validate(pago)
