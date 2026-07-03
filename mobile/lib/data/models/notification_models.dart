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
