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
