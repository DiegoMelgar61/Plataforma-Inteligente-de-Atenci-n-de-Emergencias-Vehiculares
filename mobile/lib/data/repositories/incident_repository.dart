import 'package:dio/dio.dart';
import '../../core/api_client.dart';
import '../models/incident_models.dart';

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

  Future<Incident> getIncidentById(int id) async {
    try {
      final response = await _client.dio.get('/incidents/$id');
      return Incident.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      final detail =
          (e.response?.data as Map?)?['detail'] ?? 'Error al cargar incidente';
      throw Exception(detail);
    }
  }

  Future<CotizacionDetalle?> getCotizacion(int idIncidente) async {
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
    int idIncidente, {
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
  Future<List<CotizacionOferta>> getCotizaciones(int idIncidente) async {
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
      int idIncidente, int idTaller) async {
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
  Future<CancelacionResultado> cancelarServicio(int idIncidente) async {
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
  Future<int> reportIncident({
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
      return (data['incidente_id'] as num?)?.toInt() ?? 0;
    } on DioException catch (e) {
      final detail = (e.response?.data as Map?)?['detail'] ??
          'Error al reportar incidente';
      throw Exception(detail);
    }
  }
}
