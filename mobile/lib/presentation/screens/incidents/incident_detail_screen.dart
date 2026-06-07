import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:latlong2/latlong.dart';
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
  TechnicianLocation? _technicianLocation;

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
            final data = jsonDecode(message as String) as Map<String, dynamic>;
            setState(() {
              if (data['tipo'] == 'ubicacion_tecnico') {
                _technicianLocation = TechnicianLocation.fromJson(data);
              }
              _wsMessages.insert(0, data);
            });
          } catch (_) {
            setState(
                () => _wsMessages.insert(0, {'mensaje': message.toString()}));
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
            onPressed: () =>
                ref.invalidate(selectedIncidentProvider(widget.incidentId)),
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
              onRetry: () =>
                  ref.invalidate(selectedIncidentProvider(widget.incidentId)),
            ),
          ),
        ),
        data: (incident) => _buildContent(incident),
      ),
    );
  }

  Widget _buildContent(Incident incident) {
    final quotationAsync =
        ref.watch(incidentQuotationProvider(widget.incidentId));
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _StatusCard(incident: incident),
        _QuotationSection(
          quotationAsync: quotationAsync,
          responseState:
              ref.watch(quotationResponseProvider(widget.incidentId)),
          onRespond: _respondToQuotation,
        ),
        const SizedBox(height: 16),
        _InfoSection(incident: incident),
        if (incident.resumenIa != null &&
            incident.resumenIa!.trim().isNotEmpty) ...[
          const SizedBox(height: 16),
          _AiAnalysisSection(rawSummary: incident.resumenIa!),
        ],
        const SizedBox(height: 16),
        if (incident.evidencias.isNotEmpty) ...[
          _EvidenceSection(evidencias: incident.evidencias),
          const SizedBox(height: 16),
        ],
        _LiveMapSection(
          incident: incident,
          technicianLocation: _technicianLocation,
          isConnected: _wsConnected,
        ),
        const SizedBox(height: 16),
        _NotificationsSection(messages: _wsMessages),
        const SizedBox(height: 24),
      ],
    );
  }

  Future<void> _respondToQuotation(bool accepted) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(accepted ? 'Aceptar cotización' : 'Rechazar cotización'),
        content: Text(
          accepted
              ? '¿Confirmás que aceptás esta cotización? El técnico pasará a estar en camino.'
              : '¿Confirmás que rechazás esta cotización? El incidente volverá a clasificación para reasignación.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancelar'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: Text(accepted ? 'Aceptar' : 'Rechazar'),
          ),
        ],
      ),
    );

    if (confirmed != true) return;

    final notifier =
        ref.read(quotationResponseProvider(widget.incidentId).notifier);
    await notifier.respond(accepted: accepted);
    if (!mounted) return;

    final state = ref.read(quotationResponseProvider(widget.incidentId));
    final message = state.hasError
        ? state.error.toString().withoutException
        : accepted
            ? 'Cotización aceptada. El técnico va en camino.'
            : 'Cotización rechazada. Buscaremos otra asignación.';
    ScaffoldMessenger.of(context)
        .showSnackBar(SnackBar(content: Text(message)));
  }
}

class _QuotationSection extends StatelessWidget {
  final AsyncValue<CotizacionDetalle?> quotationAsync;
  final AsyncValue<void> responseState;
  final Future<void> Function(bool accepted) onRespond;

  const _QuotationSection({
    required this.quotationAsync,
    required this.responseState,
    required this.onRespond,
  });

  @override
  Widget build(BuildContext context) {
    return quotationAsync.when(
      loading: () => const SizedBox.shrink(),
      error: (error, _) => Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Text(error.toString().withoutException),
        ),
      ),
      data: (quotation) {
        if (quotation == null || !quotation.tieneMonto)
          return const SizedBox.shrink();
        final colorScheme = Theme.of(context).colorScheme;
        final accepted = quotation.cotizacionAceptada;
        final isSubmitting = responseState.isLoading;

        return Column(
          children: [
            const SizedBox(height: 16),
            Card(
              color: accepted == null
                  ? colorScheme.secondaryContainer
                  : colorScheme.surface,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.request_quote_outlined,
                            color: colorScheme.primary),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            'Cotización del taller',
                            style: Theme.of(context)
                                .textTheme
                                .titleMedium
                                ?.copyWith(fontWeight: FontWeight.bold),
                          ),
                        ),
                        _QuotationBadge(accepted: accepted),
                      ],
                    ),
                    const Divider(),
                    Text(
                      '\$${quotation.montoCotizado!.toStringAsFixed(2)}',
                      style:
                          Theme.of(context).textTheme.headlineSmall?.copyWith(
                                fontWeight: FontWeight.w800,
                                color: colorScheme.primary,
                              ),
                    ),
                    if (quotation.tiempoEstimadoReparacion != null) ...[
                      const SizedBox(height: 8),
                      _InfoRow(
                        icon: Icons.build_outlined,
                        label: 'Tiempo estimado de reparación',
                        value: '${quotation.tiempoEstimadoReparacion} min',
                      ),
                    ],
                    if (quotation.notasCotizacion != null &&
                        quotation.notasCotizacion!.trim().isNotEmpty) ...[
                      const SizedBox(height: 8),
                      _InfoRow(
                        icon: Icons.notes_outlined,
                        label: 'Notas del taller',
                        value: quotation.notasCotizacion!,
                      ),
                    ],
                    if (quotation.pendienteRespuesta) ...[
                      const SizedBox(height: 16),
                      Row(
                        children: [
                          Expanded(
                            child: OutlinedButton(
                              onPressed:
                                  isSubmitting ? null : () => onRespond(false),
                              child: const Text('Rechazar'),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: FilledButton(
                              onPressed:
                                  isSubmitting ? null : () => onRespond(true),
                              child: Text(
                                isSubmitting
                                    ? 'Enviando...'
                                    : 'Aceptar cotización',
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ],
                ),
              ),
            ),
          ],
        );
      },
    );
  }
}

class _QuotationBadge extends StatelessWidget {
  final bool? accepted;

  const _QuotationBadge({required this.accepted});

  @override
  Widget build(BuildContext context) {
    final label = accepted == null
        ? 'Pendiente'
        : accepted!
            ? 'Aceptada'
            : 'Rechazada';
    final color = accepted == null
        ? Colors.orange
        : accepted!
            ? Colors.green
            : Colors.red;
    return _LiveBadge(label: label, color: color);
  }
}

class _LiveMapSection extends StatelessWidget {
  final Incident incident;
  final TechnicianLocation? technicianLocation;
  final bool isConnected;

  const _LiveMapSection({
    required this.incident,
    required this.technicianLocation,
    required this.isConnected,
  });

  @override
  Widget build(BuildContext context) {
    final incidentLat = incident.latitud;
    final incidentLng = incident.longitud;
    final colorScheme = Theme.of(context).colorScheme;

    if (incidentLat == null || incidentLng == null) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Icon(Icons.map_outlined, color: colorScheme.onSurfaceVariant),
              const SizedBox(width: 12),
              const Expanded(
                  child: Text('Mapa no disponible para este incidente')),
            ],
          ),
        ),
      );
    }

    final incidentPoint = LatLng(incidentLat, incidentLng);
    final technicianPoint = technicianLocation == null
        ? null
        : LatLng(technicianLocation!.latitud, technicianLocation!.longitud);
    final center = technicianPoint ?? incidentPoint;

    return Card(
      clipBehavior: Clip.antiAlias,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Icon(Icons.map_outlined, color: colorScheme.primary),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Mapa en vivo',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                ),
                _LiveBadge(
                  label: technicianPoint == null
                      ? 'Esperando técnico'
                      : (isConnected ? 'Técnico en vivo' : 'Última ubicación'),
                  color: technicianPoint == null
                      ? Colors.orange
                      : (isConnected ? Colors.green : Colors.grey),
                ),
              ],
            ),
          ),
          SizedBox(
            height: 260,
            child: FlutterMap(
              options: MapOptions(
                initialCenter: center,
                initialZoom: technicianPoint == null ? 15 : 14,
              ),
              children: [
                TileLayer(
                  urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                  userAgentPackageName: 'com.plataforma.emergencias',
                ),
                if (technicianPoint != null)
                  PolylineLayer(
                    polylines: [
                      Polyline(
                        points: [technicianPoint, incidentPoint],
                        color: colorScheme.primary,
                        strokeWidth: 4,
                      ),
                    ],
                  ),
                MarkerLayer(
                  markers: [
                    Marker(
                      point: incidentPoint,
                      width: 48,
                      height: 48,
                      child: Icon(
                        Icons.location_on,
                        color: colorScheme.error,
                        size: 42,
                      ),
                    ),
                    if (technicianPoint != null)
                      Marker(
                        point: technicianPoint,
                        width: 54,
                        height: 54,
                        child: Container(
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: colorScheme.primary,
                            boxShadow: [
                              BoxShadow(
                                color: colorScheme.primary.withOpacity(0.35),
                                blurRadius: 12,
                                spreadRadius: 2,
                              ),
                            ],
                          ),
                          child: const Icon(Icons.engineering,
                              color: Colors.white),
                        ),
                      ),
                  ],
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _InfoRow(
                  icon: Icons.report_problem_outlined,
                  label: 'Incidente',
                  value:
                      '${incidentLat.toStringAsFixed(6)}, ${incidentLng.toStringAsFixed(6)}',
                ),
                if (technicianLocation != null)
                  _InfoRow(
                    icon: Icons.engineering_outlined,
                    label: 'Técnico',
                    value:
                        '${technicianLocation!.latitud.toStringAsFixed(6)}, ${technicianLocation!.longitud.toStringAsFixed(6)}',
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _LiveBadge extends StatelessWidget {
  final String label;
  final Color color;

  const _LiveBadge({required this.label, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: color.withOpacity(0.12),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        label,
        style: TextStyle(
          color: color,
          fontSize: 11,
          fontWeight: FontWeight.w700,
        ),
      ),
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
    final currentStep = _steps
        .indexOf(incident.estado.toUpperCase())
        .clamp(-1, _steps.length - 1);

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
                value: '${incident.latitud!.toStringAsFixed(6)}, '
                    '${incident.longitud!.toStringAsFixed(6)}',
              ),
            if (incident.tiempoEstimadoLlegadaMinutos != null)
              _InfoRow(
                icon: Icons.timer_outlined,
                label: 'Tiempo estimado de llegada',
                value: '${incident.tiempoEstimadoLlegadaMinutos} min',
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
              size: 18, color: Theme.of(context).colorScheme.onSurfaceVariant),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: Theme.of(context).textTheme.labelSmall?.copyWith(
                        color: Theme.of(context).colorScheme.onSurfaceVariant,
                      ),
                ),
                const SizedBox(height: 2),
                Text(value, style: Theme.of(context).textTheme.bodyMedium),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _AiAnalysisSection extends StatelessWidget {
  final String rawSummary;
  const _AiAnalysisSection({required this.rawSummary});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final resumen = _extractMainSummary(rawSummary);
    final danos = _extractLine(rawSummary, 'Danos visibles:') ??
        _extractLine(rawSummary, 'Danos visibles:');
    final recomendaciones = _extractLine(rawSummary, 'Recomendaciones:');
    final confianza = _extractLine(rawSummary, 'Confianza IA:');

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.smart_toy_outlined),
                const SizedBox(width: 8),
                Text(
                  'Analisis IA',
                  style: Theme.of(context)
                      .textTheme
                      .titleMedium
                      ?.copyWith(fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const Divider(),
            Text(resumen, style: Theme.of(context).textTheme.bodyMedium),
            if (danos != null && danos.isNotEmpty) ...[
              const SizedBox(height: 12),
              _AiSubBlock(title: 'Danos visibles', value: danos),
            ],
            if (recomendaciones != null && recomendaciones.isNotEmpty) ...[
              const SizedBox(height: 12),
              _AiSubBlock(title: 'Recomendaciones', value: recomendaciones),
            ],
            if (confianza != null && confianza.isNotEmpty) ...[
              const SizedBox(height: 12),
              Text(
                'Confianza IA: $confianza',
                style: Theme.of(context).textTheme.labelSmall?.copyWith(
                      color: colorScheme.onSurfaceVariant,
                    ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  static String _extractMainSummary(String raw) {
    return raw
        .split('\n')
        .map((x) => x.trim())
        .where((x) =>
            x.isNotEmpty &&
            !x.startsWith('Recomendaciones:') &&
            !x.startsWith('Danos visibles:') &&
            !x.startsWith('Confianza IA:'))
        .join(' ');
  }

  static String? _extractLine(String raw, String prefix) {
    final line = raw.split('\n').map((x) => x.trim()).firstWhere(
          (x) => x.startsWith(prefix),
          orElse: () => '',
        );
    if (line.isEmpty) return null;
    return line.replaceFirst(prefix, '').trim();
  }
}

class _AiSubBlock extends StatelessWidget {
  final String title;
  final String value;
  const _AiSubBlock({required this.title, required this.value});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(10),
        color: Theme.of(context).colorScheme.surfaceContainerHighest,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: Theme.of(context)
                .textTheme
                .labelSmall
                ?.copyWith(fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 6),
          Text(value, style: Theme.of(context).textTheme.bodySmall),
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
