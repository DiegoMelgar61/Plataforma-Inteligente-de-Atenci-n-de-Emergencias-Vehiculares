from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class TechnicianCreate(BaseModel):
    """Alta de técnico bajo el taller del usuario autenticado (sin cuenta de login)."""

    nombre_completo: str = Field(..., max_length=255)
    telefono: str | None = Field(None, max_length=20)
    disponible: bool = True


class TechnicianWithUserCreate(BaseModel):
    """
    Alta de técnico con cuenta de login propia.
    Crea atómicamente un USUARIO con rol=TECNICO y el registro en TECNICOS.
    """

    nombre_completo: str = Field(..., max_length=255)
    telefono: str | None = Field(None, max_length=20)
    correo_electronico: EmailStr
    contrasena: str = Field(..., min_length=8, description="Mínimo 8 caracteres")
    id_taller: int | None = None


class TechnicianUpdate(BaseModel):
    """Actualización de técnico."""

    nombre_completo: str | None = Field(None, max_length=255)
    telefono: str | None = Field(None, max_length=20)
    disponible: bool | None = None


class TechnicianResponse(BaseModel):
    """Técnico del taller."""

    model_config = ConfigDict(from_attributes=True)

    id_tecnico: int = Field(validation_alias="ID_TECNICO")
    id_taller: int = Field(validation_alias="ID_TALLER")
    id_usuario: int | None = Field(None, validation_alias="ID_USUARIO")
    nombre_completo: str = Field(validation_alias="NOMBRE_COMPLETO")
    telefono: str | None = Field(validation_alias="TELEFONO")
    disponible: bool = Field(validation_alias="DISPONIBLE")
    fecha_creacion: datetime | None = Field(validation_alias="FECHA_CREACION")
    fecha_actualizacion: datetime | None = Field(validation_alias="FECHA_ACTUALIZACION")


class TechnicianActiveAssignmentResponse(BaseModel):
    """Asignación activa del técnico autenticado con contexto completo del incidente."""

    id_asignacion: int
    id_incidente: int
    id_taller: int
    id_tecnico: int
    estado_incidente: str
    clasificacion: str
    prioridad: str
    resumen_ia: str | None = None
    latitud: float | None = None
    longitud: float | None = None
    tiempo_estimado_llegada_minutos: int | None = None
    cliente_nombre: str | None = None
    cliente_telefono: str | None = None
    fecha_asignacion: datetime | None = None
    fecha_creacion_incidente: datetime | None = None


class UpdateIncidentStateRequest(BaseModel):
    """
    Solicitud de transición de estado por parte del técnico asignado.
    Solo se aceptan las transiciones definidas en la máquina de estados:
    ASIGNADO → EN_CAMINO → EN_PROCESO → ATENDIDO
    """

    nuevo_estado: Literal["EN_CAMINO", "EN_PROCESO", "ATENDIDO"]
