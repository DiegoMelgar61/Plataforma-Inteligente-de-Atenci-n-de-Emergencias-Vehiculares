"""
Esquemas para las operaciones de asignación inteligente y cotizaciones.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WorkshopCandidateResponse(BaseModel):
    """Taller candidato para asignación (con distancia)."""

    id_taller: int = Field(description="ID del taller")
    id_tecnico: int = Field(description="ID del técnico disponible")
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

    id_asignacion: int = Field(validation_alias="ID_ASIGNACION")
    id_incidente: int = Field(validation_alias="ID_INCIDENTE")
    id_taller: int = Field(validation_alias="ID_TALLER")
    id_tecnico: int = Field(validation_alias="ID_TECNICO")
    fecha_asignacion: datetime | None = Field(validation_alias="FECHA_ASIGNACION")
    mensaje: str = Field(default="Incidente asignado correctamente")


class CotizacionCreate(BaseModel):
    """Propuesta de cotización enviada por el taller."""

    monto_cotizado: float = Field(..., gt=0, description="Monto total cotizado (moneda local)")
    tiempo_estimado_reparacion: int | None = Field(
        None, gt=0, description="Tiempo estimado en minutos"
    )
    notas_cotizacion: str | None = Field(None, max_length=1000)


class CotizacionRespuesta(BaseModel):
    """Respuesta del cliente a la cotización propuesta."""

    aceptada: bool
    motivo_rechazo: str | None = Field(None, max_length=500)


class CotizacionDetalleResponse(BaseModel):
    """Estado actual de la cotización para un incidente."""

    id_asignacion: int
    id_incidente: int
    monto_cotizado: float | None
    tiempo_estimado_reparacion: int | None
    notas_cotizacion: str | None
    cotizacion_aceptada: bool | None
    estado_incidente: str
    timestamp: str | None = None
