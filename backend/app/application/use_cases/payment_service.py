"""
Lógica de negocio para el sistema de pagos manuales con QR (CU13).
"""
import logging
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.models import ASIGNACIONES, INCIDENTES, PAGOS, TALLERES, USUARIOS

logger = logging.getLogger(__name__)

# Tarifas base por clasificación (en Bs.)
_TARIFAS_BASE: dict[str, Decimal] = {
    "BATERIA": Decimal("150"),
    "LLANTA": Decimal("100"),
    "CHOQUE": Decimal("300"),
    "MOTOR": Decimal("250"),
    "OTROS": Decimal("120"),
    "INCIERTO": Decimal("120"),
}

_RECARGO_PRIORIDAD_ALTA = Decimal("1.20")
_TASA_COMISION = Decimal("0.15")


def calcular_tarifa(clasificacion: str, prioridad: str) -> tuple[Decimal, Decimal]:
    """
    Calcula monto y comisión según clasificación y prioridad.
    Retorna (monto, comision_plataforma).
    """
    base = _TARIFAS_BASE.get(clasificacion.upper(), Decimal("120"))
    if prioridad.upper() == "ALTA":
        base = (base * _RECARGO_PRIORIDAD_ALTA).quantize(Decimal("0.01"))
    comision = (base * _TASA_COMISION).quantize(Decimal("0.01"))
    return base, comision


def crear_pago_pendiente(db: Session, incidente: INCIDENTES, asignacion: ASIGNACIONES) -> PAGOS:
    """
    Crea registro de pago en estado NO_PAGO al marcar incidente como ATENDIDO.
    Si ya existe un pago para el incidente, lo devuelve sin duplicar.
    """
    pago_existente = db.query(PAGOS).filter(PAGOS.ID_INCIDENTE == incidente.ID_INCIDENTE).first()
    if pago_existente:
        return pago_existente

    clasificacion = (
        incidente.CLASIFICACION.value if hasattr(incidente.CLASIFICACION, "value")
        else str(incidente.CLASIFICACION)
    )
    prioridad = (
        incidente.PRIORIDAD.value if hasattr(incidente.PRIORIDAD, "value")
        else str(incidente.PRIORIDAD)
    )
    monto, comision = calcular_tarifa(clasificacion, prioridad)

    pago = PAGOS(
        ID_INCIDENTE=incidente.ID_INCIDENTE,
        ID_USUARIO_CLIENTE=incidente.ID_USUARIO_CLIENTE,
        ID_TALLER=asignacion.ID_TALLER,
        ID_ASIGNACION=asignacion.ID_ASIGNACION,
        MONTO=monto,
        COMISION_PLATAFORMA=comision,
        ESTADO="NO_PAGO",
        ID_TENANT=incidente.ID_TENANT,
    )
    db.add(pago)
    db.commit()
    db.refresh(pago)
    logger.info(
        "Pago creado para incidente %s: monto=%.2f comision=%.2f",
        incidente.ID_INCIDENTE, monto, comision,
    )
    return pago


def marcar_como_pagado(
    db: Session,
    id_pago: UUID,
    id_usuario_cliente: UUID,
    comprobante_url: str,
    comprobante_clave: str,
    notas: str | None,
) -> PAGOS:
    """
    El cliente sube el comprobante. Cambia estado NO_PAGO → PENDIENTE.
    """
    pago = db.query(PAGOS).filter(PAGOS.ID_PAGO == id_pago).first()
    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")

    if pago.ID_USUARIO_CLIENTE != id_usuario_cliente:
        raise HTTPException(status_code=403, detail="No autorizado a modificar este pago")

    estado_actual = pago.ESTADO.value if hasattr(pago.ESTADO, "value") else str(pago.ESTADO)
    if estado_actual != "NO_PAGO":
        raise HTTPException(
            status_code=409,
            detail=f"El pago debe estar en estado NO_PAGO para subir comprobante. Estado actual: {estado_actual}",
        )

    pago.COMPROBANTE_URL = comprobante_url
    pago.COMPROBANTE_CLAVE = comprobante_clave
    pago.NOTAS_CLIENTE = notas
    pago.ESTADO = "PENDIENTE"
    pago.FECHA_MARCADO_PAGO = datetime.now(timezone.utc)
    db.commit()
    db.refresh(pago)
    return pago


def confirmar_pago(db: Session, id_pago: UUID, id_usuario_confirma: UUID) -> PAGOS:
    """
    Taller o admin confirma el comprobante. Cambia estado PENDIENTE → PAGADO.
    """
    pago = db.query(PAGOS).filter(PAGOS.ID_PAGO == id_pago).first()
    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")

    usuario = db.query(USUARIOS).filter(USUARIOS.ID_USUARIO == id_usuario_confirma).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    rol = usuario.ROL.value if hasattr(usuario.ROL, "value") else str(usuario.ROL)

    if rol == "TALLER":
        taller = db.query(TALLERES).filter(TALLERES.ID_USUARIO == id_usuario_confirma).first()
        if not taller or taller.ID_TALLER != pago.ID_TALLER:
            raise HTTPException(status_code=403, detail="Solo el taller asignado puede confirmar este pago")
    elif rol != "ADMIN":
        raise HTTPException(status_code=403, detail="Solo talleres y admins pueden confirmar pagos")

    estado_actual = pago.ESTADO.value if hasattr(pago.ESTADO, "value") else str(pago.ESTADO)
    if estado_actual != "PENDIENTE":
        raise HTTPException(
            status_code=409,
            detail=f"El pago debe estar en estado PENDIENTE para confirmar. Estado actual: {estado_actual}",
        )

    pago.ESTADO = "PAGADO"
    pago.FECHA_CONFIRMACION = datetime.now(timezone.utc)
    pago.ID_USUARIO_CONFIRMO = id_usuario_confirma
    db.commit()
    db.refresh(pago)
    return pago


def rechazar_pago(db: Session, id_pago: UUID, id_usuario_confirma: UUID, motivo: str) -> PAGOS:
    """
    Taller o admin rechaza el comprobante. Vuelve a NO_PAGO para permitir reintento.
    Limpia el comprobante anterior.
    """
    pago = db.query(PAGOS).filter(PAGOS.ID_PAGO == id_pago).first()
    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")

    usuario = db.query(USUARIOS).filter(USUARIOS.ID_USUARIO == id_usuario_confirma).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    rol = usuario.ROL.value if hasattr(usuario.ROL, "value") else str(usuario.ROL)

    if rol == "TALLER":
        taller = db.query(TALLERES).filter(TALLERES.ID_USUARIO == id_usuario_confirma).first()
        if not taller or taller.ID_TALLER != pago.ID_TALLER:
            raise HTTPException(status_code=403, detail="Solo el taller asignado puede rechazar este pago")
    elif rol != "ADMIN":
        raise HTTPException(status_code=403, detail="Solo talleres y admins pueden rechazar pagos")

    estado_actual = pago.ESTADO.value if hasattr(pago.ESTADO, "value") else str(pago.ESTADO)
    if estado_actual != "PENDIENTE":
        raise HTTPException(
            status_code=409,
            detail=f"El pago debe estar en estado PENDIENTE para rechazar. Estado actual: {estado_actual}",
        )

    pago.ESTADO = "NO_PAGO"
    pago.FECHA_RECHAZO = datetime.now(timezone.utc)
    pago.MOTIVO_RECHAZO = motivo
    # Limpiar comprobante para que el cliente pueda subir uno nuevo
    pago.COMPROBANTE_URL = None
    pago.COMPROBANTE_CLAVE = None
    pago.FECHA_MARCADO_PAGO = None
    db.commit()
    db.refresh(pago)
    return pago


def obtener_estadisticas(db: Session, id_taller: UUID | None = None) -> dict:
    """
    Retorna estadísticas de pagos. Si id_taller es None, stats globales (admin).
    """
    query = db.query(PAGOS)
    if id_taller:
        query = query.filter(PAGOS.ID_TALLER == id_taller)

    pagos = query.all()

    count_por_estado: dict[str, int] = {"NO_PAGO": 0, "PENDIENTE": 0, "PAGADO": 0, "RECHAZADO": 0}
    total_cobrado = Decimal("0")
    total_pendiente = Decimal("0")
    total_no_pago = Decimal("0")

    for p in pagos:
        estado = p.ESTADO.value if hasattr(p.ESTADO, "value") else str(p.ESTADO)
        count_por_estado[estado] = count_por_estado.get(estado, 0) + 1
        if estado == "PAGADO":
            total_cobrado += Decimal(str(p.MONTO))
        elif estado == "PENDIENTE":
            total_pendiente += Decimal(str(p.MONTO))
        elif estado == "NO_PAGO":
            total_no_pago += Decimal(str(p.MONTO))

    return {
        "total_cobrado": total_cobrado,
        "total_pendiente": total_pendiente,
        "total_no_pago": total_no_pago,
        "count_por_estado": count_por_estado,
    }
