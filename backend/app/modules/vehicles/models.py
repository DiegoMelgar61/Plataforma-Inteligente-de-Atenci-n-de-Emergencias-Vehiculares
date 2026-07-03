import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class VEHICULOS(Base):
    __tablename__ = "vehiculos"

    ID_VEHICULO = Column("id_vehiculo", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ID_USUARIO_CLIENTE = Column("id_usuario_cliente", UUID(as_uuid=True), ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False)
    MARCA = Column("marca", String(100))
    MODELO = Column("modelo", String(100))
    ANIO = Column("anio", Integer)
    PLACA = Column("placa", String(20), unique=True)
    FECHA_CREACION = Column("fecha_creacion", DateTime(timezone=True), server_default=func.now())
    FECHA_ACTUALIZACION = Column("fecha_actualizacion", DateTime(timezone=True), onupdate=func.now())
