from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func

from app.core.database import Base


class VEHICULOS(Base):
    __tablename__ = "vehiculos"

    ID_VEHICULO = Column("id_vehiculo", Integer, primary_key=True)
    ID_USUARIO_CLIENTE = Column("id_usuario_cliente", Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False)
    MARCA = Column("marca", String(100))
    MODELO = Column("modelo", String(100))
    ANIO = Column("anio", Integer)
    PLACA = Column("placa", String(20), unique=True)
    FECHA_CREACION = Column("fecha_creacion", DateTime(timezone=True), server_default=func.now())
    FECHA_ACTUALIZACION = Column("fecha_actualizacion", DateTime(timezone=True), onupdate=func.now())
