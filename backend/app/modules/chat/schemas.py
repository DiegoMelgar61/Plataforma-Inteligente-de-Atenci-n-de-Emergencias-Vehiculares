from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MensajeChatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_mensaje: int = Field(validation_alias="ID_MENSAJE")
    rol_emisor: str = Field(validation_alias="ROL_EMISOR")
    contenido: str | None = Field(default=None, validation_alias="CONTENIDO")
    url_adjunto: str | None = Field(default=None, validation_alias="URL_ADJUNTO")
    tipo_adjunto: str | None = Field(default=None, validation_alias="TIPO_ADJUNTO")
    fecha_creacion: datetime = Field(validation_alias="FECHA_CREACION")


class ConversacionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_conversacion: int
    tipo: str
    mensajes: list[MensajeChatResponse] = []


class EnviarMensajeResponse(BaseModel):
    mensaje_usuario: MensajeChatResponse
    mensaje_ia: MensajeChatResponse
