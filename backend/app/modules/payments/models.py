import uuid

from sqlalchemy import DECIMAL, Column, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base

EstadoPagoEnum = Enum('NO_PAGO', 'PENDIENTE', 'PAGADO', 'RECHAZADO', name='estado_pago_enum')


class PAGOS(Base):
    __tablename__ = "pagos"

    ID_PAGO = Column("id_pago", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ID_INCIDENTE = Column("id_incidente", UUID(as_uuid=True), ForeignKey("incidentes.id_incidente"), unique=True)
    ID_USUARIO_CLIENTE = Column("id_usuario_cliente", UUID(as_uuid=True), ForeignKey("usuarios.id_usuario"))
    ID_TALLER = Column("id_taller", UUID(as_uuid=True), ForeignKey("talleres.id_taller"))
    ID_ASIGNACION = Column("id_asignacion", UUID(as_uuid=True), ForeignKey("asignaciones.id_asignacion"))
    MONTO = Column("monto", DECIMAL(10, 2), nullable=False)
    COMISION_PLATAFORMA = Column("comision_plataforma", DECIMAL(10, 2), nullable=False)
    ESTADO = Column("estado", EstadoPagoEnum, default="NO_PAGO")
    METODO_PAGO = Column("metodo_pago", String(50))
    ID_TRANSACCION = Column("id_transaccion", String(255))
    COMPROBANTE_URL = Column("comprobante_url", Text)
    COMPROBANTE_CLAVE = Column("comprobante_clave", Text)
    NOTAS_CLIENTE = Column("notas_cliente", Text)
    FECHA_CREACION = Column("fecha_creacion", DateTime(timezone=True), server_default=func.now())
    FECHA_MARCADO_PAGO = Column("fecha_marcado_pago", DateTime(timezone=True))
    FECHA_CONFIRMACION = Column("fecha_confirmacion", DateTime(timezone=True))
    FECHA_RECHAZO = Column("fecha_rechazo", DateTime(timezone=True))
    MOTIVO_RECHAZO = Column("motivo_rechazo", Text)
    ID_USUARIO_CONFIRMO = Column("id_usuario_confirmo", UUID(as_uuid=True), ForeignKey("usuarios.id_usuario"))
    FECHA_ACTUALIZACION = Column("fecha_actualizacion", DateTime(timezone=True), onupdate=func.now())
    ID_TENANT = Column("id_tenant", UUID(as_uuid=True), ForeignKey("tenants.id_tenant"), nullable=True)
    tenant = relationship("Tenant", foreign_keys=[ID_TENANT])
