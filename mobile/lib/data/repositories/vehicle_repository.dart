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

  Future<Vehicle> createVehicle({
    String? marca,
    String? modelo,
    int? anio,
    String? placa,
  }) async {
    try {
      final response = await _client.dio.post('/vehiculos', data: {
        if (marca != null && marca.isNotEmpty) 'marca': marca,
        if (modelo != null && modelo.isNotEmpty) 'modelo': modelo,
        if (anio != null) 'anio': anio,
        if (placa != null && placa.isNotEmpty) 'placa': placa,
      });
      return Vehicle.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      final detail =
          (e.response?.data as Map?)?['detail'] ?? 'Error al registrar vehículo';
      throw Exception(detail);
    }
  }

  Future<Vehicle> updateVehicle(
    int id, {
    String? marca,
    String? modelo,
    int? anio,
    String? placa,
  }) async {
    try {
      final response = await _client.dio.put('/vehiculos/$id', data: {
        if (marca != null && marca.isNotEmpty) 'marca': marca,
        if (modelo != null && modelo.isNotEmpty) 'modelo': modelo,
        if (anio != null) 'anio': anio,
        if (placa != null && placa.isNotEmpty) 'placa': placa,
      });
      return Vehicle.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      final detail =
          (e.response?.data as Map?)?['detail'] ?? 'Error al actualizar vehículo';
      throw Exception(detail);
    }
  }

  Future<void> deleteVehicle(int id) async {
    try {
      await _client.dio.delete('/vehiculos/$id');
    } on DioException catch (e) {
      final detail =
          (e.response?.data as Map?)?['detail'] ?? 'Error al eliminar vehículo';
      throw Exception(detail);
    }
  }
}
