import 'dart:io';

import 'package:dio/dio.dart';
import '../../core/api_client.dart';
import '../local/offline_storage.dart';
import '../models/models.dart';

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

// ── Incidents ─────────────────────────────────────────────────────────────────

class IncidentRepository {
  final ApiClient _client;
  IncidentRepository(this._client);

  Future<List<Incident>> getMyIncidents() async {
    try {
      final response = await _client.dio.get('/incidents/my');
      final data = response.data as List<dynamic>;
      return data
          .map((e) => Incident.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      final detail =
          (e.response?.data as Map?)?['detail'] ?? 'Error al cargar incidentes';
      throw Exception(detail);
    }
  }

  Future<Incident> getIncidentById(String id) async {
    try {
      final response = await _client.dio.get('/incidents/$id');
      return Incident.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      final detail =
          (e.response?.data as Map?)?['detail'] ?? 'Error al cargar incidente';
      throw Exception(detail);
    }
  }

  Future<CotizacionDetalle?> getCotizacion(String idIncidente) async {
    try {
      final response = await _client.dio.get(
        '/assignments/incidents/$idIncidente/cotizacion',
      );
      return CotizacionDetalle.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) return null;
      final detail =
          (e.response?.data as Map?)?['detail'] ?? 'Error al cargar cotización';
      throw Exception(detail);
    }
  }

  Future<CotizacionDetalle> responderCotizacion(
    String idIncidente, {
    required bool aceptada,
    String? motivoRechazo,
  }) async {
    try {
      final response = await _client.dio.post(
        '/assignments/incidents/$idIncidente/cotizacion/respuesta',
        data: {
          'aceptada': aceptada,
          if (motivoRechazo != null && motivoRechazo.trim().isNotEmpty)
            'motivo_rechazo': motivoRechazo.trim(),
        },
      );
      return CotizacionDetalle.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      final detail = (e.response?.data as Map?)?['detail'] ??
          'Error al responder cotización';
      throw Exception(detail);
    }
  }

  /// GET /incidents/{id}/cotizaciones — ofertas de talleres cercanos (InDrive).
  Future<List<CotizacionOferta>> getCotizaciones(String idIncidente) async {
    try {
      final response =
          await _client.dio.get('/incidents/$idIncidente/cotizaciones');
      final data = response.data as List<dynamic>;
      return data
          .map((e) => CotizacionOferta.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      final detail =
          (e.response?.data as Map?)?['detail'] ?? 'Error al cargar ofertas';
      throw Exception(detail);
    }
  }

  /// POST /incidents/{id}/seleccionar-taller — el cliente elige un taller.
  /// El incidente pasa a EN_CAMINO. Devuelve el incidente actualizado.
  Future<Incident> seleccionarTaller(
      String idIncidente, String idTaller) async {
    try {
      final response = await _client.dio.post(
        '/incidents/$idIncidente/seleccionar-taller',
        data: {'id_taller': idTaller},
      );
      return Incident.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      final detail =
          (e.response?.data as Map?)?['detail'] ?? 'Error al elegir taller';
      throw Exception(detail);
    }
  }

  /// POST /incidents/{id}/cancelar — el cliente cancela el servicio.
  Future<CancelacionResultado> cancelarServicio(String idIncidente) async {
    try {
      final response =
          await _client.dio.post('/incidents/$idIncidente/cancelar');
      return CancelacionResultado.fromJson(
          response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      final detail =
          (e.response?.data as Map?)?['detail'] ?? 'Error al cancelar servicio';
      throw Exception(detail);
    }
  }

  /// POST /incidents/report — multipart/form-data.
  /// Returns the new [idIncidente] (UUID string).
  Future<String> reportIncident({
    required double latitud,
    required double longitud,
    String? idVehiculo,
    String? textoDescripcion,
    String prioridad = 'MEDIA',
    String clasificacion = 'OTROS',
    List<String> imagenesPath = const [],
  }) async {
    try {
      final fields = <String, dynamic>{
        'latitud': latitud.toString(),
        'longitud': longitud.toString(),
        'prioridad': prioridad,
        'clasificacion': clasificacion,
        if (idVehiculo != null && idVehiculo.isNotEmpty)
          'id_vehiculo': idVehiculo,
        if (textoDescripcion != null && textoDescripcion.isNotEmpty)
          'texto_descripcion': textoDescripcion,
      };

      if (imagenesPath.isNotEmpty) {
        final files = <MultipartFile>[];
        for (final path in imagenesPath) {
          final fileName = path.split('/').last.split('\\').last;
          files.add(await MultipartFile.fromFile(path, filename: fileName));
        }
        fields['imagenes'] = files;
      }

      final formData = FormData.fromMap(fields);
      final response = await _client.dio.post(
        '/incidents/report',
        data: formData,
        options: Options(contentType: 'multipart/form-data'),
      );
      final data = response.data as Map<String, dynamic>;
      return data['incidente_id'] as String? ?? '';
    } on DioException catch (e) {
      final detail = (e.response?.data as Map?)?['detail'] ??
          'Error al reportar incidente';
      throw Exception(detail);
    }
  }
}

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
      String idIncidente, String nuevoEstado) async {
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

// ── Payments ──────────────────────────────────────────────────────────────────

class PaymentsRepository {
  final ApiClient _client;
  PaymentsRepository(this._client);

  Future<List<Payment>> listarMisPagos() async {
    try {
      final response = await _client.dio.get('/payments/my');
      final data = response.data as List<dynamic>;
      return data
          .map((e) => Payment.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      final detail =
          (e.response?.data as Map?)?['detail'] ?? 'Error al cargar pagos';
      throw Exception(detail);
    }
  }

  Future<Payment> marcarComoPagado(
    String idPago,
    File comprobante, {
    String? notas,
  }) async {
    try {
      final fileName = comprobante.path.split('/').last.split('\\').last;
      final formData = FormData.fromMap({
        'comprobante': await MultipartFile.fromFile(
          comprobante.path,
          filename: fileName,
        ),
        if (notas != null && notas.isNotEmpty) 'notas_cliente': notas,
      });
      final response = await _client.dio.post(
        '/payments/$idPago/mark-paid',
        data: formData,
        options: Options(contentType: 'multipart/form-data'),
      );
      return Payment.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      final detail =
          (e.response?.data as Map?)?['detail'] ?? 'Error al registrar pago';
      throw Exception(detail);
    }
  }
}

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
