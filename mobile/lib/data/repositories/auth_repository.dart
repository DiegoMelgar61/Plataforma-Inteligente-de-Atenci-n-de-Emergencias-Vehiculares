import 'package:dio/dio.dart';
import '../../core/api_client.dart';
import '../models/auth_models.dart';

// ── Auth ──────────────────────────────────────────────────────────────────────

class AuthRepository {
  final ApiClient _client;
  AuthRepository(this._client);

  Future<AuthResponse> login(String email, String password) async {
    try {
      final response = await _client.dio.post(
        '/auth/login',
        data: {'correo_electronico': email, 'contrasena': password},
      );
      final authResponse =
          AuthResponse.fromJson(response.data as Map<String, dynamic>);
      await _client.saveToken(authResponse.accessToken);
      return authResponse;
    } on DioException catch (e) {
      final detail =
          (e.response?.data as Map?)?['detail'] ?? 'Error al iniciar sesión';
      throw Exception(detail);
    }
  }

  Future<void> register({
    required String email,
    required String password,
    required String fullName,
    String? phone,
    String rol = 'CLIENTE',
  }) async {
    try {
      await _client.dio.post('/auth/register', data: {
        'correo_electronico': email,
        'contrasena': password,
        'nombre_completo': fullName,
        if (phone != null && phone.isNotEmpty) 'telefono': phone,
        'rol': rol,
      });
    } on DioException catch (e) {
      final detail =
          (e.response?.data as Map?)?['detail'] ?? 'Error al registrar';
      throw Exception(detail);
    }
  }

  /// GET /usuarios/me — profile of the authenticated user.
  Future<User?> getCurrentUser() async {
    try {
      final response = await _client.dio.get('/usuarios/me');
      return User.fromJson(response.data as Map<String, dynamic>);
    } catch (_) {
      return null;
    }
  }

  Future<bool> hasToken() async {
    final token = await _client.getToken();
    return token != null && token.isNotEmpty;
  }

  Future<void> logout() => _client.clearToken();
}
