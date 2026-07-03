from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class USUARIOS(Base):
    __tablename__ = "usuarios"

    ID_USUARIO = Column("id_usuario", Integer, primary_key=True)
    CORREO_ELECTRONICO = Column("correo_electronico", String(255), unique=True, nullable=False)
    HASH_CONTRASENA = Column("hash_contrasena", Text, nullable=False)
    NOMBRE_COMPLETO = Column("nombre_completo", String(255), nullable=False)
    TELEFONO = Column("telefono", String(20))
    ROL = Column("rol", Enum('CLIENTE', 'TALLER', 'ADMIN', 'TECNICO', name='rol_enum'), nullable=False)
    ACTIVO = Column("activo", Boolean, default=True)
    FECHA_CREACION = Column("fecha_creacion", DateTime(timezone=True), server_default=func.now())
    FECHA_ACTUALIZACION = Column("fecha_actualizacion", DateTime(timezone=True), onupdate=func.now())
    FECHA_ELIMINACION = Column("fecha_eliminacion", DateTime(timezone=True), nullable=True)
    ID_TENANT = Column("id_tenant", Integer, ForeignKey("tenants.id_tenant"), nullable=True)
    tenant = relationship("Tenant", foreign_keys=[ID_TENANT])


class CLIENTES(Base):
    __tablename__ = "clientes"

    ID_USUARIO = Column("id_usuario", Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), primary_key=True)
