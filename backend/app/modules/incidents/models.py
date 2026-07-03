from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey, Enum, DECIMAL, func
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
from app.core.database import Base

# ==================== ENUMS ====================
EstadoIncidenteEnum = Enum('PENDIENTE', 'EN_PROCESO_IA', 'CLASIFICADO', 'ASIGNADO',
                           'EN_CAMINO', 'EN_PROCESO', 'ATENDIDO', 'CANCELADO', 'INCIERTO',
                           name='estado_incidente_enum')
PrioridadEnum = Enum('BAJA', 'MEDIA', 'ALTA', name='prioridad_enum')
ClasificacionEnum = Enum('BATERIA', 'LLANTA', 'CHOQUE', 'MOTOR', 'OTROS', 'INCIERTO',
                         name='clasificacion_enum')
TipoEvidenciaEnum = Enum('IMAGEN', 'AUDIO', 'TEXTO', name='tipo_evidencia_enum')

# ==================== MODELOS ====================

class INCIDENTES(Base):
    __tablename__ = "incidentes"

    ID_INCIDENTE = Column("id_incidente", Integer, primary_key=True)
    ID_USUARIO_CLIENTE = Column("id_usuario_cliente", Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    ID_VEHICULO = Column("id_vehiculo", Integer, ForeignKey("vehiculos.id_vehiculo"))
    UBICACION = Column("ubicacion", Geography(geometry_type='POINT', srid=4326), nullable=False)
    ESTADO = Column("estado", EstadoIncidenteEnum, default="PENDIENTE")
    PRIORIDAD = Column("prioridad", PrioridadEnum, default="MEDIA")
    CLASIFICACION = Column("clasificacion", ClasificacionEnum, default="OTROS")
    RESUMEN_IA = Column("resumen_ia", Text)
    TIEMPO_ESTIMADO_LLEGADA_MINUTOS = Column("tiempo_estimado_llegada_minutos", Integer)
    ID_LOCAL = Column("id_local", String(36), nullable=True)
    FECHA_CREACION = Column("fecha_creacion", DateTime(timezone=True), server_default=func.now())
    FECHA_ACTUALIZACION = Column("fecha_actualizacion", DateTime(timezone=True), onupdate=func.now())
    ID_TENANT = Column("id_tenant", Integer, ForeignKey("tenants.id_tenant"), nullable=True)
    tenant = relationship("Tenant", foreign_keys=[ID_TENANT])


class EVIDENCIAS(Base):
    __tablename__ = "evidencias"

    ID_EVIDENCIA = Column("id_evidencia", Integer, primary_key=True)
    ID_INCIDENTE = Column("id_incidente", Integer, ForeignKey("incidentes.id_incidente", ondelete="CASCADE"), nullable=False)
    TIPO = Column("tipo", TipoEvidenciaEnum, nullable=False)
    URL_ARCHIVO = Column("url_archivo", Text, nullable=False)
    CLAVE_ARCHIVO = Column("clave_archivo", Text)
    TEXTO_TRANSCRITO = Column("texto_transcrito", Text)
    ANALISIS_IA = Column("analisis_ia", Text, nullable=True)
    FECHA_CREACION = Column("fecha_creacion", DateTime(timezone=True), server_default=func.now())


class HISTORIAL_INCIDENTES(Base):
    __tablename__ = "historial_incidentes"

    ID_HISTORIAL = Column("id_historial", Integer, primary_key=True)
    ID_INCIDENTE = Column("id_incidente", Integer, ForeignKey("incidentes.id_incidente", ondelete="CASCADE"), nullable=False)
    ESTADO = Column("estado", EstadoIncidenteEnum, nullable=False)
    NOTAS = Column("notas", Text)
    ID_USUARIO_CAMBIO = Column("id_usuario_cambio", Integer, ForeignKey("usuarios.id_usuario"))
    FECHA_CAMBIO = Column("fecha_cambio", DateTime(timezone=True), server_default=func.now())


