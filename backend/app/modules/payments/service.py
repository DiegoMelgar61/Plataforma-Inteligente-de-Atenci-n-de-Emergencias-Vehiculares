"""
Lógica de negocio para el sistema de pagos manuales con QR (CU13).
"""
import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.models import ASIGNACIONES, INCIDENTES
from app.modules.payments.models import PAGOS
from app.modules.users.models import USUARIOS
from app.modules.workshops.models import TALLERES

logger = logging.getLogger(__name__)

# Zona horaria de Bolivia (UTC-4, sin horario de verano) para las franjas horarias.
_TZ_BOLIVIA = timezone(timedelta(hours=-4))

# --- Parámetros de tarificación (todos editables acá) -----------------------

# Tarifa base por clasificación / tipo de problema (en Bs.)
_TARIFAS_BASE: dict[str, Decimal] = {
    "BATERIA": Decimal("150"),
    "LLANTA": Decimal("100"),
    "CHOQUE": Decimal("300"),
    "MOTOR": Decimal("250"),
    "OTROS": Decimal("120"),
    "INCIERTO": Decimal("120"),
}

# Multiplicador por gravedad/urgencia (prioridad del incidente)
_RECARGO_PRIORIDAD: dict[str, Decimal] = {
    "ALTA": Decimal("1.20"),
    "MEDIA": Decimal("1.00"),
    "BAJA": Decimal("0.90"),
}

# Multiplicador por franja horaria del servicio
_RECARGO_HORA_NOCTURNA = Decimal("1.35")  # 21:00–05:59
_RECARGO_HORA_PICO = Decimal("1.25")      # 07:00–08:59 y 18:00–20:59
_RECARGO_HORA_NORMAL = Decimal("1.00")    # resto del día

_TASA_COMISION = Decimal("0.15")

# Recargo de traslado por km de distancia del taller al incidente. Es lo que
# diferencia la oferta de cada taller (más lejos = más caro), estilo InDrive.
_RECARGO_POR_KM = Decimal("8")

# Multa por cancelar el servicio cuando el técnico ya está en camino: 20% del
# monto cotizado. El cliente queda bloqueado para nuevos pedidos hasta pagarla.
_MULTA_PORCENTAJE = Decimal("0.20")
# Marcador en METODO_PAGO para distinguir una multa de un pago de servicio.
METODO_MULTA = "MULTA"

# ---------------------------------------------------------------------------


def _factor_horario(momento: datetime) -> tuple[Decimal, str]:
    """Devuelve (multiplicador, etiqueta) según la hora local del servicio."""
    hora = momento.astimezone(_TZ_BOLIVIA).hour
    if hora >= 21 or hora < 6:
        return _RECARGO_HORA_NOCTURNA, "nocturna"
    if (7 <= hora < 9) or (18 <= hora < 21):
        return _RECARGO_HORA_PICO, "pico"
    return _RECARGO_HORA_NORMAL, "normal"


def calcular_tarifa(
    clasificacion: str,
    prioridad: str,
    momento: datetime | None = None,
) -> tuple[Decimal, Decimal]:
    """
    Calcula monto y comisión según tipo de problema, gravedad (prioridad) y
    franja horaria del servicio. Determinístico y auditable.

    Retorna (monto, comision_plataforma).
    """
    monto, comision, _ = cotizar(clasificacion, prioridad, momento)
    return monto, comision


def cotizar(
    clasificacion: str,
    prioridad: str,
    momento: datetime | None = None,
) -> tuple[Decimal, Decimal, str]:
    """
    Igual que calcular_tarifa pero también devuelve un detalle legible del cálculo.

    Retorna (monto, comision_plataforma, detalle).
    """
    momento = momento or datetime.now(timezone.utc)
    base = _TARIFAS_BASE.get(clasificacion.upper(), Decimal("120"))
    factor_prio = _RECARGO_PRIORIDAD.get(prioridad.upper(), Decimal("1.00"))
    factor_hora, etiqueta_hora = _factor_horario(momento)

    monto = (base * factor_prio * factor_hora).quantize(Decimal("0.01"))
    comision = (monto * _TASA_COMISION).quantize(Decimal("0.01"))

    detalle = (
        f"Tarifa automática — base {clasificacion.upper()} Bs.{base}, "
        f"prioridad {prioridad.upper()} x{factor_prio}, "
        f"franja {etiqueta_hora} x{factor_hora}. Total Bs.{monto}."
    )
    return monto, comision, detalle


def cotizar_oferta(
    clasificacion: str,
    prioridad: str,
    distancia_km: float,
    momento: datetime | None = None,
) -> tuple[Decimal, str]:
    """
    Cotización de un taller concreto para el flujo de ofertas (estilo InDrive).

    Igual que `cotizar` (problema + gravedad + franja horaria) más un recargo de
    traslado proporcional a la distancia del taller al incidente, que es lo que
    hace que cada taller ofrezca un precio distinto según su ubicación.

    Retorna (monto, descripcion_corta).
    """
    momento = momento or datetime.now(timezone.utc)
    base = _TARIFAS_BASE.get(clasificacion.upper(), Decimal("120"))
    factor_prio = _RECARGO_PRIORIDAD.get(prioridad.upper(), Decimal("1.00"))
    factor_hora, etiqueta_hora = _factor_horario(momento)

    subtotal = (base * factor_prio * factor_hora).quantize(Decimal("0.01"))
    km = round(max(0.0, float(distancia_km)), 1)
    fee = (Decimal(str(km)) * _RECARGO_POR_KM).quantize(Decimal("0.01"))
    monto = (subtotal + fee).quantize(Decimal("0.01"))

    descripcion = (
        f"Bs.{subtotal} por {clasificacion.lower()} (franja {etiqueta_hora}) "
        f"+ Bs.{fee} de traslado ({km} km)"
    )
    return monto, descripcion


def cliente_tiene_multa_pendiente(db: Session, id_usuario_cliente) -> bool:
    """True si el cliente tiene alguna multa sin pagar (bloquea nuevos pedidos)."""
    existe = (
        db.query(PAGOS.ID_PAGO)
        .filter(
            PAGOS.ID_USUARIO_CLIENTE == id_usuario_cliente,
            PAGOS.METODO_PAGO == METODO_MULTA,
            PAGOS.ESTADO != "PAGADO",
        )
        .first()
    )
    return existe is not None


def crear_multa_cancelacion(
    db: Session, incidente: INCIDENTES, asignacion: ASIGNACIONES | None
) -> PAGOS:
    """
    Registra una multa (20% del monto cotizado) como un PAGOS en estado NO_PAGO
    marcado con METODO_PAGO=MULTA. El cliente la paga con el flujo de pagos normal.
    """
    base = None
    if asignacion is not None and asignacion.MONTO_COTIZADO is not None:
        base = Decimal(str(asignacion.MONTO_COTIZADO))
    if base is None:
        clasificacion = (
            incidente.CLASIFICACION.value if hasattr(incidente.CLASIFICACION, "value")
            else str(incidente.CLASIFICACION)
        )
        prioridad = (
            incidente.PRIORIDAD.value if hasattr(incidente.PRIORIDAD, "value")
            else str(incidente.PRIORIDAD)
        )
        base, _ = calcular_tarifa(clasificacion, prioridad)

    monto_multa = (base * _MULTA_PORCENTAJE).quantize(Decimal("0.01"))

    pago = PAGOS(
        ID_INCIDENTE=incidente.ID_INCIDENTE,
        ID_USUARIO_CLIENTE=incidente.ID_USUARIO_CLIENTE,
        ID_TALLER=asignacion.ID_TALLER if asignacion else None,
        ID_ASIGNACION=asignacion.ID_ASIGNACION if asignacion else None,
        MONTO=monto_multa,
        COMISION_PLATAFORMA=Decimal("0.00"),
        ESTADO="NO_PAGO",
        METODO_PAGO=METODO_MULTA,
        NOTAS_CLIENTE="Multa por cancelar el servicio cuando el técnico ya estaba en camino (20%).",
        ID_TENANT=incidente.ID_TENANT,
    )
    db.add(pago)
    db.flush()
    logger.info(
        "Multa creada para cliente %s, incidente %s: Bs.%s",
        incidente.ID_USUARIO_CLIENTE, incidente.ID_INCIDENTE, monto_multa,
    )
    return pago


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
    # Preferir el monto ya cotizado automáticamente al asignar; recalcular solo si falta.
    if asignacion.MONTO_COTIZADO is not None:
        monto = Decimal(str(asignacion.MONTO_COTIZADO))
        comision = (monto * _TASA_COMISION).quantize(Decimal("0.01"))
    else:
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
