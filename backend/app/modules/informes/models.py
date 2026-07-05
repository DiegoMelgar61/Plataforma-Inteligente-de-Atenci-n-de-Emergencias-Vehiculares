from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
    func,
)

from app.core.database import Base

# ==================== ENUMS ====================
EstadoInformeEnum = Enum(
    "GENERANDO", "LISTO", "FALLIDO", name="estado_informe_enum"
)

# ==================== MODELOS ====================


class INFORMES_SERVICIO(Base):
    """
    Informe de servicio en PDF generado automáticamente por IA al finalizar un
    incidente (transición a ATENDIDO). Un informe por incidente/orden.

    Esta tabla es la fuente de verdad del estado del informe: se genera UNA
    sola vez por incidente (nunca se regenera al reingresar) y cualquier fallo
    de la IA, del PDF o del correo queda registrado acá, no en silencio.

    El PDF vive en disco bajo UPLOADS_DIR/informes/{id_incidente}/ y se sirve
    vía StaticFiles; CONTENIDO_IA guarda el JSON de secciones que devolvió la
    IA, de modo que el PDF pueda reconstruirse sin volver a llamar a la IA.
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
    ESTADO = Column(
        "estado", EstadoInformeEnum, nullable=False, default="GENERANDO"
    )
    # JSON de secciones devuelto por la IA (una clave por sección del PDF).
    CONTENIDO_IA = Column("contenido_ia", JSON, nullable=True)
    # Referencia al PDF persistido; null mientras GENERANDO o si quedó FALLIDO.
    URL_ARCHIVO = Column("url_archivo", Text, nullable=True)
    CLAVE_ARCHIVO = Column("clave_archivo", Text, nullable=True)
    # False cuando la IA falló y el PDF se generó con textos de respaldo.
    GENERADO_POR_IA = Column(
        "generado_por_ia", Boolean, nullable=False, default=True
    )
    CORREO_ENVIADO = Column(
        "correo_enviado", Boolean, nullable=False, default=False
    )
    # Detalle del fallo (IA, PDF o correo). El fallo nunca es silencioso.
    ERROR_DETALLE = Column("error_detalle", Text, nullable=True)
    # Momento en que la generación terminó (LISTO o FALLIDO).
    FECHA_GENERACION = Column(
        "fecha_generacion", DateTime(timezone=True), nullable=True
    )
    FECHA_CREACION = Column(
        "fecha_creacion", DateTime(timezone=True), server_default=func.now()
    )
