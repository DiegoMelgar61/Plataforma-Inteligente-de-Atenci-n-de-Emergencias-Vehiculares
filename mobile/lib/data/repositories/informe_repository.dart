import 'package:dio/dio.dart';
import '../../core/api_client.dart';
import '../models/informe_models.dart';

// ── Informe de servicio del incidente ────────────────────────────────────────

class InformeRepository {
  final ApiClient _client;
  InformeRepository(this._client);

  /// Devuelve el informe de servicio del incidente, o null si todavía no está
  /// disponible: 404 (generación no disparada) o registro presente pero sin
  /// PDF listo (estados GENERANDO / FALLIDO del backend).
  Future<InformeServicio?> getInforme(int idIncidente) async {
    try {
      final response =
          await _client.dio.get('/informes/incidents/$idIncidente');
      final informe =
          InformeServicio.fromJson(response.data as Map<String, dynamic>);
      if (informe.urlArchivo.isEmpty) return null;
      return informe;
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) return null;
      final detail = (e.response?.data as Map?)?['detail'] ??
          'Error al obtener el informe de servicio';
      throw Exception(detail);
    }
  }
}
