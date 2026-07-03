"""Esquemas de la bitácora de auditoría."""
from datetime import datetime

from pydantic import BaseModel


class BitacoraResponse(BaseModel):
    id_bitacora: int
    id_usuario: int | None = None
    usuario_nombre: str | None = None
    id_tenant: int | None = None
    accion: str
    entidad: str | None = None
    id_entidad: str | None = None
    descripcion: str | None = None
    ip: str | None = None
    fecha_creacion: datetime | None = None
