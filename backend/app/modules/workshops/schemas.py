from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class WorkshopCreate(BaseModel):
    """Registro del taller asociado al usuario con rol TALLER."""

    nombre_negocio: str = Field(..., max_length=255)
    nit: str | None = Field(None, max_length=50)
    direccion: str | None = None
    tasa_comision: Decimal | None = Field(default=Decimal("10.00"), ge=0, max_digits=5, decimal_places=2)
    latitud: float | None = Field(None, ge=-90, le=90)
    longitud: float | None = Field(None, ge=-180, le=180)


class WorkshopUpdate(BaseModel):
    """Actualización del taller (dueño o admin)."""

    nombre_negocio: str | None = Field(None, max_length=255)
    nit: str | None = Field(None, max_length=50)
    direccion: str | None = None
    tasa_comision: Decimal | None = Field(None, ge=0, max_digits=5, decimal_places=2)
    latitud: float | None = Field(None, ge=-90, le=90)
    longitud: float | None = Field(None, ge=-180, le=180)
    activo: bool | None = None


class WorkshopResponse(BaseModel):
    """Datos del taller."""

    model_config = ConfigDict(from_attributes=True)

    id_taller: int = Field(validation_alias="ID_TALLER")
    id_usuario: int | None = Field(None, validation_alias="ID_USUARIO")
    nombre_negocio: str = Field(validation_alias="NOMBRE_NEGOCIO")
    nit: str | None = Field(validation_alias="NIT")
    direccion: str | None = Field(validation_alias="DIRECCION")
    tasa_comision: Decimal | None = Field(validation_alias="TASA_COMISION")
    latitud: float | None = Field(validation_alias="LATITUD")
    longitud: float | None = Field(validation_alias="LONGITUD")
    activo: bool = Field(validation_alias="ACTIVO")
    fecha_creacion: datetime | None = Field(validation_alias="FECHA_CREACION")
    fecha_actualizacion: datetime | None = Field(validation_alias="FECHA_ACTUALIZACION")
    id_tenant: int | None = Field(None, validation_alias="ID_TENANT")
