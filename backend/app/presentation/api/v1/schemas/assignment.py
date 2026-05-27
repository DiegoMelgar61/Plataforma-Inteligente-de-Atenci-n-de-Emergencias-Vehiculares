"""
Esquemas para las operaciones de asignación inteligente.
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WorkshopCandidateResponse(BaseModel):
    """Taller candidato para asignación (con distancia)."""

    id_taller: UUID = Field(description="ID del taller")
    id_tecnico: UUID = Field(description="ID del técnico disponible")
    nombre_negocio: str = Field(description="Nombre del taller")
    distancia_km: float = Field(description="Distancia aproximada en km")
    telefono_tecnico: str | None = Field(description="Teléfono del técnico")


class AvailableWorkshopsResponse(BaseModel):
    """Listado de talleres cercanos disponibles."""

    ubicado: bool = Field(description="Si el incidente tiene ubicación válida")
    total_candidatos: int = Field(description="Número de talleres candidatos")
    candidatos: list[WorkshopCandidateResponse] = Field(
        description="Lista de talleres ordenados por proximidad"
    )


class AssignmentResponse(BaseModel):
    """Respuesta de asignación exitosa."""

    model_config = ConfigDict(from_attributes=True)

    id_asignacion: UUID = Field(validation_alias="ID_ASIGNACION")
    id_incidente: UUID = Field(validation_alias="ID_INCIDENTE")
    id_taller: UUID = Field(validation_alias="ID_TALLER")
    id_tecnico: UUID = Field(validation_alias="ID_TECNICO")
    fecha_asignacion: datetime | None = Field(validation_alias="FECHA_ASIGNACION")
    mensaje: str = Field(default="Incidente asignado correctamente")
