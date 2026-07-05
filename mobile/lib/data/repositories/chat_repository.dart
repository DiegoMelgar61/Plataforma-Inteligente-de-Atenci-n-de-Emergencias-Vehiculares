import 'package:dio/dio.dart';
import '../../core/api_client.dart';
import '../models/chat_models.dart';

// ── Chat de incidente (cliente + copiloto técnico) ───────────────────────────

class ChatRepository {
  final ApiClient _client;
  ChatRepository(this._client);

  Future<ConversacionChat> getMensajesCliente(int idIncidente) async {
    try {
      final response =
          await _client.dio.get('/chat/incidents/$idIncidente/cliente/mensajes');
      return ConversacionChat.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      final detail = (e.response?.data as Map?)?['detail'] ??
          'Error al cargar el chat de emergencia';
      throw Exception(detail);
    }
  }

  /// Envía un mensaje del cliente. Al menos uno de [contenido] o [adjuntoPath]
  /// debe estar presente (lo valida también el backend).
  Future<(MensajeChat mensajeUsuario, MensajeChat mensajeIa)>
      enviarMensajeCliente(
    int idIncidente, {
    String? contenido,
    String? adjuntoPath,
  }) async {
    try {
      final fields = <String, dynamic>{
        if (contenido != null && contenido.trim().isNotEmpty)
          'contenido': contenido.trim(),
      };

      if (adjuntoPath != null) {
        final fileName = adjuntoPath.split('/').last.split('\\').last;
        fields['adjunto'] =
            await MultipartFile.fromFile(adjuntoPath, filename: fileName);
      }

      final formData = FormData.fromMap(fields);
      final response = await _client.dio.post(
        '/chat/incidents/$idIncidente/cliente/mensajes',
        data: formData,
        options: Options(contentType: 'multipart/form-data'),
      );
      final data = response.data as Map<String, dynamic>;
      return (
        MensajeChat.fromJson(data['mensaje_usuario'] as Map<String, dynamic>),
        MensajeChat.fromJson(data['mensaje_ia'] as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      final detail = (e.response?.data as Map?)?['detail'] ??
          'Error al enviar el mensaje';
      throw Exception(detail);
    }
  }

  Future<ConversacionChat> getMensajesTecnico(int idIncidente) async {
    try {
      final response =
          await _client.dio.get('/chat/incidents/$idIncidente/tecnico/mensajes');
      return ConversacionChat.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      final detail = (e.response?.data as Map?)?['detail'] ??
          'Error al cargar el copiloto IA';
      throw Exception(detail);
    }
  }

  Future<(MensajeChat mensajeUsuario, MensajeChat mensajeIa)>
      enviarMensajeTecnico(int idIncidente, String contenido) async {
    try {
      final response = await _client.dio.post(
        '/chat/incidents/$idIncidente/tecnico/mensajes',
        data: {'contenido': contenido.trim()},
      );
      final data = response.data as Map<String, dynamic>;
      return (
        MensajeChat.fromJson(data['mensaje_usuario'] as Map<String, dynamic>),
        MensajeChat.fromJson(data['mensaje_ia'] as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      final detail = (e.response?.data as Map?)?['detail'] ??
          'Error al enviar el mensaje';
      throw Exception(detail);
    }
  }
}
