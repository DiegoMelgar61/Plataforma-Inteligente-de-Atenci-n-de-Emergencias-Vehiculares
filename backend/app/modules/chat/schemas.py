from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MensajeChatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_mensaje: int
    rol_emisor: str
    contenido: str | None = None
    url_adjunto: str | None = None
    tipo_adjunto: str | None = None
    fecha_creacion: datetime


class ConversacionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_conversacion: int
    tipo: str
    mensajes: list[MensajeChatResponse] = []


class EnviarMensajeResponse(BaseModel):
    mensaje_usuario: MensajeChatResponse
    mensaje_ia: MensajeChatResponse
