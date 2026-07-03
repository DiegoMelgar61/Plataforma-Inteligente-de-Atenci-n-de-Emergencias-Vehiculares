import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:geolocator/geolocator.dart';
import '../../../core/extensions.dart';
import '../../../data/models/models.dart';
import '../../providers/providers.dart';
import '../../../core/constants.dart';
import '../../../shared/widgets.dart';

class MapScreen extends ConsumerStatefulWidget {
  const MapScreen({super.key});

  @override
  ConsumerState<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends ConsumerState<MapScreen> {
  Position? _currentPosition;
  bool _loadingLocation = false;
  String? _locationError;

  @override
  void initState() {
    super.initState();
    _loadLocation();
  }

  Future<void> _loadLocation() async {
    setState(() {
      _loadingLocation = true;
      _locationError = null;
    });
    try {
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        setState(() => _locationError =
            'El servicio de GPS no está activado. Por favor actívalo.');
        return;
      }
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
      }
      if (permission == LocationPermission.denied ||
          permission == LocationPermission.deniedForever) {
        setState(() =>
            _locationError = 'Permiso de ubicación denegado.');
        return;
      }
      final position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );
      setState(() => _currentPosition = position);
    } catch (e) {
      setState(() => _locationError = 'Error al obtener ubicación: $e');
    } finally {
      if (mounted) setState(() => _loadingLocation = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final incidentsAsync = ref.watch(myIncidentsProvider);
    final colorScheme = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Mi Ubicación'),
        centerTitle: false,
        actions: [
          IconButton(
            icon: const Icon(Icons.my_location),
            tooltip: 'Actualizar ubicación',
            onPressed: _loadingLocation ? null : _loadLocation,
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => _loadLocation(),
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Map placeholder card
            _MapPlaceholder(
              position: _currentPosition,
              isLoading: _loadingLocation,
              error: _locationError,
              onRefresh: _loadLocation,
            ),
            const SizedBox(height: 16),

            // Current location info
            if (_currentPosition != null) ...[
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.location_on,
                              color: colorScheme.error, size: 20),
                          const SizedBox(width: 8),
                          Text(
                            'Tu posición actual',
                            style: Theme.of(context)
                                .textTheme
                                .titleMedium
                                ?.copyWith(fontWeight: FontWeight.bold),
                          ),
                        ],
                      ),
                      const Divider(),
                      _CoordRow(
                          label: 'Latitud',
                          value: _currentPosition!.latitude
                              .toStringAsFixed(6)),
                      const SizedBox(height: 8),
                      _CoordRow(
                          label: 'Longitud',
                          value: _currentPosition!.longitude
                              .toStringAsFixed(6)),
                      const SizedBox(height: 8),
                      _CoordRow(
                          label: 'Altitud',
                          value:
                              '${_currentPosition!.altitude.toStringAsFixed(1)} m'),
                      const SizedBox(height: 8),
                      _CoordRow(
                          label: 'Precisión',
                          value:
                              '± ${_currentPosition!.accuracy.toStringAsFixed(0)} m'),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
            ],

            // Incidents with location
            Text(
              'Incidentes con ubicación',
              style: Theme.of(context)
                  .textTheme
                  .titleMedium
                  ?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 10),
            incidentsAsync.when(
              loading: () =>
                  const AppLoadingIndicator(message: 'Cargando...'),
              error: (error, _) => AppErrorCard(
                message: error.toString().withoutException,
                onRetry: () => ref.invalidate(myIncidentsProvider),
              ),
              data: (incidents) {
                final geoIncidents = incidents
                    .where((i) =>
                        i.latitud != null && i.longitud != null)
                    .toList();
                if (geoIncidents.isEmpty) {
                  return const EmptyStateWidget(
                    icon: Icons.location_off_outlined,
                    title: 'Sin incidentes con ubicación',
                    subtitle:
                        'Los incidentes reportados con GPS aparecerán aquí.',
                  );
                }
                return Column(
                  children: geoIncidents
                      .map((i) => _IncidentLocationCard(
                            incident: i,
                            myPosition: _currentPosition,
                            onTap: () => Navigator.pushNamed(
                              context,
                              AppConstants.routeIncidentDetail,
                              arguments: i.idIncidente,
                            ),
                          ))
                      .toList(),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}

class _MapPlaceholder extends StatelessWidget {
  final Position? position;
  final bool isLoading;
  final String? error;
  final VoidCallback onRefresh;

  const _MapPlaceholder({
    required this.position,
    required this.isLoading,
    required this.error,
    required this.onRefresh,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return Container(
      height: 220,
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: colorScheme.outlineVariant),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: Stack(
          children: [
            // Grid lines (simulating a map)
            CustomPaint(
              size: const Size(double.infinity, 220),
              painter: _GridPainter(color: colorScheme.outlineVariant),
            ),
            // Center content
            Center(
              child: isLoading
                  ? Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const CircularProgressIndicator(),
                        const SizedBox(height: 12),
                        Text('Obteniendo ubicación...',
                            style: TextStyle(
                                color: colorScheme.onSurfaceVariant)),
                      ],
                    )
                  : error != null
                      ? Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.location_off,
                                size: 48,
                                color: colorScheme.outlineVariant),
                            const SizedBox(height: 8),
                            Padding(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 24),
                              child: Text(
                                error!,
                                textAlign: TextAlign.center,
                                style: TextStyle(
                                    color: colorScheme.onSurfaceVariant,
                                    fontSize: 13),
                              ),
                            ),
                            const SizedBox(height: 12),
                            FilledButton.tonal(
                              onPressed: onRefresh,
                              child: const Text('Reintentar'),
                            ),
                          ],
                        )
                      : Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.location_on,
                                size: 52, color: colorScheme.error),
                            if (position != null)
                              Container(
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 12, vertical: 6),
                                decoration: BoxDecoration(
                                  color: colorScheme.surface.withOpacity(0.9),
                                  borderRadius: BorderRadius.circular(20),
                                ),
                                child: Text(
                                  '${position!.latitude.toStringAsFixed(4)}, '
                                  '${position!.longitude.toStringAsFixed(4)}',
                                  style: const TextStyle(
                                      fontWeight: FontWeight.w600,
                                      fontSize: 13),
                                ),
                              ),
                          ],
                        ),
            ),
          ],
        ),
      ),
    );
  }
}

class _GridPainter extends CustomPainter {
  final Color color;
  _GridPainter({required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color.withOpacity(0.4)
      ..strokeWidth = 1;
    for (double x = 0; x < size.width; x += 30) {
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), paint);
    }
    for (double y = 0; y < size.height; y += 30) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), paint);
    }
  }

  @override
  bool shouldRepaint(_GridPainter oldDelegate) => color != oldDelegate.color;
}

class _CoordRow extends StatelessWidget {
  final String label;
  final String value;
  const _CoordRow({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label,
            style: TextStyle(
                color: Theme.of(context).colorScheme.onSurfaceVariant)),
        Text(value, style: const TextStyle(fontWeight: FontWeight.w600)),
      ],
    );
  }
}

class _IncidentLocationCard extends StatelessWidget {
  final Incident incident;
  final Position? myPosition;
  final VoidCallback onTap;

  const _IncidentLocationCard({
    required this.incident,
    required this.myPosition,
    required this.onTap,
  });

  String _distance() {
    if (myPosition == null) return '';
    final dist = Geolocator.distanceBetween(
      myPosition!.latitude,
      myPosition!.longitude,
      incident.latitud!,
      incident.longitud!,
    );
    if (dist < 1000) return '${dist.toStringAsFixed(0)} m';
    return '${(dist / 1000).toStringAsFixed(1)} km';
  }

  @override
  Widget build(BuildContext context) {
    final distance = _distance();
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        onTap: onTap,
        leading: CircleAvatar(
          backgroundColor:
              Theme.of(context).colorScheme.errorContainer,
          child: Icon(Icons.car_crash,
              color: Theme.of(context).colorScheme.error, size: 20),
        ),
        title: Text(
            '${incident.clasificacionLabel} #${incident.idIncidente}',
            style: const TextStyle(fontWeight: FontWeight.w600)),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(incident.fechaCreacion?.relative ?? ''),
            Text(
              '${incident.latitud!.toStringAsFixed(4)}, '
              '${incident.longitud!.toStringAsFixed(4)}',
              style: const TextStyle(fontSize: 12),
            ),
          ],
        ),
        trailing: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            StatusChip(status: incident.estado),
            if (distance.isNotEmpty) ...[
              const SizedBox(height: 4),
              Text(distance, style: const TextStyle(fontSize: 12)),
            ],
          ],
        ),
        isThreeLine: true,
      ),
    );
  }
}
