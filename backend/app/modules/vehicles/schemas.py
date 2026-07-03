from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class VehicleCreate(BaseModel):
    """Alta de vehículo para el cliente autenticado."""

    marca: str | None = Field(None, max_length=100)
    modelo: str | None = Field(None, max_length=100)
    anio: int | None = Field(None, ge=1900, le=2100)
    placa: str | None = Field(None, max_length=20)


class VehicleUpdate(BaseModel):
    """Actualización parcial de vehículo."""

    marca: str | None = Field(None, max_length=100)
    modelo: str | None = Field(None, max_length=100)
    anio: int | None = Field(None, ge=1900, le=2100)
    placa: str | None = Field(None, max_length=20)


class VehicleResponse(BaseModel):
    """Vehículo persistido."""

    model_config = ConfigDict(from_attributes=True)

    id_vehiculo: int = Field(validation_alias="ID_VEHICULO")
    id_usuario_cliente: int = Field(validation_alias="ID_USUARIO_CLIENTE")
    marca: str | None = Field(validation_alias="MARCA")
    modelo: str | None = Field(validation_alias="MODELO")
    anio: int | None = Field(validation_alias="ANIO")
    placa: str | None = Field(validation_alias="PLACA")
    fecha_creacion: datetime | None = Field(validation_alias="FECHA_CREACION")
    fecha_actualizacion: datetime | None = Field(validation_alias="FECHA_ACTUALIZACION")
