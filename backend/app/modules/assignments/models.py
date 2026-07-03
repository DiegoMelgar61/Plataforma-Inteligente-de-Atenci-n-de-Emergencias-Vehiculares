from sqlalchemy import DECIMAL, Boolean, Column, DateTime, ForeignKey, Integer, Text, func

from app.core.database import Base


class ASIGNACIONES(Base):
    __tablename__ = "asignaciones"

    ID_ASIGNACION = Column("id_asignacion", Integer, primary_key=True)
    ID_INCIDENTE = Column("id_incidente", Integer, ForeignKey("incidentes.id_incidente"), unique=True)
    ID_TALLER = Column("id_taller", Integer, ForeignKey("talleres.id_taller"))
    ID_TECNICO = Column("id_tecnico", Integer, ForeignKey("tecnicos.id_tecnico"))
    FECHA_ASIGNACION = Column("fecha_asignacion", DateTime(timezone=True), server_default=func.now())
    FECHA_ACEPTACION = Column("fecha_aceptacion", DateTime(timezone=True))
    FECHA_RECHAZO = Column("fecha_rechazo", DateTime(timezone=True))
    MOTIVO_RECHAZO = Column("motivo_rechazo", Text)
    MONTO_COTIZADO = Column("monto_cotizado", DECIMAL(10, 2), nullable=True)
    TIEMPO_ESTIMADO_REPARACION = Column("tiempo_estimado_reparacion", Integer, nullable=True)
    COTIZACION_ACEPTADA = Column("cotizacion_aceptada", Boolean, nullable=True)
    NOTAS_COTIZACION = Column("notas_cotizacion", Text, nullable=True)
