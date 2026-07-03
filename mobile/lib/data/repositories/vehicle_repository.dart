import 'package:dio/dio.dart';
import '../../core/api_client.dart';
import '../models/vehicle_models.dart';

// ── Vehicles ──────────────────────────────────────────────────────────────────

class VehicleRepository {
  final ApiClient _client;
  VehicleRepository(this._client);

  Future<List<Vehicle>> getVehicles() async {
    try {
      final response = await _client.dio.get('/vehiculos');
      final data = response.data as List<dynamic>;
      return data
          .map((e) => Vehicle.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      final detail =
          (e.response?.data as Map?)?['detail'] ?? 'Error al cargar vehículos';
      throw Exception(detail);
    }
  }
}
