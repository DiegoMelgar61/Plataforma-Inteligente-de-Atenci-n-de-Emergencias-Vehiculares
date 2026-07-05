from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class InformeServicioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_informe: int = Field(validation_alias="ID_INFORME")
    id_incidente: int = Field(validation_alias="ID_INCIDENTE")
    url_archivo: str = Field(validation_alias="URL_ARCHIVO")
    generado_por_ia: bool = Field(validation_alias="GENERADO_POR_IA")
    fecha_creacion: datetime = Field(validation_alias="FECHA_CREACION")
