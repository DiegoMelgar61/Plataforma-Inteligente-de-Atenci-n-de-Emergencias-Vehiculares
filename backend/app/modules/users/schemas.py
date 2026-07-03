from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserProfile(BaseModel):
    """Perfil público del usuario autenticado (sin contraseña)."""

    model_config = ConfigDict(from_attributes=True)

    id_usuario: int = Field(validation_alias="ID_USUARIO")
    correo_electronico: EmailStr = Field(validation_alias="CORREO_ELECTRONICO")
    nombre_completo: str = Field(validation_alias="NOMBRE_COMPLETO")
    telefono: str | None = Field(validation_alias="TELEFONO")
    rol: str = Field(validation_alias="ROL")
    activo: bool = Field(validation_alias="ACTIVO")
    fecha_creacion: datetime | None = Field(validation_alias="FECHA_CREACION")
    fecha_actualizacion: datetime | None = Field(validation_alias="FECHA_ACTUALIZACION")
    id_tenant: int | None = Field(None, validation_alias="ID_TENANT")


class UserUpdate(BaseModel):
    """Campos editables del perfil propio."""

    nombre_completo: str | None = None
    telefono: str | None = None
