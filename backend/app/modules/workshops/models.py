from sqlalchemy import DECIMAL, Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class TALLERES(Base):
    __tablename__ = "talleres"

    ID_TALLER = Column("id_taller", Integer, primary_key=True)
    ID_USUARIO = Column("id_usuario", Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), unique=True)
    NOMBRE_NEGOCIO = Column("nombre_negocio", String(255), nullable=False)
    NIT = Column("nit", String(50), unique=True)
    DIRECCION = Column("direccion", Text)
    TASA_COMISION = Column("tasa_comision", DECIMAL(5, 2), default=10.00)
    LATITUD = Column("latitud", DECIMAL(10, 7), nullable=True)
    LONGITUD = Column("longitud", DECIMAL(10, 7), nullable=True)
    ACTIVO = Column("activo", Boolean, default=True)
    FECHA_CREACION = Column("fecha_creacion", DateTime(timezone=True), server_default=func.now())
    FECHA_ACTUALIZACION = Column("fecha_actualizacion", DateTime(timezone=True), onupdate=func.now())
    ID_TENANT = Column("id_tenant", Integer, ForeignKey("tenants.id_tenant"), nullable=True)
    tenant = relationship("Tenant", foreign_keys=[ID_TENANT])
