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
