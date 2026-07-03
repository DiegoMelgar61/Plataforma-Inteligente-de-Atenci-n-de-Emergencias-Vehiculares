import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class BITACORA(Base):
    """Bitácora de auditoría: registra acciones relevantes de los usuarios."""
    __tablename__ = "bitacora"

    ID_BITACORA = Column("id_bitacora", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ID_USUARIO = Column("id_usuario", UUID(as_uuid=True), ForeignKey("usuarios.id_usuario", ondelete="SET NULL"), nullable=True)
    ID_TENANT = Column("id_tenant", UUID(as_uuid=True), ForeignKey("tenants.id_tenant"), nullable=True)
    ACCION = Column("accion", String(100), nullable=False)
    ENTIDAD = Column("entidad", String(50), nullable=True)
    ID_ENTIDAD = Column("id_entidad", String(64), nullable=True)
    DESCRIPCION = Column("descripcion", Text, nullable=True)
    IP = Column("ip", String(64), nullable=True)
    FECHA_CREACION = Column("fecha_creacion", DateTime(timezone=True), server_default=func.now())
