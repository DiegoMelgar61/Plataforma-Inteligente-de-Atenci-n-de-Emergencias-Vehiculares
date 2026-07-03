import uuid

from geoalchemy2 import Geography
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class TECNICOS(Base):
    __tablename__ = "tecnicos"

    ID_TECNICO = Column("id_tecnico", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ID_TALLER = Column("id_taller", UUID(as_uuid=True), ForeignKey("talleres.id_taller", ondelete="CASCADE"), nullable=False)
    # Cuenta de login del técnico (usuario con rol TECNICO). Nullable para
    # compatibilidad con técnicos creados antes de esta columna.
    ID_USUARIO = Column("id_usuario", UUID(as_uuid=True), ForeignKey("usuarios.id_usuario", ondelete="SET NULL"), unique=True, nullable=True)
    NOMBRE_COMPLETO = Column("nombre_completo", String(255), nullable=False)
    TELEFONO = Column("telefono", String(20))
    DISPONIBLE = Column("disponible", Boolean, default=True)
    UBICACION_ACTUAL = Column("ubicacion_actual", Geography(geometry_type='POINT', srid=4326))
    FECHA_CREACION = Column("fecha_creacion", DateTime(timezone=True), server_default=func.now())
    FECHA_ACTUALIZACION = Column("fecha_actualizacion", DateTime(timezone=True), onupdate=func.now())
