import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';

import '../../../../core/extensions.dart';
import '../../../../data/models/models.dart';
import '../../providers/providers.dart';

class MakePaymentScreen extends ConsumerStatefulWidget {
  final Payment payment;

  const MakePaymentScreen({super.key, required this.payment});

  @override
  ConsumerState<MakePaymentScreen> createState() => _MakePaymentScreenState();
}

class _MakePaymentScreenState extends ConsumerState<MakePaymentScreen> {
  File? _comprobanteFile;
  final _notasController = TextEditingController();
  bool _isLoading = false;
  final _picker = ImagePicker();

  @override
  void dispose() {
    _notasController.dispose();
    super.dispose();
  }

  Future<void> _seleccionarImagen(ImageSource source) async {
    Navigator.pop(context); // cierra el bottom sheet
    try {
      final picked = await _picker.pickImage(
        source: source,
        imageQuality: 75, // compresión para mantener < 2MB
        maxWidth: 1920,
      );
      if (picked != null && mounted) {
        setState(() => _comprobanteFile = File(picked.path));
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error al seleccionar imagen: $e')),
        );
      }
    }
  }

  void _mostrarSelectorImagen() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 12),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 40,
                height: 4,
                margin: const EdgeInsets.only(bottom: 12),
                decoration: BoxDecoration(
                  color: Colors.grey.shade300,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              ListTile(
                leading: const Icon(Icons.camera_alt_outlined),
                title: const Text('Tomar foto'),
                onTap: () => _seleccionarImagen(ImageSource.camera),
              ),
              ListTile(
                leading: const Icon(Icons.photo_library_outlined),
                title: const Text('Elegir de galería'),
                onTap: () => _seleccionarImagen(ImageSource.gallery),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _marcarComoPagado() async {
    if (_comprobanteFile == null) return;
    setState(() => _isLoading = true);

    try {
      await ref.read(paymentsRepositoryProvider).marcarComoPagado(
            widget.payment.idPago,
            _comprobanteFile!,
            notas: _notasController.text.trim().isEmpty
                ? null
                : _notasController.text.trim(),
          );
      ref.invalidate(myPaymentsProvider);

      if (mounted) {
        Navigator.pop(context);
        showDialog(
          context: context,
          builder: (_) => AlertDialog(
            title: const Text('Pago realizado 🎉'),
            content: const Text(
              'Tu pago está pendiente de confirmación. '
              'Te avisaremos cuando el taller lo confirme.',
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Entendido'),
              ),
            ],
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(e.toString().withoutException),
            backgroundColor: Colors.red,
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final monto = widget.payment.monto;

    return Scaffold(
      appBar: AppBar(title: const Text('Realizar Pago')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // ── Card monto ──────────────────────────────────────────────────
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children: [
                    Text(
                      'Monto a pagar',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Bs. ${monto.toStringAsFixed(2)}',
                      style: Theme.of(context)
                          .textTheme
                          .displaySmall
                          ?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: colorScheme.primary,
                          ),
                    ),
                    if (widget.payment.comisionPlataforma != null) ...[
                      const SizedBox(height: 4),
                      Text(
                        'Incluye Bs. ${widget.payment.comisionPlataforma!.toStringAsFixed(2)} de comisión de plataforma',
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: colorScheme.onSurfaceVariant,
                            ),
                        textAlign: TextAlign.center,
                      ),
                    ],
                    const Divider(height: 24),
                    Text(
                      'Incidente #${widget.payment.idIncidente.substring(0, 8).toUpperCase()}',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            fontFamily: 'monospace',
                            color: colorScheme.onSurfaceVariant,
                          ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // ── Card QR ─────────────────────────────────────────────────────
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children: [
                    Text(
                      'Escanea para transferir',
                      style: Theme.of(context)
                          .textTheme
                          .titleMedium
                          ?.copyWith(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 16),
                    ClipRRect(
                      borderRadius: BorderRadius.circular(12),
                      child: Image.asset(
                        'lib/assets/qr_pago.jpeg',
                        height: 220,
                        fit: BoxFit.contain,
                        errorBuilder: (_, __, ___) => Container(
                          height: 220,
                          decoration: BoxDecoration(
                            color: colorScheme.surfaceVariant,
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(
                                color: colorScheme.outline.withOpacity(0.3)),
                          ),
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.qr_code,
                                  size: 80,
                                  color: colorScheme.onSurfaceVariant),
                              const SizedBox(height: 8),
                              Text(
                                'QR no disponible\n(agrega lib/assets/qr_pago.jpeg)',
                                textAlign: TextAlign.center,
                                style: TextStyle(
                                    color: colorScheme.onSurfaceVariant,
                                    fontSize: 12),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 12),
                    Text(
                      'Escanea el QR con tu app bancaria',
                      style: Theme.of(context)
                          .textTheme
                          .bodyMedium
                          ?.copyWith(color: colorScheme.onSurfaceVariant),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // ── Card instrucciones ───────────────────────────────────────────
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Instrucciones',
                      style: Theme.of(context)
                          .textTheme
                          .titleSmall
                          ?.copyWith(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 12),
                    ...[
                      'Escanea el código QR con tu app bancaria',
                      'Transfiere el monto exacto: Bs. ${monto.toStringAsFixed(2)}',
                      'Guarda la captura de pantalla del comprobante',
                      'Adjúntala aquí y pulsa "Marcar como pagado"',
                    ].asMap().entries.map(
                          (e) => Padding(
                            padding: const EdgeInsets.only(bottom: 8),
                            child: Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                CircleAvatar(
                                  radius: 11,
                                  backgroundColor: colorScheme.primaryContainer,
                                  child: Text(
                                    '${e.key + 1}',
                                    style: TextStyle(
                                      fontSize: 11,
                                      color: colorScheme.onPrimaryContainer,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 10),
                                Expanded(
                                  child: Text(e.value,
                                      style: Theme.of(context)
                                          .textTheme
                                          .bodyMedium),
                                ),
                              ],
                            ),
                          ),
                        ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // ── Sección comprobante ──────────────────────────────────────────
            if (_comprobanteFile == null)
              OutlinedButton.icon(
                onPressed: _mostrarSelectorImagen,
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  side: BorderSide(color: colorScheme.primary),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12)),
                ),
                icon: const Icon(Icons.add_a_photo_outlined, size: 22),
                label: const Text('Adjuntar comprobante',
                    style: TextStyle(fontSize: 16)),
              )
            else
              Card(
                child: Column(
                  children: [
                    Stack(
                      children: [
                        ClipRRect(
                          borderRadius: BorderRadius.circular(12),
                          child: Image.file(
                            _comprobanteFile!,
                            height: 200,
                            width: double.infinity,
                            fit: BoxFit.cover,
                          ),
                        ),
                        Positioned(
                          top: 8,
                          right: 8,
                          child: GestureDetector(
                            onTap: () =>
                                setState(() => _comprobanteFile = null),
                            child: Container(
                              decoration: const BoxDecoration(
                                color: Colors.black54,
                                shape: BoxShape.circle,
                              ),
                              padding: const EdgeInsets.all(4),
                              child: const Icon(Icons.close,
                                  color: Colors.white, size: 18),
                            ),
                          ),
                        ),
                      ],
                    ),
                    TextButton.icon(
                      onPressed: _mostrarSelectorImagen,
                      icon: const Icon(Icons.swap_horiz),
                      label: const Text('Cambiar comprobante'),
                    ),
                  ],
                ),
              ),
            const SizedBox(height: 16),

            // ── Notas opcionales ─────────────────────────────────────────────
            TextField(
              controller: _notasController,
              maxLines: 3,
              maxLength: 200,
              decoration: InputDecoration(
                labelText: 'Notas para el taller (opcional)',
                hintText: 'Ej: Transferencia enviada a las 14:30 desde Banco X',
                alignLabelWithHint: true,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
            const SizedBox(height: 24),

            // ── Botón enviar ─────────────────────────────────────────────────
            SizedBox(
              height: 52,
              child: ElevatedButton.icon(
                onPressed:
                    (_comprobanteFile != null && !_isLoading)
                        ? _marcarComoPagado
                        : null,
                style: ElevatedButton.styleFrom(
                  backgroundColor: colorScheme.primary,
                  foregroundColor: colorScheme.onPrimary,
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12)),
                ),
                icon: _isLoading
                    ? SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: colorScheme.onPrimary,
                        ),
                      )
                    : const Icon(Icons.check_circle_outline),
                label: Text(
                  _isLoading ? 'Enviando...' : 'Marcar como pagado',
                  style: const TextStyle(
                      fontSize: 16, fontWeight: FontWeight.bold),
                ),
              ),
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }
}
