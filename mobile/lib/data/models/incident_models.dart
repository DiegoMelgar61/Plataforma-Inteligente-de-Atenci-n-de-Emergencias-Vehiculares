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

// ── CotizacionDetalle ─────────────────────────────────────────────────────────

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

// ── Resultado de cancelación ──────────────────────────────────────────────────

class CancelacionResultado {
  final bool conPenalidad;
  final double montoMulta;
  final String mensaje;

  const CancelacionResultado({
    required this.conPenalidad,
    required this.montoMulta,
    required this.mensaje,
  });

  factory CancelacionResultado.fromJson(Map<String, dynamic> json) =>
      CancelacionResultado(
        conPenalidad: json['con_penalidad'] as bool? ?? false,
        montoMulta: _toDouble(json['monto_multa']) ?? 0,
        mensaje: json['mensaje'] as String? ?? 'Servicio cancelado',
      );
}
