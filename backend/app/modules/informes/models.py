from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
    func,
)

from app.core.database import Base

# ==================== MODELOS ====================


class INFORMES_SERVICIO(Base):
    """
    Informe de servicio en PDF generado automáticamente por IA al finalizar un
    incidente (transición a ATENDIDO). Un informe por incidente/orden.

    El PDF vive en disco bajo UPLOADS_DIR/informes/{id_incidente}/ y se sirve
    vía StaticFiles; esta tabla guarda solo los metadatos y la ruta.
    """

    __tablename__ = "informes_servicio"
    __table_args__ = (
        UniqueConstraint("id_incidente", name="uq_informes_servicio_incidente"),
    )

    ID_INFORME = Column("id_informe", Integer, primary_key=True)
    ID_INCIDENTE = Column(
        "id_incidente",
        Integer,
        ForeignKey("incidentes.id_incidente", ondelete="CASCADE"),
        nullable=False,
    )
    ID_TENANT = Column(
        "id_tenant", Integer, ForeignKey("tenants.id_tenant"), nullable=True
    )
    URL_ARCHIVO = Column("url_archivo", Text, nullable=False)
    CLAVE_ARCHIVO = Column("clave_archivo", Text, nullable=False)
    # False cuando la IA falló y el PDF se generó con textos de respaldo.
    GENERADO_POR_IA = Column(
        "generado_por_ia", Boolean, nullable=False, default=True
    )
    FECHA_CREACION = Column(
        "fecha_creacion", DateTime(timezone=True), server_default=func.now()
    )
