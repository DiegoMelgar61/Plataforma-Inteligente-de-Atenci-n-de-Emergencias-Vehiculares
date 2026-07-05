from sqlalchemy import (
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
TipoConversacionEnum = Enum("CLIENTE", "TECNICO", name="tipo_conversacion_enum")
RolEmisorEnum = Enum("CLIENTE", "TECNICO", "IA", name="rol_emisor_enum")
TipoAdjuntoEnum = Enum("IMAGEN", "ARCHIVO", name="tipo_adjunto_enum")

# ==================== MODELOS ====================


class CONVERSACIONES(Base):
    __tablename__ = "conversaciones"
    __table_args__ = (
        UniqueConstraint("id_incidente", "tipo", name="uq_conversaciones_incidente_tipo"),
    )

    ID_CONVERSACION = Column("id_conversacion", Integer, primary_key=True)
    ID_INCIDENTE = Column(
        "id_incidente",
        Integer,
        ForeignKey("incidentes.id_incidente", ondelete="CASCADE"),
        nullable=False,
    )
    TIPO = Column("tipo", TipoConversacionEnum, nullable=False)
    ID_TENANT = Column(
        "id_tenant", Integer, ForeignKey("tenants.id_tenant"), nullable=True
    )
    FECHA_CREACION = Column("fecha_creacion", DateTime(timezone=True), server_default=func.now())
    FECHA_ACTUALIZACION = Column("fecha_actualizacion", DateTime(timezone=True), onupdate=func.now())


class MENSAJES_CHAT(Base):
    __tablename__ = "mensajes_chat"

    ID_MENSAJE = Column("id_mensaje", Integer, primary_key=True)
    ID_CONVERSACION = Column(
        "id_conversacion",
        Integer,
        ForeignKey("conversaciones.id_conversacion", ondelete="CASCADE"),
        nullable=False,
    )
    ROL_EMISOR = Column("rol_emisor", RolEmisorEnum, nullable=False)
    ID_USUARIO_EMISOR = Column(
        "id_usuario_emisor", Integer, ForeignKey("usuarios.id_usuario"), nullable=True
    )
    CONTENIDO = Column("contenido", Text, nullable=True)
    URL_ADJUNTO = Column("url_adjunto", Text, nullable=True)
    CLAVE_ADJUNTO = Column("clave_adjunto", Text, nullable=True)
    TIPO_ADJUNTO = Column("tipo_adjunto", TipoAdjuntoEnum, nullable=True)
    RELEVANTE_TECNICO = Column("relevante_tecnico", Boolean, server_default="false", nullable=False)
    FECHA_CREACION = Column("fecha_creacion", DateTime(timezone=True), server_default=func.now())
