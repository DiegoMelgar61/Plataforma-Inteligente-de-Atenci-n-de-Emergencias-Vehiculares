import 'package:dio/dio.dart';
import '../../core/api_client.dart';
import '../models/informe_models.dart';

// ── Informe de servicio del incidente ────────────────────────────────────────

class InformeRepository {
  final ApiClient _client;
  InformeRepository(this._client);

  /// Devuelve el informe de servicio del incidente con su estado
  /// (GENERANDO / LISTO / FALLIDO), o null si la generación todavía no fue
  /// disparada (backend responde 404). La UI decide qué mostrar según el estado.
  Future<InformeServicio?> getInforme(int idIncidente) async {
    try {
      final response =
          await _client.dio.get('/informes/incidents/$idIncidente');
      return InformeServicio.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) return null;
      final detail = (e.response?.data as Map?)?['detail'] ??
          'Error al obtener el informe de servicio';
      throw Exception(detail);
    }
  }
}
