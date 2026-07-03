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

num? _toNum(dynamic v) {
  if (v == null) return null;
  if (v is num) return v;
  if (v is String) return num.tryParse(v);
  return null;
}

double? _toDouble(dynamic value) {
  if (value is num) return value.toDouble();
  if (value is String) return double.tryParse(value);
  return null;
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
