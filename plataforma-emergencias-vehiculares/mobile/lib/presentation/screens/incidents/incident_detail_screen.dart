import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../../../core/api_client.dart';
import '../../../core/config.dart';
import '../../../core/extensions.dart';
import '../../../data/models/models.dart';
import '../../providers/providers.dart';
import '../../../shared/widgets.dart';

class IncidentDetailScreen extends ConsumerStatefulWidget {
  final String incidentId; // UUID string
  const IncidentDetailScreen({super.key, required this.incidentId});

  @override
  ConsumerState<IncidentDetailScreen> createState() =>
      _IncidentDetailScreenState();
}

class _IncidentDetailScreenState extends ConsumerState<IncidentDetailScreen> {
  WebSocketChannel? _channel;
  StreamSubscription<dynamic>? _subscription;
  final List<Map<String, dynamic>> _wsMessages = [];
  bool _wsConnected = false;

  @override
  void initState() {
    super.initState();
    _connectWebSocket();
  }

  Future<void> _connectWebSocket() async {
    final token = await ApiClient().getToken();
    if (token == null || !mounted) return;

    try {
      // Backend WS endpoint: /notifications/ws/incidents/{id_incidente}
      final wsUrl =
          '${AppConfig.wsBaseUrl}/notifications/ws/incidents/${widget.incidentId}?token=$token';
      _channel = WebSocketChannel.connect(Uri.parse(wsUrl));

      if (mounted) setState(() => _wsConnected = true);

      _subscription = _channel!.stream.listen(
        (message) {
          if (!mounted) return;
          try {
            final data =
                jsonDecode(message as String) as Map<String, dynamic>;
            setState(() => _wsMessages.insert(0, data));
          } catch (_) {
            setState(() =>
                _wsMessages.insert(0, {'mensaje': message.toString()}));
          }
        },
        onError: (_) {
          if (mounted) setState(() => _wsConnected = false);
        },
        onDone: () {
          if (mounted) setState(() => _wsConnected = false);
        },
        cancelOnError: false,
      );
    } catch (_) {
      if (mounted) setState(() => _wsConnected = false);
    }
  }

  @override
  void dispose() {
    _subscription?.cancel();
    _channel?.sink.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final incidentAsync =
        ref.watch(selectedIncidentProvider(widget.incidentId));

    return Scaffold(
      appBar: AppBar(
        title: Text('Incidente #${widget.incidentId.substring(0, 8)}…'),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  _wsConnected ? Icons.wifi : Icons.wifi_off,
                  color: _wsConnected ? Colors.green : Colors.grey,
                  size: 16,
                ),
                const SizedBox(width: 4),
                Text(
                  _wsConnected ? 'En vivo' : 'Sin conexión',
                  style: TextStyle(
                    fontSize: 11,
                    color: _wsConnected ? Colors.green : Colors.grey,
                  ),
                ),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.refresh_outlined),
            onPressed: () => ref
                .invalidate(selectedIncidentProvider(widget.incidentId)),
          ),
        ],
      ),
      body: incidentAsync.when(
        loading: () =>
            const AppLoadingIndicator(message: 'Cargando incidente...'),
        error: (error, _) => Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: AppErrorCard(
              message: error.toString().withoutException,
              onRetry: () => ref
                  .invalidate(selectedIncidentProvider(widget.incidentId)),
            ),
          ),
        ),
        data: (incident) => _buildContent(incident),
      ),
    );
  }

  Widget _buildContent(Incident incident) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _StatusCard(incident: incident),
        const SizedBox(height: 16),
        _InfoSection(incident: incident),
        const SizedBox(height: 16),
        if (incident.evidencias.isNotEmpty) ...[
          _EvidenceSection(evidencias: incident.evidencias),
          const SizedBox(height: 16),
        ],
        _NotificationsSection(messages: _wsMessages),
        const SizedBox(height: 24),
      ],
    );
  }
}

// ── Status card with timeline ─────────────────────────────────────────────────

class _StatusCard extends StatelessWidget {
  final Incident incident;
  const _StatusCard({required this.incident});

  static const _steps = [
    'PENDIENTE',
    'ASIGNADO',
    'EN_CAMINO',
    'EN_PROCESO',
    'ATENDIDO',
  ];

  static const _stepLabels = [
    'Recibido',
    'Asignado',
    'En camino',
    'En proceso',
    'Atendido',
  ];

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final currentStep =
        _steps.indexOf(incident.estado.toUpperCase()).clamp(-1, _steps.length - 1);

    return Card(
      color: colorScheme.primaryContainer,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    incident.clasificacionLabel,
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: colorScheme.onPrimaryContainer,
                        ),
                  ),
                ),
                StatusChip(status: incident.estado),
              ],
            ),
            if (incident.resumenIa != null) ...[
              const SizedBox(height: 8),
              Text(
                incident.resumenIa!,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: colorScheme.onPrimaryContainer.withOpacity(0.8),
                    ),
              ),
            ],
            const SizedBox(height: 16),
            // Timeline
            Row(
              children: _steps.asMap().entries.map((entry) {
                final i = entry.key;
                final isCompleted = currentStep >= i;
                final isLast = i == _steps.length - 1;
                final color = isCompleted
                    ? colorScheme.primary
                    : colorScheme.outlineVariant;

                return Expanded(
                  child: Row(
                    children: [
                      Column(
                        children: [
                          CircleAvatar(
                            radius: 10,
                            backgroundColor: color,
                            child: isCompleted
                                ? const Icon(Icons.check,
                                    size: 12, color: Colors.white)
                                : null,
                          ),
                          const SizedBox(height: 4),
                          Text(
                            _stepLabels[i],
                            style: TextStyle(fontSize: 9, color: color),
                            textAlign: TextAlign.center,
                          ),
                        ],
                      ),
                      if (!isLast)
                        Expanded(
                          child: Divider(
                            color: (currentStep > i)
                                ? colorScheme.primary
                                : colorScheme.outlineVariant,
                            thickness: 2,
                          ),
                        ),
                    ],
                  ),
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }
}

// ── Info section ──────────────────────────────────────────────────────────────

class _InfoSection extends StatelessWidget {
  final Incident incident;
  const _InfoSection({required this.incident});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Detalles',
              style: Theme.of(context)
                  .textTheme
                  .titleMedium
                  ?.copyWith(fontWeight: FontWeight.bold),
            ),
            const Divider(),
            _InfoRow(
              icon: Icons.category_outlined,
              label: 'Clasificación',
              value: incident.clasificacionLabel,
            ),
            _InfoRow(
              icon: Icons.flag_outlined,
              label: 'Prioridad',
              value: incident.prioridadLabel,
            ),
            if (incident.fechaCreacion != null)
              _InfoRow(
                icon: Icons.access_time,
                label: 'Fecha de reporte',
                value: incident.fechaCreacion!.formatted,
              ),
            if (incident.latitud != null && incident.longitud != null)
              _InfoRow(
                icon: Icons.location_on_outlined,
                label: 'Ubicación',
                value:
                    '${incident.latitud!.toStringAsFixed(6)}, '
                    '${incident.longitud!.toStringAsFixed(6)}',
              ),
            if (incident.tiempoEstimadoLlegadaMinutos != null)
              _InfoRow(
                icon: Icons.timer_outlined,
                label: 'Tiempo estimado de llegada',
                value:
                    '${incident.tiempoEstimadoLlegadaMinutos} min',
              ),
            if (incident.textoDescripcion != null)
              _InfoRow(
                icon: Icons.description_outlined,
                label: 'Descripción',
                value: incident.textoDescripcion!,
              ),
          ],
        ),
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _InfoRow({
    required this.icon,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon,
              size: 18,
              color: Theme.of(context).colorScheme.onSurfaceVariant),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: Theme.of(context).textTheme.labelSmall?.copyWith(
                        color:
                            Theme.of(context).colorScheme.onSurfaceVariant,
                      ),
                ),
                const SizedBox(height: 2),
                Text(value,
                    style: Theme.of(context).textTheme.bodyMedium),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// ── Evidence section ──────────────────────────────────────────────────────────

class _EvidenceSection extends StatelessWidget {
  final List<Evidence> evidencias;
  const _EvidenceSection({required this.evidencias});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Evidencias (${evidencias.length})',
              style: Theme.of(context)
                  .textTheme
                  .titleMedium
                  ?.copyWith(fontWeight: FontWeight.bold),
            ),
            const Divider(),
            ...evidencias.map(
              (e) => ListTile(
                contentPadding: EdgeInsets.zero,
                leading: CircleAvatar(
                  child: Icon(
                    e.isImage
                        ? Icons.image_outlined
                        : e.tipo.toUpperCase() == 'AUDIO'
                            ? Icons.audiotrack_outlined
                            : Icons.text_snippet_outlined,
                  ),
                ),
                title: Text(
                  e.urlArchivo.split('/').last,
                  overflow: TextOverflow.ellipsis,
                ),
                subtitle: Text(
                  e.fechaCreacion?.formatted ?? e.tipo,
                ),
                trailing: const Icon(Icons.open_in_new),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ── WebSocket notifications section ──────────────────────────────────────────

class _NotificationsSection extends StatelessWidget {
  final List<Map<String, dynamic>> messages;
  const _NotificationsSection({required this.messages});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.notifications_active_outlined,
                    color: colorScheme.primary, size: 20),
                const SizedBox(width: 8),
                Text(
                  'Actualizaciones en tiempo real',
                  style: Theme.of(context)
                      .textTheme
                      .titleMedium
                      ?.copyWith(fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const Divider(),
            if (messages.isEmpty)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 16),
                child: Center(
                  child: Text(
                    'Esperando actualizaciones...',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: colorScheme.onSurfaceVariant),
                  ),
                ),
              )
            else
              ...messages.map(
                (msg) {
                  final tipo = msg['tipo'] as String? ?? '';
                  final nuevoEstado = msg['nuevo_estado'] as String?;
                  final mensaje = msg['mensaje'] as String?;
                  return ListTile(
                    contentPadding: EdgeInsets.zero,
                    leading: CircleAvatar(
                      radius: 16,
                      backgroundColor: tipo == 'estado_actualizado'
                          ? colorScheme.primaryContainer
                          : colorScheme.surfaceContainerHighest,
                      child: Icon(
                        tipo == 'estado_actualizado'
                            ? Icons.update
                            : Icons.notifications,
                        size: 16,
                        color: colorScheme.primary,
                      ),
                    ),
                    title: Text(
                      nuevoEstado != null
                          ? 'Estado → $nuevoEstado'
                          : (mensaje ?? tipo),
                      style: const TextStyle(fontWeight: FontWeight.w600),
                    ),
                    subtitle: msg['timestamp'] != null
                        ? Text(
                            msg['timestamp'] as String,
                            style: const TextStyle(fontSize: 11),
                          )
                        : null,
                    dense: true,
                  );
                },
              ),
          ],
        ),
      ),
    );
  }
}
