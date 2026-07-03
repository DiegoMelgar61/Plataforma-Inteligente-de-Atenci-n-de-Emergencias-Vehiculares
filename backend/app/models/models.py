from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey, Enum, DECIMAL, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
from app.core.database import Base
import uuid

# ==================== ENUMS ====================
EstadoIncidenteEnum = Enum('PENDIENTE', 'EN_PROCESO_IA', 'CLASIFICADO', 'ASIGNADO',
                           'EN_CAMINO', 'EN_PROCESO', 'ATENDIDO', 'CANCELADO', 'INCIERTO',
                           name='estado_incidente_enum')
PrioridadEnum = Enum('BAJA', 'MEDIA', 'ALTA', name='prioridad_enum')
ClasificacionEnum = Enum('BATERIA', 'LLANTA', 'CHOQUE', 'MOTOR', 'OTROS', 'INCIERTO',
                         name='clasificacion_enum')
TipoEvidenciaEnum = Enum('IMAGEN', 'AUDIO', 'TEXTO', name='tipo_evidencia_enum')
EstadoPagoEnum = Enum('NO_PAGO', 'PENDIENTE', 'PAGADO', 'RECHAZADO', name='estado_pago_enum')

# ==================== MODELOS ====================

class TALLERES(Base):
    __tablename__ = "talleres"

    ID_TALLER = Column("id_taller", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ID_USUARIO = Column("id_usuario", UUID(as_uuid=True), ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), unique=True)
    NOMBRE_NEGOCIO = Column("nombre_negocio", String(255), nullable=False)
    NIT = Column("nit", String(50), unique=True)
    DIRECCION = Column("direccion", Text)
    TASA_COMISION = Column("tasa_comision", DECIMAL(5, 2), default=10.00)
    LATITUD = Column("latitud", DECIMAL(10, 7), nullable=True)
    LONGITUD = Column("longitud", DECIMAL(10, 7), nullable=True)
    ACTIVO = Column("activo", Boolean, default=True)
    FECHA_CREACION = Column("fecha_creacion", DateTime(timezone=True), server_default=func.now())
    FECHA_ACTUALIZACION = Column("fecha_actualizacion", DateTime(timezone=True), onupdate=func.now())
    ID_TENANT = Column("id_tenant", UUID(as_uuid=True), ForeignKey("tenants.id_tenant"), nullable=True)
    tenant = relationship("Tenant", foreign_keys=[ID_TENANT])


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


class VEHICULOS(Base):
    __tablename__ = "vehiculos"

    ID_VEHICULO = Column("id_vehiculo", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ID_USUARIO_CLIENTE = Column("id_usuario_cliente", UUID(as_uuid=True), ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False)
    MARCA = Column("marca", String(100))
    MODELO = Column("modelo", String(100))
    ANIO = Column("anio", Integer)
    PLACA = Column("placa", String(20), unique=True)
    FECHA_CREACION = Column("fecha_creacion", DateTime(timezone=True), server_default=func.now())
    FECHA_ACTUALIZACION = Column("fecha_actualizacion", DateTime(timezone=True), onupdate=func.now())


class INCIDENTES(Base):
    __tablename__ = "incidentes"

    ID_INCIDENTE = Column("id_incidente", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ID_USUARIO_CLIENTE = Column("id_usuario_cliente", UUID(as_uuid=True), ForeignKey("usuarios.id_usuario"), nullable=False)
    ID_VEHICULO = Column("id_vehiculo", UUID(as_uuid=True), ForeignKey("vehiculos.id_vehiculo"))
    UBICACION = Column("ubicacion", Geography(geometry_type='POINT', srid=4326), nullable=False)
    ESTADO = Column("estado", EstadoIncidenteEnum, default="PENDIENTE")
    PRIORIDAD = Column("prioridad", PrioridadEnum, default="MEDIA")
    CLASIFICACION = Column("clasificacion", ClasificacionEnum, default="OTROS")
    RESUMEN_IA = Column("resumen_ia", Text)
    TIEMPO_ESTIMADO_LLEGADA_MINUTOS = Column("tiempo_estimado_llegada_minutos", Integer)
    ID_LOCAL = Column("id_local", String(36), nullable=True)
    FECHA_CREACION = Column("fecha_creacion", DateTime(timezone=True), server_default=func.now())
    FECHA_ACTUALIZACION = Column("fecha_actualizacion", DateTime(timezone=True), onupdate=func.now())
    ID_TENANT = Column("id_tenant", UUID(as_uuid=True), ForeignKey("tenants.id_tenant"), nullable=True)
    tenant = relationship("Tenant", foreign_keys=[ID_TENANT])


class EVIDENCIAS(Base):
    __tablename__ = "evidencias"

    ID_EVIDENCIA = Column("id_evidencia", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ID_INCIDENTE = Column("id_incidente", UUID(as_uuid=True), ForeignKey("incidentes.id_incidente", ondelete="CASCADE"), nullable=False)
    TIPO = Column("tipo", TipoEvidenciaEnum, nullable=False)
    URL_ARCHIVO = Column("url_archivo", Text, nullable=False)
    CLAVE_ARCHIVO = Column("clave_archivo", Text)
    TEXTO_TRANSCRITO = Column("texto_transcrito", Text)
    ANALISIS_IA = Column("analisis_ia", Text, nullable=True)
    FECHA_CREACION = Column("fecha_creacion", DateTime(timezone=True), server_default=func.now())


class HISTORIAL_INCIDENTES(Base):
    __tablename__ = "historial_incidentes"

    ID_HISTORIAL = Column("id_historial", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ID_INCIDENTE = Column("id_incidente", UUID(as_uuid=True), ForeignKey("incidentes.id_incidente", ondelete="CASCADE"), nullable=False)
    ESTADO = Column("estado", EstadoIncidenteEnum, nullable=False)
    NOTAS = Column("notas", Text)
    ID_USUARIO_CAMBIO = Column("id_usuario_cambio", UUID(as_uuid=True), ForeignKey("usuarios.id_usuario"))
    FECHA_CAMBIO = Column("fecha_cambio", DateTime(timezone=True), server_default=func.now())


class ASIGNACIONES(Base):
    __tablename__ = "asignaciones"

    ID_ASIGNACION = Column("id_asignacion", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ID_INCIDENTE = Column("id_incidente", UUID(as_uuid=True), ForeignKey("incidentes.id_incidente"), unique=True)
    ID_TALLER = Column("id_taller", UUID(as_uuid=True), ForeignKey("talleres.id_taller"))
    ID_TECNICO = Column("id_tecnico", UUID(as_uuid=True), ForeignKey("tecnicos.id_tecnico"))
    FECHA_ASIGNACION = Column("fecha_asignacion", DateTime(timezone=True), server_default=func.now())
    FECHA_ACEPTACION = Column("fecha_aceptacion", DateTime(timezone=True))
    FECHA_RECHAZO = Column("fecha_rechazo", DateTime(timezone=True))
    MOTIVO_RECHAZO = Column("motivo_rechazo", Text)
    MONTO_COTIZADO = Column("monto_cotizado", DECIMAL(10, 2), nullable=True)
    TIEMPO_ESTIMADO_REPARACION = Column("tiempo_estimado_reparacion", Integer, nullable=True)
    COTIZACION_ACEPTADA = Column("cotizacion_aceptada", Boolean, nullable=True)
    NOTAS_COTIZACION = Column("notas_cotizacion", Text, nullable=True)


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


