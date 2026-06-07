// ignore_for_file: non_constant_identifier_names

// ── Auth ──────────────────────────────────────────────────────────────────────

class AuthResponse {
  final String accessToken;
  final String tokenType;

  const AuthResponse({required this.accessToken, required this.tokenType});

  factory AuthResponse.fromJson(Map<String, dynamic> json) => AuthResponse(
        accessToken: json['access_token'] as String? ?? '',
        tokenType: json['token_type'] as String? ?? 'bearer',
      );
}

// ── User ──────────────────────────────────────────────────────────────────────

class User {
  final String idUsuario;
  final String correoElectronico;
  final String nombreCompleto;
  final String? telefono;
  final String rol;
  final bool activo;
  final DateTime? fechaCreacion;

  const User({
    required this.idUsuario,
    required this.correoElectronico,
    required this.nombreCompleto,
    this.telefono,
    required this.rol,
    required this.activo,
    this.fechaCreacion,
  });

  factory User.fromJson(Map<String, dynamic> json) => User(
        idUsuario: json['id_usuario'] as String? ?? '',
        correoElectronico: json['correo_electronico'] as String? ?? '',
        nombreCompleto: json['nombre_completo'] as String? ?? '',
        telefono: json['telefono'] as String?,
        rol: json['rol'] as String? ?? 'CLIENTE',
        activo: json['activo'] as bool? ?? true,
        fechaCreacion:
            DateTime.tryParse(json['fecha_creacion'] as String? ?? ''),
      );

  bool get esTecnico => rol.toUpperCase() == 'TECNICO';

  String get roleLabel {
    switch (rol.toUpperCase()) {
      case 'ADMIN':
        return 'Administrador';
      case 'TALLER':
        return 'Taller';
      case 'CLIENTE':
        return 'Cliente';
      case 'TECNICO':
        return 'Técnico';
      default:
        return rol;
    }
  }

  String get initials {
    final parts = nombreCompleto.trim().split(' ');
    if (parts.length >= 2) {
      return '${parts[0][0]}${parts[1][0]}'.toUpperCase();
    }
    return nombreCompleto.isNotEmpty ? nombreCompleto[0].toUpperCase() : 'U';
  }
}

// ── Vehicle ───────────────────────────────────────────────────────────────────

class Vehicle {
  final String idVehiculo;
  final String idUsuarioCliente;
  final String? marca;
  final String? modelo;
  final int? anio;
  final String? placa;
  final DateTime? fechaCreacion;

  const Vehicle({
    required this.idVehiculo,
    required this.idUsuarioCliente,
    this.marca,
    this.modelo,
    this.anio,
    this.placa,
    this.fechaCreacion,
  });

  factory Vehicle.fromJson(Map<String, dynamic> json) => Vehicle(
        idVehiculo: json['id_vehiculo'] as String? ?? '',
        idUsuarioCliente: json['id_usuario_cliente'] as String? ?? '',
        marca: json['marca'] as String?,
        modelo: json['modelo'] as String?,
        anio: (json['anio'] as num?)?.toInt(),
        placa: json['placa'] as String?,
        fechaCreacion:
            DateTime.tryParse(json['fecha_creacion'] as String? ?? ''),
      );

  String get displayName {
    final parts = <String>[
      if (marca != null && marca!.isNotEmpty) marca!,
      if (modelo != null && modelo!.isNotEmpty) modelo!,
      if (anio != null) '($anio)',
      if (placa != null && placa!.isNotEmpty) '- $placa',
    ];
    return parts.isEmpty ? 'Vehículo sin datos' : parts.join(' ');
  }
}

// ── Evidence ──────────────────────────────────────────────────────────────────

class Evidence {
  final String idEvidencia;
  final String idIncidente;
  final String tipo; // IMAGEN | AUDIO | TEXTO
  final String urlArchivo;
  final String? claveArchivo;
  final String? textoTranscrito;
  final DateTime? fechaCreacion;

  const Evidence({
    required this.idEvidencia,
    required this.idIncidente,
    required this.tipo,
    required this.urlArchivo,
    this.claveArchivo,
    this.textoTranscrito,
    this.fechaCreacion,
  });

  factory Evidence.fromJson(Map<String, dynamic> json) => Evidence(
        idEvidencia: json['id_evidencia'] as String? ?? '',
        idIncidente: json['id_incidente'] as String? ?? '',
        tipo: json['tipo'] as String? ?? '',
        urlArchivo: json['url_archivo'] as String? ?? '',
        claveArchivo: json['clave_archivo'] as String?,
        textoTranscrito: json['texto_transcrito'] as String?,
        fechaCreacion:
            DateTime.tryParse(json['fecha_creacion'] as String? ?? ''),
      );

  bool get isImage => tipo.toUpperCase() == 'IMAGEN';
}

// ── Incident ──────────────────────────────────────────────────────────────────

class Incident {
  // Present in both list (GET /incidents/my) and detail (GET /incidents/{id})
  final String idIncidente;
  final String idUsuarioCliente;
  final String? idVehiculo;
  final double? latitud;
  final double? longitud;
  final String estado;
  final String prioridad;
  final String clasificacion;
  final DateTime? fechaCreacion;

  // Detail-only fields (null when loaded from list endpoint)
  final String? resumenIa;
  final int? tiempoEstimadoLlegadaMinutos;
  final DateTime? fechaActualizacion;
  final List<Evidence> evidencias;

  const Incident({
    required this.idIncidente,
    required this.idUsuarioCliente,
    this.idVehiculo,
    this.latitud,
    this.longitud,
    required this.estado,
    required this.prioridad,
    required this.clasificacion,
    this.fechaCreacion,
    this.resumenIa,
    this.tiempoEstimadoLlegadaMinutos,
    this.fechaActualizacion,
    this.evidencias = const [],
  });

  factory Incident.fromJson(Map<String, dynamic> json) => Incident(
        idIncidente: json['id_incidente'] as String? ?? '',
        idUsuarioCliente: json['id_usuario_cliente'] as String? ?? '',
        idVehiculo: json['id_vehiculo'] as String?,
        latitud: (json['latitud'] as num?)?.toDouble(),
        longitud: (json['longitud'] as num?)?.toDouble(),
        estado: json['estado'] as String? ?? 'PENDIENTE',
        prioridad: json['prioridad'] as String? ?? 'MEDIA',
        clasificacion: json['clasificacion'] as String? ?? 'OTROS',
        fechaCreacion:
            DateTime.tryParse(json['fecha_creacion'] as String? ?? ''),
        resumenIa: json['resumen_ia'] as String?,
        tiempoEstimadoLlegadaMinutos:
            (json['tiempo_estimado_llegada_minutos'] as num?)?.toInt(),
        fechaActualizacion:
            DateTime.tryParse(json['fecha_actualizacion'] as String? ?? ''),
        evidencias: (json['evidencias'] as List<dynamic>?)
                ?.map((e) => Evidence.fromJson(e as Map<String, dynamic>))
                .toList() ??
            const [],
      );

  String get estadoLabel {
    switch (estado.toUpperCase()) {
      case 'PENDIENTE':
        return 'Pendiente';
      case 'EN_PROCESO_IA':
        return 'Procesando IA';
      case 'CLASIFICADO':
        return 'Clasificado';
      case 'ASIGNADO':
        return 'Asignado';
      case 'EN_CAMINO':
        return 'En camino';
      case 'EN_PROCESO':
        return 'En proceso';
      case 'ATENDIDO':
        return 'Atendido';
      case 'CANCELADO':
        return 'Cancelado';
      case 'INCIERTO':
        return 'Incierto';
      default:
        return estado;
    }
  }

  String get clasificacionLabel {
    switch (clasificacion.toUpperCase()) {
      case 'BATERIA':
        return 'Batería';
      case 'LLANTA':
        return 'Llanta';
      case 'CHOQUE':
        return 'Choque';
      case 'MOTOR':
        return 'Motor';
      case 'OTROS':
        return 'Otros';
      case 'INCIERTO':
        return 'Incierto';
      default:
        return clasificacion;
    }
  }

  String get prioridadLabel {
    switch (prioridad.toUpperCase()) {
      case 'ALTA':
        return 'Alta';
      case 'MEDIA':
        return 'Media';
      case 'BAJA':
        return 'Baja';
      default:
        return prioridad;
    }
  }

  bool get isActive {
    final s = estado.toUpperCase();
    return s == 'PENDIENTE' ||
        s == 'EN_PROCESO_IA' ||
        s == 'CLASIFICADO' ||
        s == 'ASIGNADO' ||
        s == 'EN_CAMINO' ||
        s == 'EN_PROCESO';
  }

  /// Returns the transcribed text evidence if available (submitted as texto_descripcion).
  String? get textoDescripcion {
    try {
      return evidencias
          .firstWhere((e) => e.tipo.toUpperCase() == 'TEXTO')
          .textoTranscrito;
    } catch (_) {
      return null;
    }
  }
}

// ── Assignment ────────────────────────────────────────────────────────────────

class Assignment {
  final String idAsignacion;
  final String idIncidente;
  final String idTaller;
  final String? idTecnico;
  final DateTime? fechaAsignacion;
  final num? montoCotizado;
  final int? tiempoEstimadoReparacion;
  final String? notasCotizacion;
  final bool? cotizacionAceptada;

  const Assignment({
    required this.idAsignacion,
    required this.idIncidente,
    required this.idTaller,
    this.idTecnico,
    this.fechaAsignacion,
    this.montoCotizado,
    this.tiempoEstimadoReparacion,
    this.notasCotizacion,
    this.cotizacionAceptada,
  });

  factory Assignment.fromJson(Map<String, dynamic> json) => Assignment(
        idAsignacion: json['id_asignacion'] as String? ?? '',
        idIncidente: json['id_incidente'] as String? ?? '',
        idTaller: json['id_taller'] as String? ?? '',
        idTecnico: json['id_tecnico'] as String?,
        fechaAsignacion:
            DateTime.tryParse(json['fecha_asignacion'] as String? ?? ''),
        montoCotizado: _toNum(json['monto_cotizado']),
        tiempoEstimadoReparacion:
            (json['tiempo_estimado_reparacion'] as num?)?.toInt(),
        notasCotizacion: json['notas_cotizacion'] as String?,
        cotizacionAceptada: json['cotizacion_aceptada'] as bool?,
      );
}

class CotizacionDetalle {
  final String idAsignacion;
  final String idIncidente;
  final num? montoCotizado;
  final int? tiempoEstimadoReparacion;
  final String? notasCotizacion;
  final bool? cotizacionAceptada;
  final String estadoIncidente;
  final DateTime? timestamp;

  const CotizacionDetalle({
    required this.idAsignacion,
    required this.idIncidente,
    this.montoCotizado,
    this.tiempoEstimadoReparacion,
    this.notasCotizacion,
    this.cotizacionAceptada,
    required this.estadoIncidente,
    this.timestamp,
  });

  factory CotizacionDetalle.fromJson(Map<String, dynamic> json) =>
      CotizacionDetalle(
        idAsignacion: json['id_asignacion'] as String? ?? '',
        idIncidente: json['id_incidente'] as String? ?? '',
        montoCotizado: _toNum(json['monto_cotizado']),
        tiempoEstimadoReparacion:
            (json['tiempo_estimado_reparacion'] as num?)?.toInt(),
        notasCotizacion: json['notas_cotizacion'] as String?,
        cotizacionAceptada: json['cotizacion_aceptada'] as bool?,
        estadoIncidente: json['estado_incidente'] as String? ?? '',
        timestamp: DateTime.tryParse(json['timestamp'] as String? ?? ''),
      );

  bool get tieneMonto => montoCotizado != null;
  bool get pendienteRespuesta => tieneMonto && cotizacionAceptada == null;
}

// ── TechnicianAssignment ──────────────────────────────────────────────────────

class TechnicianAssignment {
  final String idAsignacion;
  final String idIncidente;
  final String idTaller;
  final String idTecnico;
  final String estadoIncidente;
  final String clasificacion;
  final String prioridad;
  final String? resumenIa;
  final double? latitud;
  final double? longitud;
  final int? tiempoEstimadoLlegadaMinutos;
  final String? clienteNombre;
  final String? clienteTelefono;
  final DateTime? fechaAsignacion;
  final DateTime? fechaCreacionIncidente;

  const TechnicianAssignment({
    required this.idAsignacion,
    required this.idIncidente,
    required this.idTaller,
    required this.idTecnico,
    required this.estadoIncidente,
    required this.clasificacion,
    required this.prioridad,
    this.resumenIa,
    this.latitud,
    this.longitud,
    this.tiempoEstimadoLlegadaMinutos,
    this.clienteNombre,
    this.clienteTelefono,
    this.fechaAsignacion,
    this.fechaCreacionIncidente,
  });

  factory TechnicianAssignment.fromJson(Map<String, dynamic> json) =>
      TechnicianAssignment(
        idAsignacion: json['id_asignacion'] as String? ?? '',
        idIncidente: json['id_incidente'] as String? ?? '',
        idTaller: json['id_taller'] as String? ?? '',
        idTecnico: json['id_tecnico'] as String? ?? '',
        estadoIncidente: json['estado_incidente'] as String? ?? 'ASIGNADO',
        clasificacion: json['clasificacion'] as String? ?? 'OTROS',
        prioridad: json['prioridad'] as String? ?? 'MEDIA',
        resumenIa: json['resumen_ia'] as String?,
        latitud: (json['latitud'] as num?)?.toDouble(),
        longitud: (json['longitud'] as num?)?.toDouble(),
        tiempoEstimadoLlegadaMinutos:
            (json['tiempo_estimado_llegada_minutos'] as num?)?.toInt(),
        clienteNombre: json['cliente_nombre'] as String?,
        clienteTelefono: json['cliente_telefono'] as String?,
        fechaAsignacion:
            DateTime.tryParse(json['fecha_asignacion'] as String? ?? ''),
        fechaCreacionIncidente: DateTime.tryParse(
            json['fecha_creacion_incidente'] as String? ?? ''),
      );

  /// Etiqueta visible al usuario para el estado actual
  String get estadoLabel {
    switch (estadoIncidente.toUpperCase()) {
      case 'ASIGNADO':
        return 'Nuevo trabajo asignado';
      case 'EN_CAMINO':
        return 'En camino al sitio';
      case 'EN_PROCESO':
        return 'Trabajando en el sitio';
      case 'ATENDIDO':
        return 'Trabajo finalizado';
      default:
        return estadoIncidente;
    }
  }

  /// Siguiente estado en la máquina de estados (null si no hay transición)
  String? get siguienteEstado {
    switch (estadoIncidente.toUpperCase()) {
      case 'ASIGNADO':
        return 'EN_CAMINO';
      case 'EN_CAMINO':
        return 'EN_PROCESO';
      case 'EN_PROCESO':
        return 'ATENDIDO';
      default:
        return null;
    }
  }

  /// Etiqueta del botón de acción para el siguiente estado
  String? get accionLabel {
    switch (estadoIncidente.toUpperCase()) {
      case 'ASIGNADO':
        return 'IR AL SITIO';
      case 'EN_CAMINO':
        return 'COMENZAR TRABAJO';
      case 'EN_PROCESO':
        return 'FINALIZAR TRABAJO';
      default:
        return null;
    }
  }

  bool get tieneAccionDisponible => siguienteEstado != null;
}

class TechnicianLocation {
  final String idIncidente;
  final String? idTecnico;
  final double latitud;
  final double longitud;
  final DateTime? timestamp;

  const TechnicianLocation({
    required this.idIncidente,
    this.idTecnico,
    required this.latitud,
    required this.longitud,
    this.timestamp,
  });

  factory TechnicianLocation.fromJson(Map<String, dynamic> json) =>
      TechnicianLocation(
        idIncidente:
            (json['incidente_id'] ?? json['id_incidente']) as String? ?? '',
        idTecnico: (json['tecnico_id'] ?? json['id_tecnico']) as String?,
        latitud: _toDouble(json['lat'] ?? json['latitud']) ?? 0,
        longitud: _toDouble(json['lng'] ?? json['longitud']) ?? 0,
        timestamp: DateTime.tryParse(json['timestamp'] as String? ?? ''),
      );
}

double? _toDouble(dynamic value) {
  if (value is num) return value.toDouble();
  if (value is String) return double.tryParse(value);
  return null;
}

// ── Oferta de cotización (flujo InDrive) ──────────────────────────────────────

class CotizacionOferta {
  final String idTaller;
  final String nombreTaller;
  final double distanciaKm;
  final double monto;
  final String descripcion;
  final String? idTecnicoSugerido;

  const CotizacionOferta({
    required this.idTaller,
    required this.nombreTaller,
    required this.distanciaKm,
    required this.monto,
    required this.descripcion,
    this.idTecnicoSugerido,
  });

  factory CotizacionOferta.fromJson(Map<String, dynamic> json) => CotizacionOferta(
        idTaller: json['id_taller'] as String? ?? '',
        nombreTaller: json['nombre_taller'] as String? ?? 'Taller',
        distanciaKm: _toDouble(json['distancia_km']) ?? 0,
        monto: _toDouble(json['monto']) ?? 0,
        descripcion: json['descripcion'] as String? ?? '',
        idTecnicoSugerido: json['id_tecnico_sugerido'] as String?,
      );
}

// ── WebSocket Notification ────────────────────────────────────────────────────

class WsNotification {
  final String tipo; // "conectado" | "estado_actualizado"
  final String incidenteId;
  final String? mensaje;
  final String? nuevoEstado;
  final String timestamp;

  const WsNotification({
    required this.tipo,
    required this.incidenteId,
    this.mensaje,
    this.nuevoEstado,
    required this.timestamp,
  });

  factory WsNotification.fromJson(Map<String, dynamic> json) => WsNotification(
        tipo: json['tipo'] as String? ?? '',
        incidenteId: json['incidente_id'] as String? ?? '',
        mensaje: json['mensaje'] as String?,
        nuevoEstado: json['nuevo_estado'] as String?,
        timestamp: json['timestamp'] as String? ?? '',
      );

  String get displayTitle {
    switch (tipo) {
      case 'conectado':
        return 'Conectado';
      case 'estado_actualizado':
        return 'Estado actualizado → ${nuevoEstado ?? ''}';
      default:
        return tipo;
    }
  }
}

// ── EstadoPago ────────────────────────────────────────────────────────────────

enum EstadoPago {
  noPago,
  pendiente,
  pagado,
  rechazado;

  static EstadoPago fromString(String s) {
    switch (s.toUpperCase()) {
      case 'NO_PAGO':
        return EstadoPago.noPago;
      case 'PENDIENTE':
        return EstadoPago.pendiente;
      case 'PAGADO':
        return EstadoPago.pagado;
      case 'RECHAZADO':
        return EstadoPago.rechazado;
      default:
        return EstadoPago.noPago;
    }
  }

  String get label {
    switch (this) {
      case EstadoPago.noPago:
        return 'Pendiente de pago';
      case EstadoPago.pendiente:
        return 'Esperando confirmación';
      case EstadoPago.pagado:
        return 'Pagado';
      case EstadoPago.rechazado:
        return 'Rechazado - reintentar';
    }
  }

  String get backendValue {
    switch (this) {
      case EstadoPago.noPago:
        return 'NO_PAGO';
      case EstadoPago.pendiente:
        return 'PENDIENTE';
      case EstadoPago.pagado:
        return 'PAGADO';
      case EstadoPago.rechazado:
        return 'RECHAZADO';
    }
  }
}

// ── Payment ───────────────────────────────────────────────────────────────────

num? _toNum(dynamic v) {
  if (v == null) return null;
  if (v is num) return v;
  if (v is String) return num.tryParse(v);
  return null;
}

class Payment {
  final String idPago;
  final String idIncidente;
  final String? idTaller;
  final String? idAsignacion;
  final num monto;
  final num? comisionPlataforma;
  final EstadoPago estado;
  final String? comprobanteUrl;
  final String? notasCliente;
  final String? motivoRechazo;
  final DateTime? fechaCreacion;
  final DateTime? fechaMarcadoPago;
  final DateTime? fechaConfirmacion;
  final DateTime? fechaRechazo;

  const Payment({
    required this.idPago,
    required this.idIncidente,
    this.idTaller,
    this.idAsignacion,
    required this.monto,
    this.comisionPlataforma,
    required this.estado,
    this.comprobanteUrl,
    this.notasCliente,
    this.motivoRechazo,
    this.fechaCreacion,
    this.fechaMarcadoPago,
    this.fechaConfirmacion,
    this.fechaRechazo,
  });

  factory Payment.fromJson(Map<String, dynamic> json) => Payment(
        idPago: json['id_pago'] as String? ?? '',
        idIncidente: json['id_incidente'] as String? ?? '',
        idTaller: json['id_taller'] as String?,
        idAsignacion: json['id_asignacion'] as String?,
        monto: _toNum(json['monto']) ?? 0,
        comisionPlataforma: _toNum(json['comision_plataforma']),
        estado: EstadoPago.fromString(json['estado'] as String? ?? 'NO_PAGO'),
        comprobanteUrl: json['comprobante_url'] as String?,
        notasCliente: json['notas_cliente'] as String?,
        motivoRechazo: json['motivo_rechazo'] as String?,
        fechaCreacion:
            DateTime.tryParse(json['fecha_creacion'] as String? ?? ''),
        fechaMarcadoPago:
            DateTime.tryParse(json['fecha_marcado_pago'] as String? ?? ''),
        fechaConfirmacion:
            DateTime.tryParse(json['fecha_confirmacion'] as String? ?? ''),
        fechaRechazo: DateTime.tryParse(json['fecha_rechazo'] as String? ?? ''),
      );
}

// ── Offline emergency ─────────────────────────────────────────────────────────

class EmergenciaLocal {
  final String id_local;
  final String descripcion;
  final double latitud;
  final double longitud;
  final String? id_vehiculo;
  final DateTime fecha_creacion;
  bool sincronizado;
  String? error_sync;

  EmergenciaLocal({
    required this.id_local,
    required this.descripcion,
    required this.latitud,
    required this.longitud,
    this.id_vehiculo,
    required this.fecha_creacion,
    this.sincronizado = false,
    this.error_sync,
  });

  Map<String, dynamic> toJson() => {
        'id_local': id_local,
        'descripcion': descripcion,
        'latitud': latitud,
        'longitud': longitud,
        'id_vehiculo': id_vehiculo,
        'fecha_creacion': fecha_creacion.toIso8601String(),
        'sincronizado': sincronizado,
        'error_sync': error_sync,
      };

  factory EmergenciaLocal.fromJson(Map<String, dynamic> json) =>
      EmergenciaLocal(
        id_local: json['id_local'] as String? ?? '',
        descripcion: json['descripcion'] as String? ?? '',
        latitud: (json['latitud'] as num?)?.toDouble() ?? 0,
        longitud: (json['longitud'] as num?)?.toDouble() ?? 0,
        id_vehiculo: json['id_vehiculo'] as String?,
        fecha_creacion: DateTime.tryParse(
              json['fecha_creacion'] as String? ?? '',
            ) ??
            DateTime.now(),
        sincronizado: json['sincronizado'] as bool? ?? false,
        error_sync: json['error_sync'] as String?,
      );
}
