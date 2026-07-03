import 'package:dio/dio.dart';
import '../../core/api_client.dart';
import '../models/assignment_models.dart';

// ── Technician ────────────────────────────────────────────────────────────────

class TechnicianRepository {
  final ApiClient _client;
  TechnicianRepository(this._client);

  /// GET /tecnicos/mi-asignacion — asignación activa o null si está libre.
  Future<TechnicianAssignment?> getMiAsignacion() async {
    try {
      final response = await _client.dio.get('/tecnicos/mi-asignacion');
      if (response.data == null) return null;
      return TechnicianAssignment.fromJson(
          response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      final detail =
          (e.response?.data as Map?)?['detail'] ?? 'Error al cargar asignación';
      throw Exception(detail);
    }
  }

  /// PATCH /tecnicos/incidente/{id}/estado — transición de estado.
  /// Devuelve el incidente actualizado (como mapa JSON crudo).
  Future<Map<String, dynamic>> updateIncidentState(
      int idIncidente, String nuevoEstado) async {
    try {
      final response = await _client.dio.patch(
        '/tecnicos/incidente/$idIncidente/estado',
        data: {'nuevo_estado': nuevoEstado},
      );
      return response.data as Map<String, dynamic>;
    } on DioException catch (e) {
      final detail =
          (e.response?.data as Map?)?['detail'] ?? 'Error al actualizar estado';
      throw Exception(detail);
    }
  }
}
