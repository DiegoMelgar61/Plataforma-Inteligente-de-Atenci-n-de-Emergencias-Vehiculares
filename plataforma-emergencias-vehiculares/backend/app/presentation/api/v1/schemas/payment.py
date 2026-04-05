"""
Esquemas para pagos e ingresos generados por la plataforma.
"""
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PaymentCreate(BaseModel):
    """Creación de pago para un incidente."""

    monto: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2, description="Monto total a pagar")
    metodo_pago: str | None = Field(None, max_length=50, description="Método de pago (ej. TARJETA, TRANSFERENCIA)")


class PaymentResponse(BaseModel):
    """Respuesta de información de pago."""

    model_config = ConfigDict(from_attributes=True)

    id_pago: UUID = Field(validation_alias="ID_PAGO")
    id_incidente: UUID = Field(validation_alias="ID_INCIDENTE")
    id_usuario_cliente: UUID = Field(validation_alias="ID_USUARIO_CLIENTE")
    monto: Decimal = Field(validation_alias="MONTO")
    comision_plataforma: Decimal = Field(validation_alias="COMISION_PLATAFORMA")
    estado: str = Field(validation_alias="ESTADO")
    metodo_pago: str | None = Field(validation_alias="METODO_PAGO")
    id_transaccion: str | None = Field(validation_alias="ID_TRANSACCION")
    fecha_creacion: datetime | None = Field(validation_alias="FECHA_CREACION")
