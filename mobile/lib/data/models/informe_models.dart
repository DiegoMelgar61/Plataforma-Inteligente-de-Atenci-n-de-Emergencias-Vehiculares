int _parseInt(dynamic v, [int fallback = 0]) {
  if (v is int) return v;
  if (v is String) return int.tryParse(v) ?? fallback;
  return fallback;
}

// ── InformeServicio ───────────────────────────────────────────────────────────

class InformeServicio {
  final int idInforme;
  final int idIncidente;
  final String estado; // GENERANDO | LISTO | FALLIDO
  final String urlArchivo;
  final bool generadoPorIa;
  final bool correoEnviado;
  final DateTime fechaCreacion;

  const InformeServicio({
    required this.idInforme,
    required this.idIncidente,
    required this.estado,
    required this.urlArchivo,
    required this.generadoPorIa,
    required this.correoEnviado,
    required this.fechaCreacion,
  });

  factory InformeServicio.fromJson(Map<String, dynamic> json) =>
      InformeServicio(
        idInforme: _parseInt(json['id_informe']),
        idIncidente: _parseInt(json['id_incidente']),
        estado: json['estado'] as String? ?? 'GENERANDO',
        urlArchivo: json['url_archivo'] as String? ?? '',
        generadoPorIa: json['generado_por_ia'] as bool? ?? false,
        correoEnviado: json['correo_enviado'] as bool? ?? false,
        fechaCreacion:
            DateTime.tryParse(json['fecha_creacion'] as String? ?? '') ??
                DateTime.now(),
      );

  bool get estaListo => estado.toUpperCase() == 'LISTO';
}
