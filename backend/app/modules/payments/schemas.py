"""
Esquemas Pydantic para el sistema de pagos manuales con QR (CU13).
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class PaymentEstadoEnum(str, Enum):
    NO_PAGO = "NO_PAGO"
    PENDIENTE = "PENDIENTE"
    PAGADO = "PAGADO"
    RECHAZADO = "RECHAZADO"


class PaymentCreate(BaseModel):
    """Creación interna de pago (usada por payment_service)."""
    monto: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    comision_plataforma: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)
    id_taller: int
    id_asignacion: int


class PaymentMarkPaid(BaseModel):
    notas_cliente: str | None = Field(None, max_length=1000)


class PaymentConfirm(BaseModel):
    pass


class PaymentReject(BaseModel):
    motivo_rechazo: str = Field(..., min_length=1, max_length=500)


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_pago: int = Field(validation_alias="ID_PAGO")
    id_incidente: int = Field(validation_alias="ID_INCIDENTE")
    id_usuario_cliente: int = Field(validation_alias="ID_USUARIO_CLIENTE")
    id_taller: int | None = Field(None, validation_alias="ID_TALLER")
    id_asignacion: int | None = Field(None, validation_alias="ID_ASIGNACION")
    monto: Decimal = Field(validation_alias="MONTO")
    comision_plataforma: Decimal = Field(validation_alias="COMISION_PLATAFORMA")
    estado: str = Field(validation_alias="ESTADO")
    metodo_pago: str | None = Field(None, validation_alias="METODO_PAGO")
    id_transaccion: str | None = Field(None, validation_alias="ID_TRANSACCION")
    comprobante_url: str | None = Field(None, validation_alias="COMPROBANTE_URL")
    notas_cliente: str | None = Field(None, validation_alias="NOTAS_CLIENTE")
    fecha_creacion: datetime | None = Field(None, validation_alias="FECHA_CREACION")
    fecha_marcado_pago: datetime | None = Field(None, validation_alias="FECHA_MARCADO_PAGO")
    fecha_confirmacion: datetime | None = Field(None, validation_alias="FECHA_CONFIRMACION")
    fecha_rechazo: datetime | None = Field(None, validation_alias="FECHA_RECHAZO")
    motivo_rechazo: str | None = Field(None, validation_alias="MOTIVO_RECHAZO")
    id_usuario_confirmo: int | None = Field(None, validation_alias="ID_USUARIO_CONFIRMO")
    fecha_actualizacion: datetime | None = Field(None, validation_alias="FECHA_ACTUALIZACION")
    id_tenant: int | None = Field(None, validation_alias="ID_TENANT")


class PaymentListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_pago: int = Field(validation_alias="ID_PAGO")
    id_incidente: int = Field(validation_alias="ID_INCIDENTE")
    estado: str = Field(validation_alias="ESTADO")
    monto: Decimal = Field(validation_alias="MONTO")
    comprobante_url: str | None = Field(None, validation_alias="COMPROBANTE_URL")
    fecha_creacion: datetime | None = Field(None, validation_alias="FECHA_CREACION")
    fecha_marcado_pago: datetime | None = Field(None, validation_alias="FECHA_MARCADO_PAGO")


class PaymentStats(BaseModel):
    total_cobrado: Decimal
    total_pendiente: Decimal
    total_no_pago: Decimal
    count_por_estado: dict[str, int]
