// ignore_for_file: non_constant_identifier_names

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
