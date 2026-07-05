from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class InformeServicioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_informe: int = Field(validation_alias="ID_INFORME")
    id_incidente: int = Field(validation_alias="ID_INCIDENTE")
    estado: str = Field(validation_alias="ESTADO")
    # Referencia al PDF; null mientras GENERANDO o si quedó FALLIDO.
    url_archivo: str | None = Field(default=None, validation_alias="URL_ARCHIVO")
    generado_por_ia: bool = Field(validation_alias="GENERADO_POR_IA")
    correo_enviado: bool = Field(validation_alias="CORREO_ENVIADO")
    error_detalle: str | None = Field(default=None, validation_alias="ERROR_DETALLE")
    fecha_generacion: datetime | None = Field(
        default=None, validation_alias="FECHA_GENERACION"
    )
    fecha_creacion: datetime = Field(validation_alias="FECHA_CREACION")

    @field_validator("estado", mode="before")
    @classmethod
    def _estado_a_texto(cls, v):
        return v.value if hasattr(v, "value") else v
