"""
Respuesta al registrar una evidencia en el reporte multimodal.
"""
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class EvidenceUploadResponse(BaseModel):
    """Metadatos de una evidencia recién creada (URL provisional hasta CDN/S3)."""

    id_evidencia: UUID = Field(description="Identificador persistido en EVIDENCIAS")
    tipo: Literal["IMAGEN", "AUDIO", "TEXTO"] = Field(description="Tipo de evidencia")
    url_archivo: str = Field(
        description="URL temporal de referencia; sustituir por URL definitiva en producción",
    )
    nombre_original: str | None = Field(
        default=None,
        description="Nombre del archivo enviado por el cliente, si aplica",
    )
