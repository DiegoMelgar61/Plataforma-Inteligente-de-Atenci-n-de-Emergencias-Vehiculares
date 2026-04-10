"""
Router de pagos e ingresos por incidentes atendidos.
Calcula automáticamente la comisión del 10% de la plataforma.
Tags = ["Pagos"]
"""
import logging
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import INCIDENTES, PAGOS, USUARIOS
from app.presentation.api.v1.dependencies.auth import get_current_user
from app.presentation.api.v1.schemas.payment import PaymentCreate, PaymentResponse

router = APIRouter(prefix="/payments", tags=["Pagos"])

logger = logging.getLogger(__name__)

# Porcentaje de comisión de la plataforma
COMISION_PORCENTAJE = Decimal("10")


def _rol_texto(usuario: USUARIOS) -> str:
    """Obtiene el rol como string."""
    r = usuario.ROL
    return r.value if hasattr(r, "value") else str(r)


def _calcular_comision(monto: Decimal) -> Decimal:
    """
    Calcula la comisión de la plataforma (10% del monto).

    :param monto: Monto total
    :return: Comisión calculada
    """
    return (monto * COMISION_PORCENTAJE / Decimal("100")).quantize(Decimal("0.01"))


@router.post(
    "/incidents/{id_incidente}/pay",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear pago para incidente",
    description=(
        "Cliente paga por un incidente atendido. "
        "La comisión del 10% se calcula automáticamente y se cobra a la plataforma."
    ),
    response_description="Pago registrado satisfactoriamente",
)
def crear_pago_incidente(
    id_incidente: UUID,
    datos: PaymentCreate,
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_user),
):
    """
    Crea un pago para un incidente atendido. Solo el cliente (propietario del incidente)
    puede realizar el pago.

    **Cálculo de comisión:**
    - Comisión = Monto * 10% (redondeado a 2 decimales)
    - El monto y comisión se registran en la tabla PAGOS

    **Estados válidos para pago:**
    - ATENDIDO (incidente completado y listo para pago)

    **Parámetros:**
    - `id_incidente` (UUID): ID del incidente
    - `monto` (Decimal): Monto total a pagar
    - `metodo_pago` (str, opcional): Método de pago (TARJETA, TRANSFERENCIA, etc.)
    """
    # Verificar que el usuario es cliente
    rol = _rol_texto(usuario)
    if rol != "CLIENTE":
        raise HTTPException(
            status_code=403,
            detail="Solo los clientes pueden realizar pagos",
        )

    # Verificar que el incidente existe
    incidente = (
        db.query(INCIDENTES).filter(INCIDENTES.ID_INCIDENTE == id_incidente).first()
    )
    if not incidente:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")

    # Verificar que el cliente es propietario del incidente
    if incidente.ID_USUARIO_CLIENTE != usuario.ID_USUARIO:
        raise HTTPException(
            status_code=403,
            detail="No autorizado a pagar este incidente",
        )

    # Verificar que el incidente está atendido
    estado_incidente = (
        incidente.ESTADO.value if hasattr(incidente.ESTADO, "value")
        else str(incidente.ESTADO)
    )
    if estado_incidente != "ATENDIDO":
        raise HTTPException(
            status_code=400,
            detail=f"El incidente debe estar ATENDIDO para pagar. Estado actual: {estado_incidente}",
        )

    # Verificar que no existe un pago pagado previamente
    pago_existente = (
        db.query(PAGOS)
        .filter(
            PAGOS.ID_INCIDENTE == id_incidente,
            PAGOS.ESTADO == "PAGADO",
        )
        .first()
    )
    if pago_existente:
        raise HTTPException(
            status_code=400,
            detail="Este incidente ya ha sido pagado",
        )

    # Calcular comisión
    monto = Decimal(str(datos.monto))
    comision = _calcular_comision(monto)

    try:
        # Crear registro de pago
        pago = PAGOS(
            ID_INCIDENTE=id_incidente,
            ID_USUARIO_CLIENTE=usuario.ID_USUARIO,
            MONTO=monto,
            COMISION_PLATAFORMA=comision,
            ESTADO="PAGADO",  # En un sistema real, pasaría por procesador de pagos
            METODO_PAGO=datos.metodo_pago,
            ID_TRANSACCION=None,  # Stub: en producción vendría de pasarela de pagos
        )
        db.add(pago)
        db.commit()
        db.refresh(pago)

        logger.info(
            "Pago registrado: incidente %s, monto %.2f, comisión %.2f",
            id_incidente,
            monto,
            comision,
        )

        return PaymentResponse.model_validate(pago)

    except Exception as e:
        logger.exception("Error al crear pago para incidente %s", id_incidente)
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error al procesar el pago",
        )


@router.get(
    "/my",
    response_model=list[PaymentResponse],
    summary="Mis pagos",
    description="Lista de pagos realizados por el cliente autenticado.",
    response_description="Listado de pagos del cliente",
)
def listar_mis_pagos(
    estado: str | None = None,
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_user),
):
    """
    Obtiene el historial de pagos del cliente autenticado.

    **Parámetro query:**
    - `estado` (str, opcional): Filtrar por estado (PENDIENTE, PAGADO, RECHAZADO)

    **Respuesta:**
    Listado de pagos ordenados por fecha de creación (más recientes primero).

    ```json
    [
        {
            "id_pago": "uuid",
            "id_incidente": "uuid",
            "monto": 100.00,
            "comision_plataforma": 10.00,
            "estado": "PAGADO",
            "fecha_creacion": "2026-04-05T12:00:00"
        }
    ]
    ```
    """
    # Verificar que el usuario es cliente
    rol = _rol_texto(usuario)
    if rol != "CLIENTE":
        raise HTTPException(
            status_code=403,
            detail="Solo los clientes pueden consultar sus pagos",
        )

    query = db.query(PAGOS).filter(PAGOS.ID_USUARIO_CLIENTE == usuario.ID_USUARIO)

    if estado:
        query = query.filter(PAGOS.ESTADO == estado)

    pagos = query.order_by(PAGOS.FECHA_CREACION.desc()).all()

    return [PaymentResponse.model_validate(p) for p in pagos]
