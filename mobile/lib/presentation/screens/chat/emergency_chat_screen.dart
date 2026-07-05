import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';

import '../../../core/config.dart';
import '../../../core/extensions.dart';
import '../../../data/models/models.dart';
import '../../../shared/widgets.dart';
import '../../providers/providers.dart';

/// Chat de emergencia del cliente: asistente de IA que acompaña mientras el
/// técnico está en camino / atendiendo el incidente.
class EmergencyChatScreen extends ConsumerStatefulWidget {
  final int incidentId;
  const EmergencyChatScreen({super.key, required this.incidentId});

  @override
  ConsumerState<EmergencyChatScreen> createState() =>
      _EmergencyChatScreenState();
}

class _EmergencyChatScreenState extends ConsumerState<EmergencyChatScreen> {
  final _textController = TextEditingController();
  String? _pendingImagePath;

  @override
  void dispose() {
    _textController.dispose();
    super.dispose();
  }

  Future<void> _pickImage(ImageSource source) async {
    final picker = ImagePicker();
    final photo = await picker.pickImage(source: source, imageQuality: 80);
    if (photo != null && mounted) {
      setState(() => _pendingImagePath = photo.path);
    }
  }

  void _showAttachOptions() {
    showModalBottomSheet(
      context: context,
      builder: (ctx) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.camera_alt_outlined),
              title: const Text('Tomar foto'),
              onTap: () {
                Navigator.pop(ctx);
                _pickImage(ImageSource.camera);
              },
            ),
            ListTile(
              leading: const Icon(Icons.photo_library_outlined),
              title: const Text('Elegir de la galería'),
              onTap: () {
                Navigator.pop(ctx);
                _pickImage(ImageSource.gallery);
              },
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _enviar() async {
    final texto = _textController.text.trim();
    final imagen = _pendingImagePath;
    if (texto.isEmpty && imagen == null) return;

    final ok = await ref
        .read(clienteChatEnvioProvider(widget.incidentId).notifier)
        .enviar(contenido: texto.isEmpty ? null : texto, adjuntoPath: imagen);

    if (ok && mounted) {
      _textController.clear();
      setState(() => _pendingImagePath = null);
    }
  }

  @override
  Widget build(BuildContext context) {
    final chatAsync = ref.watch(clienteChatProvider(widget.incidentId));
    final envioState = ref.watch(clienteChatEnvioProvider(widget.incidentId));

    ref.listen<AsyncValue<void>>(
      clienteChatEnvioProvider(widget.incidentId),
      (prev, next) {
        next.whenOrNull(
          error: (e, _) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text(e.toString().withoutException)),
            );
            ref
                .read(clienteChatEnvioProvider(widget.incidentId).notifier)
                .reset();
          },
        );
      },
    );

    return Scaffold(
      appBar: AppBar(title: const Text('Chat de emergencia')),
      body: Column(
        children: [
          Expanded(
            child: chatAsync.when(
              loading: () =>
                  const AppLoadingIndicator(message: 'Cargando chat...'),
              error: (error, _) => Center(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: AppErrorCard(
                    message: error.toString().withoutException,
                    onRetry: () =>
                        ref.invalidate(clienteChatProvider(widget.incidentId)),
                  ),
                ),
              ),
              data: (conversacion) => _buildMessages(conversacion),
            ),
          ),
          if (_pendingImagePath != null) _buildImagePreview(),
          _buildInputRow(envioState.isLoading),
        ],
      ),
    );
  }

  Widget _buildMessages(ConversacionChat conversacion) {
    final mensajes = conversacion.mensajes;
    return ListView.builder(
      reverse: true,
      padding: const EdgeInsets.all(12),
      itemCount: mensajes.length + 1,
      itemBuilder: (context, index) {
        // El último item (índice más alto, visualmente arriba de todo por
        // reverse:true) es el disclaimer inicial.
        if (index == mensajes.length) {
          return _buildDisclaimer();
        }
        final mensaje = mensajes[mensajes.length - 1 - index];
        return _MessageBubble(mensaje: mensaje);
      },
    );
  }

  Widget _buildDisclaimer() {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 16),
      child: Card(
        color: Colors.blue.shade50,
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(Icons.info_outline, color: Colors.blue.shade700, size: 20),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  'Este es un asistente de IA que te va a orientar mientras el '
                  'técnico llega. No reemplaza la atención profesional en el lugar.',
                  style: TextStyle(color: Colors.blue.shade900, fontSize: 13),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildImagePreview() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      alignment: Alignment.centerLeft,
      child: Stack(
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: Image.file(
              File(_pendingImagePath!),
              width: 72,
              height: 72,
              fit: BoxFit.cover,
            ),
          ),
          Positioned(
            top: -8,
            right: -8,
            child: IconButton(
              icon: const Icon(Icons.cancel, size: 20),
              onPressed: () => setState(() => _pendingImagePath = null),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInputRow(bool enviando) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
        child: Row(
          children: [
            IconButton(
              icon: const Icon(Icons.image_outlined),
              onPressed: enviando ? null : _showAttachOptions,
            ),
            Expanded(
              child: TextField(
                controller: _textController,
                minLines: 1,
                maxLines: 4,
                decoration: const InputDecoration(
                  hintText: 'Escribí tu mensaje...',
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

// ── Burbuja de mensaje ────────────────────────────────────────────────────────

class _MessageBubble extends StatelessWidget {
  final MensajeChat mensaje;
  const _MessageBubble({required this.mensaje});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final esCliente = mensaje.esCliente;

    final bgColor = esCliente ? colorScheme.primary : colorScheme.surfaceContainerHighest;
    final fgColor = esCliente ? colorScheme.onPrimary : colorScheme.onSurface;

    return Align(
      alignment: esCliente ? Alignment.centerRight : Alignment.centerLeft,
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
            if (!esCliente)
              Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Text(
                  mensaje.esIa ? 'Asistente IA' : 'Técnico',
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                    color: fgColor.withOpacity(0.7),
                  ),
                ),
              ),
            if (mensaje.tieneImagen) ...[
              ClipRRect(
                borderRadius: BorderRadius.circular(10),
                child: Image.network(
                  '${AppConfig.baseUrl}${mensaje.urlAdjunto}',
                  width: 200,
                  fit: BoxFit.cover,
                  errorBuilder: (_, __, ___) => Container(
                    width: 200,
                    height: 120,
                    color: colorScheme.surfaceContainerHighest,
                    child: const Icon(Icons.broken_image_outlined),
                  ),
                ),
              ),
              if (mensaje.contenido != null && mensaje.contenido!.isNotEmpty)
                const SizedBox(height: 6),
            ],
            if (mensaje.contenido != null && mensaje.contenido!.isNotEmpty)
              Text(
                mensaje.contenido!,
                style: TextStyle(color: fgColor),
              ),
          ],
        ),
      ),
    );
  }
}
