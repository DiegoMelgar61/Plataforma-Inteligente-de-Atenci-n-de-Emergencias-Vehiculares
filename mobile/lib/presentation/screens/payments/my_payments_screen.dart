import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

import '../../../../core/api_client.dart';
import '../../../../core/config.dart';
import '../../../../core/constants.dart';
import '../../../../core/extensions.dart';
import '../../../../data/models/models.dart';
import '../../providers/providers.dart';
import '../../../../shared/widgets.dart';
import 'make_payment_screen.dart';

class MyPaymentsScreen extends ConsumerStatefulWidget {
  const MyPaymentsScreen({super.key});

  @override
  ConsumerState<MyPaymentsScreen> createState() => _MyPaymentsScreenState();
}

class _MyPaymentsScreenState extends ConsumerState<MyPaymentsScreen> {
  WebSocketChannel? _channel;
  StreamSubscription<dynamic>? _wsSub;

  @override
  void initState() {
    super.initState();
    _connectWebSocket();
  }

  Future<void> _connectWebSocket() async {
    final token = await ApiClient().getToken();
    if (token == null || !mounted) return;
    try {
      final wsUrl = '${AppConfig.wsBaseUrl}/notifications/ws?token=$token';
      _channel = WebSocketChannel.connect(Uri.parse(wsUrl));
      _wsSub = _channel!.stream.listen(
        (message) {
          if (!mounted) return;
          try {
            final data = jsonDecode(message as String) as Map<String, dynamic>;
            final tipo = data['tipo'] as String? ?? '';
            if (tipo == 'pago_confirmado') {
              ref.invalidate(myPaymentsProvider);
              _showSnackBar('¡Pago confirmado, muchas gracias!', success: true);
            } else if (tipo == 'pago_rechazado') {
              ref.invalidate(myPaymentsProvider);
              _showSnackBar('Pago rechazado, revisa el motivo', success: false);
            }
          } catch (_) {}
        },
        onError: (_) {},
        onDone: () {},
        cancelOnError: false,
      );
    } catch (_) {}
  }

  void _showSnackBar(String mensaje, {required bool success}) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(mensaje),
        backgroundColor: success ? Colors.green : Colors.red,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  @override
  void dispose() {
    _wsSub?.cancel();
    _channel?.sink.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final paymentsAsync = ref.watch(myPaymentsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Mis Pagos'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_outlined),
            tooltip: 'Actualizar',
            onPressed: () => ref.invalidate(myPaymentsProvider),
          ),
        ],
      ),
      body: paymentsAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => AppErrorCard(
          message: error.toString().withoutException,
          onRetry: () => ref.invalidate(myPaymentsProvider),
        ),
        data: (pagos) {
          if (pagos.isEmpty) {
            return const EmptyStateWidget(
              icon: Icons.receipt_long_outlined,
              title: 'No tienes pagos pendientes',
              subtitle:
                  'Cuando un técnico atienda tu incidente, el pago aparecerá aquí.',
            );
          }
          return RefreshIndicator(
            onRefresh: () async => ref.invalidate(myPaymentsProvider),
            child: ListView.separated(
              padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
              itemCount: pagos.length,
              separatorBuilder: (_, __) => const SizedBox(height: 10),
              itemBuilder: (context, i) =>
                  _PaymentCard(payment: pagos[i], onAction: () {
                ref.invalidate(myPaymentsProvider);
              }),
            ),
          );
        },
      ),
    );
  }
}

// ── Payment card ──────────────────────────────────────────────────────────────

class _PaymentCard extends StatelessWidget {
  final Payment payment;
  final VoidCallback onAction;

  const _PaymentCard({required this.payment, required this.onAction});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final estado = payment.estado;

    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                // Icono genérico de pago
                Container(
                  width: 44,
                  height: 44,
                  decoration: BoxDecoration(
                    color: colorScheme.primaryContainer,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    Icons.receipt_long,
                    color: colorScheme.onPrimaryContainer,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Incidente #${payment.idIncidente}',
                        style: Theme.of(context)
                            .textTheme
                            .titleSmall
                            ?.copyWith(fontWeight: FontWeight.bold),
                      ),
                      if (payment.fechaCreacion != null)
                        Text(
                          payment.fechaCreacion!.formatted,
                          style: Theme.of(context)
                              .textTheme
                              .bodySmall
                              ?.copyWith(color: colorScheme.onSurfaceVariant),
                        ),
                    ],
                  ),
                ),
                // Monto
                Text(
                  'Bs. ${payment.monto.toStringAsFixed(2)}',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: colorScheme.primary,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Badge de estado
            _EstadoBadge(estado: estado),
            const SizedBox(height: 12),

            // Motivo de rechazo (si aplica)
            if (estado == EstadoPago.rechazado &&
                payment.motivoRechazo != null) ...[
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: Colors.red.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.red.shade200),
                ),
                child: Row(
                  children: [
                    Icon(Icons.info_outline,
                        size: 14, color: Colors.red.shade700),
                    const SizedBox(width: 6),
                    Expanded(
                      child: Text(
                        payment.motivoRechazo!,
                        style: TextStyle(
                            fontSize: 12, color: Colors.red.shade700),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 10),
            ],

            // Botón de acción
            _ActionButton(payment: payment, onAction: onAction),
          ],
        ),
      ),
    );
  }
}

class _EstadoBadge extends StatelessWidget {
  final EstadoPago estado;
  const _EstadoBadge({required this.estado});

  @override
  Widget build(BuildContext context) {
    Color bg;
    Color fg;
    switch (estado) {
      case EstadoPago.noPago:
        bg = Colors.red.shade100;
        fg = Colors.red.shade800;
        break;
      case EstadoPago.pendiente:
        bg = Colors.amber.shade100;
        fg = Colors.amber.shade900;
        break;
      case EstadoPago.pagado:
        bg = Colors.green.shade100;
        fg = Colors.green.shade800;
        break;
      case EstadoPago.rechazado:
        bg = Colors.grey.shade200;
        fg = Colors.grey.shade800;
        break;
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        estado.label,
        style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: fg),
      ),
    );
  }
}

class _ActionButton extends StatelessWidget {
  final Payment payment;
  final VoidCallback onAction;
  const _ActionButton({required this.payment, required this.onAction});

  @override
  Widget build(BuildContext context) {
    final estado = payment.estado;

    if (estado == EstadoPago.noPago || estado == EstadoPago.rechazado) {
      return SizedBox(
        width: double.infinity,
        child: ElevatedButton.icon(
          onPressed: () async {
            await Navigator.pushNamed(
              context,
              AppConstants.routeMakePayment,
              arguments: payment,
            );
            onAction();
          },
          icon: const Icon(Icons.payment),
          label: const Text('Realizar pago'),
        ),
      );
    }

    if (estado == EstadoPago.pendiente) {
      return SizedBox(
        width: double.infinity,
        child: OutlinedButton.icon(
          onPressed: null,
          icon: const Icon(Icons.hourglass_empty_outlined),
          label: const Text('Esperando confirmación del taller'),
        ),
      );
    }

    // PAGADO
    return SizedBox(
      width: double.infinity,
      child: OutlinedButton.icon(
        onPressed: () => _mostrarDetalle(context),
        icon: const Icon(Icons.check_circle_outline),
        label: const Text('Ver detalle'),
      ),
    );
  }

  void _mostrarDetalle(BuildContext context) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Pago confirmado ✅'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Monto: Bs. ${payment.monto.toStringAsFixed(2)}'),
            if (payment.fechaConfirmacion != null)
              Text('Confirmado: ${payment.fechaConfirmacion!.formatted}'),
            if (payment.comisionPlataforma != null)
              Text(
                  'Comisión plataforma: Bs. ${payment.comisionPlataforma!.toStringAsFixed(2)}'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cerrar'),
          ),
        ],
      ),
    );
  }
}
