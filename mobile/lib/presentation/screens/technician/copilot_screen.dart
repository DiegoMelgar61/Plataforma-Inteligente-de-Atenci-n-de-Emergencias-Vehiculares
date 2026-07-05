import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

import '../../../core/api_client.dart';
import '../../../core/config.dart';
import '../../../core/extensions.dart';
import '../../../data/models/models.dart';
import '../../../shared/widgets.dart';
import '../../providers/providers.dart';

/// Copiloto IA del técnico: hilo conectado al chat de emergencia del cliente,
/// con sugerencia inicial de herramientas/repuestos y avisos en vivo cuando
/// el cliente comparte información técnicamente relevante.
class CopilotScreen extends ConsumerStatefulWidget {
  final int incidentId;
  const CopilotScreen({super.key, required this.incidentId});

  @override
  ConsumerState<CopilotScreen> createState() => _CopilotScreenState();
}

class _CopilotScreenState extends ConsumerState<CopilotScreen> {
  final _textController = TextEditingController();
  WebSocketChannel? _channel;
  StreamSubscription<dynamic>? _subscription;

  @override
  void initState() {
    super.initState();
    _connectWebSocket();
  }

  Future<void> _connectWebSocket() async {
    final token = await ApiClient().getToken();
    if (token == null || !mounted) return;

    try {
      final wsUrl =
          '${AppConfig.wsBaseUrl}/notifications/ws/incidents/${widget.incidentId}?token=$token';
      _channel = WebSocketChannel.connect(Uri.parse(wsUrl));

      _subscription = _channel!.stream.listen(
        (message) {
          if (!mounted) return;
          try {
            final data = jsonDecode(message as String) as Map<String, dynamic>;
            if (data['tipo'] == 'chat_info_relevante') {
              ref.invalidate(tecnicoChatProvider(widget.incidentId));
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(
                    (data['mensaje'] as String?) ??
                        'Nueva información del cliente',
                  ),
                  backgroundColor: Theme.of(context).colorScheme.primary,
                ),
              );
            }
          } catch (_) {
            // Mensajes no reconocidos del canal se ignoran.
          }
        },
        cancelOnError: false,
      );
    } catch (_) {
      // Sin WS en vivo, el copiloto sigue funcionando por polling manual.
    }
  }

  @override
  void dispose() {
    _textController.dispose();
    _subscription?.cancel();
    _channel?.sink.close();
    super.dispose();
  }

  Future<void> _enviar() async {
    final texto = _textController.text.trim();
    if (texto.isEmpty) return;

    final ok = await ref
        .read(tecnicoChatEnvioProvider(widget.incidentId).notifier)
        .enviar(contenido: texto);

    if (ok && mounted) {
      _textController.clear();
    }
  }

  @override
  Widget build(BuildContext context) {
    final chatAsync = ref.watch(tecnicoChatProvider(widget.incidentId));
    final envioState = ref.watch(tecnicoChatEnvioProvider(widget.incidentId));

    ref.listen<AsyncValue<void>>(
      tecnicoChatEnvioProvider(widget.incidentId),
      (prev, next) {
        next.whenOrNull(
          error: (e, _) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text(e.toString().withoutException)),
            );
            ref
                .read(tecnicoChatEnvioProvider(widget.incidentId).notifier)
                .reset();
          },
        );
      },
    );

    return Scaffold(
      appBar: AppBar(
        title: const Text('Copiloto IA'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_outlined),
            onPressed: () =>
                ref.invalidate(tecnicoChatProvider(widget.incidentId)),
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: chatAsync.when(
              loading: () =>
                  const AppLoadingIndicator(message: 'Cargando copiloto...'),
              error: (error, _) => Center(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: AppErrorCard(
                    message: error.toString().withoutException,
                    onRetry: () =>
                        ref.invalidate(tecnicoChatProvider(widget.incidentId)),
                  ),
                ),
              ),
              data: (conversacion) => _buildMessages(conversacion),
            ),
          ),
          _buildInputRow(envioState.isLoading),
        ],
      ),
    );
  }

  Widget _buildMessages(ConversacionChat conversacion) {
    final mensajes = conversacion.mensajes;
    if (mensajes.isEmpty) {
      return const EmptyStateWidget(
        icon: Icons.build_circle_outlined,
        title: 'Sin mensajes todavía',
        subtitle: 'El copiloto va a sugerir herramientas y repuestos acá.',
      );
    }

    final primeraSugerencia = mensajes.first.esIa ? mensajes.first : null;
    final resto = primeraSugerencia == null ? mensajes : mensajes.sublist(1);

    return ListView.builder(
      reverse: true,
      padding: const EdgeInsets.all(12),
      itemCount: resto.length + (primeraSugerencia != null ? 1 : 0),
      itemBuilder: (context, index) {
        final ultimoIndex = resto.length + (primeraSugerencia != null ? 1 : 0) - 1;
        if (index == ultimoIndex && primeraSugerencia != null) {
          return _SuggestionCard(mensaje: primeraSugerencia);
        }
        final mensaje = resto[resto.length - 1 - index];
        return _CopilotMessageBubble(mensaje: mensaje);
      },
    );
  }

  Widget _buildInputRow(bool enviando) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
        child: Row(
          children: [
            Expanded(
              child: TextField(
                controller: _textController,
                minLines: 1,
                maxLines: 4,
                decoration: const InputDecoration(
                  hintText: 'Preguntale al copiloto...',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.all(Radius.circular(24)),
                  ),
                  contentPadding:
                      EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                ),
                textInputAction: TextInputAction.send,
                onSubmitted: (_) => enviando ? null : _enviar(),
              ),
            ),
            const SizedBox(width: 4),
            enviando
                ? const Padding(
                    padding: EdgeInsets.all(12),
                    child: SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    ),
                  )
                : IconButton(
                    icon: const Icon(Icons.send),
                    onPressed: _enviar,
                  ),
          ],
        ),
      ),
    );
  }
}

// ── Tarjeta de sugerencia inicial ─────────────────────────────────────────────

class _SuggestionCard extends StatelessWidget {
  final MensajeChat mensaje;
  const _SuggestionCard({required this.mensaje});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return Card(
      color: colorScheme.primaryContainer,
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.build_circle, color: colorScheme.onPrimaryContainer),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Sugerencia de herramientas y repuestos',
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: colorScheme.onPrimaryContainer,
                        ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Text(
              mensaje.contenido ?? '',
              style: TextStyle(color: colorScheme.onPrimaryContainer),
            ),
          ],
        ),
      ),
    );
  }
}

// ── Burbuja de mensaje ────────────────────────────────────────────────────────

class _CopilotMessageBubble extends StatelessWidget {
  final MensajeChat mensaje;
  const _CopilotMessageBubble({required this.mensaje});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final esTecnico = mensaje.esTecnico;

    final bgColor = esTecnico ? colorScheme.primary : colorScheme.surfaceContainerHighest;
    final fgColor = esTecnico ? colorScheme.onPrimary : colorScheme.onSurface;

    return Align(
      alignment: esTecnico ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 4),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.75,
        ),
        decoration: BoxDecoration(
          color: bgColor,
          borderRadius: BorderRadius.circular(16),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            if (!esTecnico)
              Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Text(
                  'Asistente IA',
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                    color: fgColor.withOpacity(0.7),
                  ),
                ),
              ),
            Text(
              mensaje.contenido ?? '',
              style: TextStyle(color: fgColor),
            ),
          ],
        ),
      ),
    );
  }
}
