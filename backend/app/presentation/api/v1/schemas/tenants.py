from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TenantCreate(BaseModel):
    nombre: str
    descripcion: str | None = None


class TenantUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    activo: bool | None = None


class TenantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_tenant: UUID = Field(validation_alias="ID_TENANT")
    nombre: str = Field(validation_alias="NOMBRE")
    descripcion: str | None = Field(None, validation_alias="DESCRIPCION")
    activo: bool = Field(validation_alias="ACTIVO")
    fecha_creacion: datetime | None = Field(None, validation_alias="FECHA_CREACION")
