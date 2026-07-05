int _parseInt(dynamic v, [int fallback = 0]) {
  if (v is int) return v;
  if (v is String) return int.tryParse(v) ?? fallback;
  return fallback;
}

// ── MensajeChat ───────────────────────────────────────────────────────────────

class MensajeChat {
  final int idMensaje;
  final String rolEmisor; // CLIENTE | TECNICO | IA
  final String? contenido;
  final String? urlAdjunto;
  final String? tipoAdjunto; // IMAGEN | ARCHIVO
  final DateTime fechaCreacion;

  const MensajeChat({
    required this.idMensaje,
    required this.rolEmisor,
    this.contenido,
    this.urlAdjunto,
    this.tipoAdjunto,
    required this.fechaCreacion,
  });

  factory MensajeChat.fromJson(Map<String, dynamic> json) => MensajeChat(
        idMensaje: _parseInt(json['id_mensaje']),
        rolEmisor: json['rol_emisor'] as String? ?? '',
        contenido: json['contenido'] as String?,
        urlAdjunto: json['url_adjunto'] as String?,
        tipoAdjunto: json['tipo_adjunto'] as String?,
        fechaCreacion:
            DateTime.tryParse(json['fecha_creacion'] as String? ?? '') ??
                DateTime.now(),
      );

  bool get esCliente => rolEmisor.toUpperCase() == 'CLIENTE';
  bool get esTecnico => rolEmisor.toUpperCase() == 'TECNICO';
  bool get esIa => rolEmisor.toUpperCase() == 'IA';
  bool get tieneImagen =>
      urlAdjunto != null && tipoAdjunto?.toUpperCase() == 'IMAGEN';
}

// ── ConversacionChat ──────────────────────────────────────────────────────────

class ConversacionChat {
  final int idConversacion;
  final String tipo; // CLIENTE | TECNICO
  final List<MensajeChat> mensajes;

  const ConversacionChat({
    required this.idConversacion,
    required this.tipo,
    this.mensajes = const [],
  });

  factory ConversacionChat.fromJson(Map<String, dynamic> json) =>
      ConversacionChat(
        idConversacion: _parseInt(json['id_conversacion']),
        tipo: json['tipo'] as String? ?? '',
        mensajes: (json['mensajes'] as List<dynamic>?)
                ?.map((e) => MensajeChat.fromJson(e as Map<String, dynamic>))
                .toList() ??
            const [],
      );

  ConversacionChat copyWith({List<MensajeChat>? mensajes}) => ConversacionChat(
        idConversacion: idConversacion,
        tipo: tipo,
        mensajes: mensajes ?? this.mensajes,
      );
}
