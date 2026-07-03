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
  final int idUsuario;
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
        idUsuario: (json['id_usuario'] as num?)?.toInt() ?? 0,
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
