from geoalchemy2 import Geography
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func

from app.core.database import Base


class TECNICOS(Base):
    __tablename__ = "tecnicos"

    ID_TECNICO = Column("id_tecnico", Integer, primary_key=True)
    ID_TALLER = Column("id_taller", Integer, ForeignKey("talleres.id_taller", ondelete="CASCADE"), nullable=False)
    ID_USUARIO = Column("id_usuario", Integer, ForeignKey("usuarios.id_usuario", ondelete="SET NULL"), unique=True, nullable=True)
    NOMBRE_COMPLETO = Column("nombre_completo", String(255), nullable=False)
    TELEFONO = Column("telefono", String(20))
    DISPONIBLE = Column("disponible", Boolean, default=True)
    UBICACION_ACTUAL = Column("ubicacion_actual", Geography(geometry_type='POINT', srid=4326))
    FECHA_CREACION = Column("fecha_creacion", DateTime(timezone=True), server_default=func.now())
    FECHA_ACTUALIZACION = Column("fecha_actualizacion", DateTime(timezone=True), onupdate=func.now())
