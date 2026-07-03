from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, func

from app.core.database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    ID_TENANT = Column("id_tenant", Integer, primary_key=True)
    NOMBRE = Column("nombre", String(255), unique=True, nullable=False)
    DESCRIPCION = Column("descripcion", Text, nullable=True)
    ACTIVO = Column("activo", Boolean, default=True)
    FECHA_CREACION = Column("fecha_creacion", DateTime(timezone=True), server_default=func.now())
    FECHA_ACTUALIZACION = Column("fecha_actualizacion", DateTime(timezone=True), onupdate=func.now())
