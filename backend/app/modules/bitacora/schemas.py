"""Esquemas de la bitácora de auditoría."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class BitacoraResponse(BaseModel):
    """Entrada de bitácora con el nombre del usuario actor (si existe)."""

    id_bitacora: UUID
    id_usuario: UUID | None = None
    usuario_nombre: str | None = None
    id_tenant: UUID | None = None
    accion: str
    entidad: str | None = None
    id_entidad: str | None = None
    descripcion: str | None = None
    ip: str | None = None
    fecha_creacion: datetime | None = None
