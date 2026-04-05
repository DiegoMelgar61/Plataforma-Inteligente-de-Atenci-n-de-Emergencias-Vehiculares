from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TechnicianCreate(BaseModel):
    """Alta de técnico bajo el taller del usuario autenticado."""

    nombre_completo: str = Field(..., max_length=255)
    telefono: str | None = Field(None, max_length=20)
    disponible: bool = True


class TechnicianUpdate(BaseModel):
    """Actualización de técnico."""

    nombre_completo: str | None = Field(None, max_length=255)
    telefono: str | None = Field(None, max_length=20)
    disponible: bool | None = None


class TechnicianResponse(BaseModel):
    """Técnico del taller."""

    model_config = ConfigDict(from_attributes=True)

    id_tecnico: UUID = Field(validation_alias="ID_TECNICO")
    id_taller: UUID = Field(validation_alias="ID_TALLER")
    nombre_completo: str = Field(validation_alias="NOMBRE_COMPLETO")
    telefono: str | None = Field(validation_alias="TELEFONO")
    disponible: bool = Field(validation_alias="DISPONIBLE")
    fecha_creacion: datetime | None = Field(validation_alias="FECHA_CREACION")
    fecha_actualizacion: datetime | None = Field(validation_alias="FECHA_ACTUALIZACION")
