import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/models/chat_models.dart';
import '../../data/repositories/chat_repository.dart';
import 'core_providers.dart';

final chatRepositoryProvider = Provider<ChatRepository>((ref) {
  return ChatRepository(ref.watch(apiClientProvider));
});

// ── Historial ─────────────────────────────────────────────────────────────────

final clienteChatProvider = FutureProvider.autoDispose
    .family<ConversacionChat, int>((ref, idIncidente) async {
  return ref.read(chatRepositoryProvider).getMensajesCliente(idIncidente);
});

final tecnicoChatProvider = FutureProvider.autoDispose
    .family<ConversacionChat, int>((ref, idIncidente) async {
  return ref.read(chatRepositoryProvider).getMensajesTecnico(idIncidente);
});

// ── Envío de mensajes ─────────────────────────────────────────────────────────

/// Notifier genérico de envío para un hilo de chat (cliente o técnico).
/// Mantiene el estado de "enviando" y, al recibir la respuesta del backend
/// (mensaje del usuario + respuesta de IA), invalida el provider de
/// historial correspondiente para reflejar los mensajes nuevos.
class ChatEnvioNotifier extends StateNotifier<AsyncValue<void>> {
  ChatEnvioNotifier(this._repo, this._ref, this._incidentId, this._esCliente)
      : super(const AsyncValue.data(null));

  final ChatRepository _repo;
  final Ref _ref;
  final int _incidentId;
  final bool _esCliente;

  Future<bool> enviar({String? contenido, String? adjuntoPath}) async {
    state = const AsyncValue.loading();
    try {
      if (_esCliente) {
        await _repo.enviarMensajeCliente(
          _incidentId,
          contenido: contenido,
          adjuntoPath: adjuntoPath,
        );
        _ref.invalidate(clienteChatProvider(_incidentId));
      } else {
        await _repo.enviarMensajeTecnico(_incidentId, contenido ?? '');
        _ref.invalidate(tecnicoChatProvider(_incidentId));
      }
      state = const AsyncValue.data(null);
      return true;
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      return false;
    }
  }

  void reset() => state = const AsyncValue.data(null);
}

final clienteChatEnvioProvider = StateNotifierProvider.autoDispose
    .family<ChatEnvioNotifier, AsyncValue<void>, int>((ref, idIncidente) {
  return ChatEnvioNotifier(
    ref.watch(chatRepositoryProvider),
    ref,
    idIncidente,
    true,
  );
});

final tecnicoChatEnvioProvider = StateNotifierProvider.autoDispose
    .family<ChatEnvioNotifier, AsyncValue<void>, int>((ref, idIncidente) {
  return ChatEnvioNotifier(
    ref.watch(chatRepositoryProvider),
    ref,
    idIncidente,
    false,
  );
});
