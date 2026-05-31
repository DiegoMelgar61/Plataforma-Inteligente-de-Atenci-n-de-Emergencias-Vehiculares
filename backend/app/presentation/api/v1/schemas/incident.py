"""
Esquemas del núcleo de incidentes y evidencias asociadas.
"""
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.presentation.api.v1.schemas.evidence import EvidenceUploadResponse


class IncidentCreate(BaseModel):
    """
    Modelo de referencia para documentar el cuerpo lógico del reporte.
    La ruta POST /incidents/report usa multipart (Form + File); estos campos equivalen a los formularios.
    """

    latitud: float = Field(..., ge=-90, le=90, description="Latitud WGS84", examples=[-16.5])
    longitud: float = Field(..., ge=-180, le=180, description="Longitud WGS84", examples=[-68.15])
    id_vehiculo: UUID | None = Field(default=None, description="Vehículo del cliente (opcional)")
    prioridad: Literal["BAJA", "MEDIA", "ALTA"] = "MEDIA"
    clasificacion: Literal["BATERIA", "LLANTA", "CHOQUE", "MOTOR", "OTROS", "INCIERTO"] = "OTROS"
    texto_descripcion: str | None = Field(
        default=None,
        max_length=8000,
        description="Texto libre si no se adjuntan archivos",
    )
    id_local: str | None = None


class IncidentSyncItem(BaseModel):
    """Item individual para POST /incidents/sync (sync offline)."""

    id_local: str = Field(..., max_length=36, description="ID local del incidente (requerido para sync)")
    latitud: float = Field(..., ge=-90, le=90)
    longitud: float = Field(..., ge=-180, le=180)
    id_vehiculo: UUID | None = None
    prioridad: Literal["BAJA", "MEDIA", "ALTA"] = "MEDIA"
    clasificacion: Literal["BATERIA", "LLANTA", "CHOQUE", "MOTOR", "OTROS", "INCIERTO"] = "OTROS"
    texto_descripcion: str | None = Field(None, max_length=8000)


class IncidentSyncResponse(BaseModel):
    """Respuesta de POST /incidents/sync."""

    sincronizados: int
    omitidos: int
    errores: list[str]


class EvidenceItemResponse(BaseModel):
    """Evidencia ligada a un incidente (respuesta de detalle)."""

    model_config = ConfigDict(from_attributes=True)

    id_evidencia: UUID = Field(validation_alias="ID_EVIDENCIA")
    id_incidente: UUID = Field(validation_alias="ID_INCIDENTE")
    tipo: str = Field(validation_alias="TIPO")
    url_archivo: str = Field(validation_alias="URL_ARCHIVO")
    clave_archivo: str | None = Field(validation_alias="CLAVE_ARCHIVO")
    texto_transcrito: str | None = Field(validation_alias="TEXTO_TRANSCRITO")
    analisis_ia: str | None = Field(default=None, validation_alias="ANALISIS_IA")
    fecha_creacion: datetime | None = Field(validation_alias="FECHA_CREACION")


class IncidentListResponse(BaseModel):
    """Resumen para GET /incidents/my (sin lista de evidencias)."""

    model_config = ConfigDict(from_attributes=True)

    id_incidente: UUID = Field(validation_alias="ID_INCIDENTE")
    id_usuario_cliente: UUID = Field(validation_alias="ID_USUARIO_CLIENTE")
    id_vehiculo: UUID | None = Field(validation_alias="ID_VEHICULO")
    latitud: float | None = Field(default=None, description="Derivada de UBICACION en el router")
    longitud: float | None = Field(default=None, description="Derivada de UBICACION en el router")
    estado: str = Field(validation_alias="ESTADO")
    prioridad: str = Field(validation_alias="PRIORIDAD")
    clasificacion: str = Field(validation_alias="CLASIFICACION")
    fecha_creacion: datetime | None = Field(validation_alias="FECHA_CREACION")
    id_tenant: UUID | None = Field(None, validation_alias="ID_TENANT")


class IncidentResponse(BaseModel):
    """Detalle completo con evidencias (GET /incidents/{id})."""

    model_config = ConfigDict(from_attributes=True)

    id_incidente: UUID = Field(validation_alias="ID_INCIDENTE")
    id_usuario_cliente: UUID = Field(validation_alias="ID_USUARIO_CLIENTE")
    id_vehiculo: UUID | None = Field(validation_alias="ID_VEHICULO")
    latitud: float | None = None
    longitud: float | None = None
    estado: str = Field(validation_alias="ESTADO")
    prioridad: str = Field(validation_alias="PRIORIDAD")
    clasificacion: str = Field(validation_alias="CLASIFICACION")
    resumen_ia: str | None = Field(validation_alias="RESUMEN_IA")
    tiempo_estimado_llegada_minutos: int | None = Field(
        validation_alias="TIEMPO_ESTIMADO_LLEGADA_MINUTOS"
    )
    fecha_creacion: datetime | None = Field(validation_alias="FECHA_CREACION")
    fecha_actualizacion: datetime | None = Field(validation_alias="FECHA_ACTUALIZACION")
    id_tenant: UUID | None = Field(None, validation_alias="ID_TENANT")
    id_local: str | None = Field(None, validation_alias="ID_LOCAL")
    evidencias: list[EvidenceItemResponse] = Field(default_factory=list)


class ReporteIncidenteResponse(BaseModel):
    """Respuesta de POST /incidents/report."""

    incidente_id: UUID = Field(description="ID del incidente creado")
    mensaje: str = Field(default="Incidente registrado correctamente")
    evidencias_subidas: list[EvidenceUploadResponse] = Field(
        description="Evidencias registradas con URL temporal",
    )
