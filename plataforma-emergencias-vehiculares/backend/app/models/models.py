from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey, Enum, DECIMAL, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
from app.core.database import Base
import uuid

# ==================== ENUMS ====================
RolEnum = Enum('CLIENTE', 'TALLER', 'ADMIN', name='rol_enum')
EstadoIncidenteEnum = Enum('PENDIENTE', 'EN_PROCESO_IA', 'CLASIFICADO', 'ASIGNADO',
                           'EN_CAMINO', 'EN_PROCESO', 'ATENDIDO', 'CANCELADO', 'INCIERTO',
                           name='estado_incidente_enum')
PrioridadEnum = Enum('BAJA', 'MEDIA', 'ALTA', name='prioridad_enum')
ClasificacionEnum = Enum('BATERIA', 'LLANTA', 'CHOQUE', 'MOTOR', 'OTROS', 'INCIERTO',
                         name='clasificacion_enum')
TipoEvidenciaEnum = Enum('IMAGEN', 'AUDIO', 'TEXTO', name='tipo_evidencia_enum')
EstadoPagoEnum = Enum('PENDIENTE', 'PAGADO', 'RECHAZADO', name='estado_pago_enum')

# ==================== MODELOS ====================

class USUARIOS(Base):
    __tablename__ = "USUARIOS"

    ID_USUARIO = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    CORREO_ELECTRONICO = Column(String(255), unique=True, nullable=False)
    HASH_CONTRASENA = Column(Text, nullable=False)
    NOMBRE_COMPLETO = Column(String(255), nullable=False)
    TELEFONO = Column(String(20))
    ROL = Column(RolEnum, nullable=False)
    ACTIVO = Column(Boolean, default=True)
    FECHA_CREACION = Column(DateTime(timezone=True), server_default=func.now())
    FECHA_ACTUALIZACION = Column(DateTime(timezone=True), onupdate=func.now())
    FECHA_ELIMINACION = Column(DateTime(timezone=True), nullable=True)


class CLIENTES(Base):
    __tablename__ = "CLIENTES"

    ID_USUARIO = Column(UUID(as_uuid=True), ForeignKey("USUARIOS.ID_USUARIO", ondelete="CASCADE"), primary_key=True)


class TALLERES(Base):
    __tablename__ = "TALLERES"

    ID_TALLER = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ID_USUARIO = Column(UUID(as_uuid=True), ForeignKey("USUARIOS.ID_USUARIO", ondelete="CASCADE"), unique=True)
    NOMBRE_NEGOCIO = Column(String(255), nullable=False)
    NIT = Column(String(50), unique=True)
    DIRECCION = Column(Text)
    TASA_COMISION = Column(DECIMAL(5, 2), default=10.00)
    ACTIVO = Column(Boolean, default=True)
    FECHA_CREACION = Column(DateTime(timezone=True), server_default=func.now())
    FECHA_ACTUALIZACION = Column(DateTime(timezone=True), onupdate=func.now())


class TECNICOS(Base):
    __tablename__ = "TECNICOS"

    ID_TECNICO = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ID_TALLER = Column(UUID(as_uuid=True), ForeignKey("TALLERES.ID_TALLER", ondelete="CASCADE"), nullable=False)
    NOMBRE_COMPLETO = Column(String(255), nullable=False)
    TELEFONO = Column(String(20))
    DISPONIBLE = Column(Boolean, default=True)
    UBICACION_ACTUAL = Column(Geography(geometry_type='POINT', srid=4326))
    FECHA_CREACION = Column(DateTime(timezone=True), server_default=func.now())
    FECHA_ACTUALIZACION = Column(DateTime(timezone=True), onupdate=func.now())


class VEHICULOS(Base):
    __tablename__ = "VEHICULOS"

    ID_VEHICULO = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ID_USUARIO_CLIENTE = Column(UUID(as_uuid=True), ForeignKey("USUARIOS.ID_USUARIO", ondelete="CASCADE"), nullable=False)
    MARCA = Column(String(100))
    MODELO = Column(String(100))
    ANIO = Column(Integer)
    PLACA = Column(String(20), unique=True)
    FECHA_CREACION = Column(DateTime(timezone=True), server_default=func.now())
    FECHA_ACTUALIZACION = Column(DateTime(timezone=True), onupdate=func.now())


class INCIDENTES(Base):
    __tablename__ = "INCIDENTES"

    ID_INCIDENTE = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ID_USUARIO_CLIENTE = Column(UUID(as_uuid=True), ForeignKey("USUARIOS.ID_USUARIO"), nullable=False)
    ID_VEHICULO = Column(UUID(as_uuid=True), ForeignKey("VEHICULOS.ID_VEHICULO"))
    UBICACION = Column(Geography(geometry_type='POINT', srid=4326), nullable=False)
    ESTADO = Column(EstadoIncidenteEnum, default="PENDIENTE")
    PRIORIDAD = Column(PrioridadEnum, default="MEDIA")
    CLASIFICACION = Column(ClasificacionEnum, default="OTROS")
    RESUMEN_IA = Column(Text)
    TIEMPO_ESTIMADO_LLEGADA_MINUTOS = Column(Integer)
    FECHA_CREACION = Column(DateTime(timezone=True), server_default=func.now())
    FECHA_ACTUALIZACION = Column(DateTime(timezone=True), onupdate=func.now())


class EVIDENCIAS(Base):
    __tablename__ = "EVIDENCIAS"

    ID_EVIDENCIA = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ID_INCIDENTE = Column(UUID(as_uuid=True), ForeignKey("INCIDENTES.ID_INCIDENTE", ondelete="CASCADE"), nullable=False)
    TIPO = Column(TipoEvidenciaEnum, nullable=False)
    URL_ARCHIVO = Column(Text, nullable=False)
    CLAVE_ARCHIVO = Column(Text)
    TEXTO_TRANSCRITO = Column(Text)
    FECHA_CREACION = Column(DateTime(timezone=True), server_default=func.now())


class HISTORIAL_INCIDENTES(Base):
    __tablename__ = "HISTORIAL_INCIDENTES"

    ID_HISTORIAL = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ID_INCIDENTE = Column(UUID(as_uuid=True), ForeignKey("INCIDENTES.ID_INCIDENTE", ondelete="CASCADE"), nullable=False)
    ESTADO = Column(EstadoIncidenteEnum, nullable=False)
    NOTAS = Column(Text)
    ID_USUARIO_CAMBIO = Column(UUID(as_uuid=True), ForeignKey("USUARIOS.ID_USUARIO"))
    FECHA_CAMBIO = Column(DateTime(timezone=True), server_default=func.now())


class ASIGNACIONES(Base):
    __tablename__ = "ASIGNACIONES"

    ID_ASIGNACION = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ID_INCIDENTE = Column(UUID(as_uuid=True), ForeignKey("INCIDENTES.ID_INCIDENTE"), unique=True)
    ID_TALLER = Column(UUID(as_uuid=True), ForeignKey("TALLERES.ID_TALLER"))
    ID_TECNICO = Column(UUID(as_uuid=True), ForeignKey("TECNICOS.ID_TECNICO"))
    FECHA_ASIGNACION = Column(DateTime(timezone=True), server_default=func.now())
    FECHA_ACEPTACION = Column(DateTime(timezone=True))
    FECHA_RECHAZO = Column(DateTime(timezone=True))
    MOTIVO_RECHAZO = Column(Text)


class PAGOS(Base):
    __tablename__ = "PAGOS"

    ID_PAGO = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ID_INCIDENTE = Column(UUID(as_uuid=True), ForeignKey("INCIDENTES.ID_INCIDENTE"))
    ID_USUARIO_CLIENTE = Column(UUID(as_uuid=True), ForeignKey("USUARIOS.ID_USUARIO"))
    MONTO = Column(DECIMAL(10, 2), nullable=False)
    COMISION_PLATAFORMA = Column(DECIMAL(10, 2), nullable=False)
    ESTADO = Column(EstadoPagoEnum, default="PENDIENTE")
    METODO_PAGO = Column(String(50))
    ID_TRANSACCION = Column(String(255))
    FECHA_CREACION = Column(DateTime(timezone=True), server_default=func.now())