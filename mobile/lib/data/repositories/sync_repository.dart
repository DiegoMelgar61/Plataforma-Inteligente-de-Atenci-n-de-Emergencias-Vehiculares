import 'package:dio/dio.dart';
import '../../core/api_client.dart';
import '../local/offline_storage.dart';

// ── Offline sync ──────────────────────────────────────────────────────────────

class OfflineSyncRepository {
  final ApiClient _client;
  OfflineSyncRepository(this._client);

  Future<Map<String, dynamic>> sincronizarPendientes() async {
    final pendientes = await OfflineStorage.obtenerPendientes();
    if (pendientes.isEmpty) {
      return {'sincronizados': 0, 'omitidos': 0, 'errores': []};
    }

    final payload = pendientes
        .map(
          (e) => {
            'id_local': e.id_local,
            'texto_descripcion': e.descripcion,
            'latitud': e.latitud,
            'longitud': e.longitud,
            'id_vehiculo': e.id_vehiculo,
          },
        )
        .toList();

    try {
      final response = await _client.dio.post(
        '/incidents/sync',
        data: payload,
      );
      final result = response.data as Map<String, dynamic>;
      final errores = result['errores'];
      final idsConError = <String>{};

      if (errores is List) {
        for (final error in errores) {
          if (error is Map<String, dynamic>) {
            final idLocal = error['id_local'] as String?;
            if (idLocal != null) {
              idsConError.add(idLocal);
              await OfflineStorage.marcarError(
                idLocal,
                error['error'] as String? ?? 'Error al sincronizar',
              );
            }
          }
        }
      }

      for (final emergencia in pendientes) {
        if (!idsConError.contains(emergencia.id_local)) {
          await OfflineStorage.marcarSincronizada(emergencia.id_local);
        }
      }

      return result;
    } on DioException catch (e) {
      final detail = (e.response?.data as Map?)?['detail'] ??
          'No se pudo sincronizar. Verifica tu conexión.';
      throw Exception(detail);
    } catch (e) {
      throw Exception('No se pudo sincronizar: $e');
    }
  }
}
