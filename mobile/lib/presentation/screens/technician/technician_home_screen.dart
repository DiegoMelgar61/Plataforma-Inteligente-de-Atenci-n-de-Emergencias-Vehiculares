import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:geolocator/geolocator.dart';
import 'package:latlong2/latlong.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../../core/constants.dart';
import '../../../data/models/models.dart';
import '../../../shared/widgets.dart';
import '../../providers/providers.dart';

/// Pantalla principal del técnico autenticado.
/// Muestra la orden activa con mapa (enlace externo), datos del cliente y
/// botones de acción secuencial según la máquina de estados.
class TechnicianHomeScreen extends ConsumerWidget {
  const TechnicianHomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);
    final asignacionAsync = ref.watch(miAsignacionProvider);
    final nombre =
        authState.currentUser?.nombreCompleto.split(' ').first ?? 'Técnico';

    // Si el cliente eligió este taller, la orden llega ya en EN_CAMINO: arrancar
    // el tracking GPS automáticamente (sin que el técnico toque nada).
    ref.listen(miAsignacionProvider, (prev, next) {
      next.whenData((asignacion) {
        if (asignacion == null) return;
        final estado = asignacion.estadoIncidente.toUpperCase();
        if (estado != 'EN_CAMINO' && estado != 'EN_PROCESO') return;
        final tracking = ref.read(technicianTrackingProvider);
        final yaActivo =
            tracking.isTracking && tracking.incidentId == asignacion.idIncidente;
        if (!yaActivo && !tracking.isConnecting) {
          ref
              .read(technicianTrackingProvider.notifier)
              .start(asignacion.idIncidente);
        }
      });
    });

    // Aviso push cuando el cliente cancela el servicio en camino.
    ref.listen(technicianTrackingProvider, (prev, next) {
      final aviso = next.avisoCancelacion;
      if (aviso == null) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(aviso),
          backgroundColor: Theme.of(context).colorScheme.error,
          duration: const Duration(seconds: 5),
        ),
      );
      ref.read(technicianTrackingProvider.notifier).limpiarAviso();
      ref.invalidate(miAsignacionProvider); // queda libre
    });

    return Scaffold(
      appBar: AppBar(
        title: const Text('Mi Orden'),
        centerTitle: false,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_outlined),
            tooltip: 'Actualizar',
            onPressed: () => ref.invalidate(miAsignacionProvider),
          ),
          IconButton(
            icon: const Icon(Icons.logout_outlined),
            tooltip: 'Cerrar sesión',
            onPressed: () => _logout(context, ref),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async => ref.invalidate(miAsignacionProvider),
        child: asignacionAsync.when(
          loading: () => const Center(child: AppLoadingIndicator()),
          error: (error, _) => ListView(
            children: [
              const SizedBox(height: 40),
              AppErrorCard(
                message: error.toString().replaceAll('Exception: ', ''),
                onRetry: () => ref.invalidate(miAsignacionProvider),
              ),
            ],
          ),
          data: (asignacion) => asignacion == null
              ? _LibreView(nombre: nombre)
              : _OrdenActivaView(asignacion: asignacion),
        ),
      ),
    );
  }

  void _logout(BuildContext context, WidgetRef ref) async {
    await ref.read(authProvider.notifier).logout();
    if (context.mounted) {
      Navigator.pushReplacementNamed(context, AppConstants.routeLogin);
    }
  }
}

// ── Estado LIBRE ──────────────────────────────────────────────────────────────

class _LibreView extends StatelessWidget {
  final String nombre;
  const _LibreView({required this.nombre});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return ListView(
      padding: const EdgeInsets.all(24),
      children: [
        // Tarjeta de bienvenida
        Card(
          color: colorScheme.primaryContainer,
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              children: [
                CircleAvatar(
                  radius: 36,
                  backgroundColor: colorScheme.primary,
                  child: Icon(Icons.engineering,
                      size: 40, color: colorScheme.onPrimary),
                ),
                const SizedBox(height: 16),
                Text(
                  '¡Hola, $nombre!',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: colorScheme.onPrimaryContainer,
                      ),
                ),
                const SizedBox(height: 8),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.green.shade100,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.circle, size: 10, color: Colors.green.shade700),
                      const SizedBox(width: 6),
                      Text(
                        'DISPONIBLE',
                        style: TextStyle(
                          color: Colors.green.shade700,
                          fontWeight: FontWeight.bold,
                          fontSize: 13,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 32),
        const EmptyStateWidget(
          icon: Icons.check_circle_outline,
          title: 'Sin órdenes activas',
          subtitle:
              'Estás libre. Cuando se te asigne un incidente aparecerá aquí automáticamente.',
        ),
      ],
    );
  }
}

class _TrackingCard extends ConsumerWidget {
  final TechnicianAssignment asignacion;
  const _TrackingCard({required this.asignacion});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final tracking = ref.watch(technicianTrackingProvider);
    final colorScheme = Theme.of(context).colorScheme;
    final isCurrentIncident = tracking.incidentId == asignacion.idIncidente;
    final isActive = tracking.isTracking && isCurrentIncident;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const _SeccionTitulo(
              icon: Icons.gps_fixed,
              titulo: 'Tracking GPS del servicio',
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Icon(
                  isActive ? Icons.location_searching : Icons.location_disabled,
                  color: isActive ? Colors.green : colorScheme.onSurfaceVariant,
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    isActive
                        ? 'Enviando ubicación al cliente en tiempo real.'
                        : 'Inicia el tracking cuando salgas hacia el incidente.',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                ),
              ],
            ),
            if (tracking.lastLocation != null && isCurrentIncident) ...[
              const SizedBox(height: 8),
              Text(
                'Última ubicación: ${tracking.lastLocation!.latitud.toStringAsFixed(6)}, ${tracking.lastLocation!.longitud.toStringAsFixed(6)}',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: colorScheme.onSurfaceVariant,
                    ),
              ),
            ],
            if (tracking.errorMessage != null) ...[
              const SizedBox(height: 8),
              Text(
                tracking.errorMessage!,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: colorScheme.error,
                    ),
              ),
            ],
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: isActive
                  ? OutlinedButton.icon(
                      icon: const Icon(Icons.stop_circle_outlined),
                      label: const Text('Detener tracking'),
                      onPressed: () => ref
                          .read(technicianTrackingProvider.notifier)
                          .stop(),
                    )
                  : FilledButton.icon(
                      icon: tracking.isConnecting
                          ? const SizedBox(
                              width: 18,
                              height: 18,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.play_arrow),
                      label: Text(tracking.isConnecting
                          ? 'Iniciando...'
                          : 'Iniciar tracking GPS'),
                      onPressed: tracking.isConnecting
                          ? null
                          : () => ref
                              .read(technicianTrackingProvider.notifier)
                              .start(asignacion.idIncidente),
                    ),
            ),
          ],
        ),
      ),
    );
  }
}

// ── Orden activa ──────────────────────────────────────────────────────────────

class _OrdenActivaView extends ConsumerWidget {
  final TechnicianAssignment asignacion;
  const _OrdenActivaView({required this.asignacion});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final updateAsync = ref.watch(technicianStateUpdateProvider);
    final colorScheme = Theme.of(context).colorScheme;

    // Mostrar snackbar en error de actualización
    ref.listen<AsyncValue<void>>(technicianStateUpdateProvider, (_, next) {
      next.whenOrNull(
        error: (e, _) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(e.toString().replaceAll('Exception: ', '')),
              backgroundColor: colorScheme.error,
            ),
          );
          ref.read(technicianStateUpdateProvider.notifier).reset();
        },
        data: (_) {
          // Recargar asignación tras actualización exitosa
          ref.invalidate(miAsignacionProvider);
        },
      );
    });

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // ── Estado actual ────────────────────────────────────────────────────
        _EstadoBadge(estado: asignacion.estadoIncidente),
        const SizedBox(height: 16),

        // ── Datos del incidente ──────────────────────────────────────────────
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _SeccionTitulo(
                    icon: Icons.car_crash, titulo: 'Detalles del incidente'),
                const SizedBox(height: 12),
                _InfoFila(
                    label: 'Tipo',
                    valor: _clasificacionLabel(asignacion.clasificacion)),
                _InfoFila(
                    label: 'Prioridad',
                    valor: _prioridadLabel(asignacion.prioridad),
                    color: _prioridadColor(asignacion.prioridad)),
                if (asignacion.resumenIa != null &&
                    asignacion.resumenIa!.isNotEmpty) ...[
                  const SizedBox(height: 8),
                  Text('Resumen IA',
                      style: Theme.of(context)
                          .textTheme
                          .labelSmall
                          ?.copyWith(color: colorScheme.onSurfaceVariant)),
                  const SizedBox(height: 4),
                  Text(asignacion.resumenIa!,
                      style: Theme.of(context).textTheme.bodyMedium),
                ],
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),

        // ── Datos del cliente ────────────────────────────────────────────────
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _SeccionTitulo(icon: Icons.person, titulo: 'Cliente'),
                const SizedBox(height: 12),
                _InfoFila(
                    label: 'Nombre',
                    valor: asignacion.clienteNombre ?? 'Sin datos'),
                if (asignacion.clienteTelefono != null)
                  _InfoFila(
                      label: 'Teléfono', valor: asignacion.clienteTelefono!),
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),

        // ── Ubicación del incidente ──────────────────────────────────────────
        _UbicacionCard(asignacion: asignacion),
        const SizedBox(height: 12),

        // ── Evidencias del incidente ─────────────────────────────────────────
        _EvidenciasTecnico(incidentId: asignacion.idIncidente),

        // ── Copiloto IA ───────────────────────────────────────────────────────
        _CopilotEntry(incidentId: asignacion.idIncidente),
        const SizedBox(height: 24),

        // ── Tracking GPS ─────────────────────────────────────────────────────
        if (asignacion.estadoIncidente.toUpperCase() != 'ATENDIDO') ...[
          _TrackingCard(asignacion: asignacion),
          const SizedBox(height: 24),
        ],

        // ── Botón de acción ──────────────────────────────────────────────────
        if (asignacion.tieneAccionDisponible)
          _BotonAccion(
            asignacion: asignacion,
            isLoading: updateAsync.isLoading,
            onPressed: updateAsync.isLoading
                ? null
                : () => _ejecutarTransicion(context, ref, asignacion),
          )
        else
          _IncidenteFinalizadoCard(),
      ],
    );
  }

  Future<void> _ejecutarTransicion(
    BuildContext context,
    WidgetRef ref,
    TechnicianAssignment asignacion,
  ) async {
    final siguiente = asignacion.siguienteEstado!;
    final confirmar = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: Text(asignacion.accionLabel ?? 'Confirmar'),
        content: Text(
            '¿Confirmas cambiar el estado a "${_estadoLabel(siguiente)}"?'),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('Cancelar')),
          FilledButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text('Confirmar')),
        ],
      ),
    );
    if (confirmar != true) return;

    await ref
        .read(technicianStateUpdateProvider.notifier)
        .updateState(asignacion.idIncidente, siguiente);

    if (siguiente == 'EN_CAMINO') {
      await ref
          .read(technicianTrackingProvider.notifier)
          .start(asignacion.idIncidente);
    } else if (siguiente == 'ATENDIDO') {
      await ref.read(technicianTrackingProvider.notifier).stop();
    }
  }

  String _clasificacionLabel(String c) {
    switch (c.toUpperCase()) {
      case 'BATERIA':
        return 'Batería';
      case 'LLANTA':
        return 'Llanta';
      case 'CHOQUE':
        return 'Choque';
      case 'MOTOR':
        return 'Motor';
      case 'OTROS':
        return 'Otros';
      default:
        return c;
    }
  }

  String _prioridadLabel(String p) {
    switch (p.toUpperCase()) {
      case 'ALTA':
        return 'Alta ⚠️';
      case 'MEDIA':
        return 'Media';
      case 'BAJA':
        return 'Baja';
      default:
        return p;
    }
  }

  Color _prioridadColor(String p) {
    switch (p.toUpperCase()) {
      case 'ALTA':
        return Colors.red;
      case 'MEDIA':
        return Colors.orange;
      default:
        return Colors.green;
    }
  }

  String _estadoLabel(String s) {
    switch (s.toUpperCase()) {
      case 'EN_CAMINO':
        return 'En camino';
      case 'EN_PROCESO':
        return 'En proceso';
      case 'ATENDIDO':
        return 'Atendido';
      default:
        return s;
    }
  }
}

// ── Sub-widgets ───────────────────────────────────────────────────────────────

class _EstadoBadge extends StatelessWidget {
  final String estado;
  const _EstadoBadge({required this.estado});

  @override
  Widget build(BuildContext context) {
    final (label, color) = _estadoInfo(estado);
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.12),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color, width: 1.5),
      ),
      child: Row(
        children: [
          Icon(_estadoIcon(estado), color: color, size: 22),
          const SizedBox(width: 10),
          Text(
            label,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: color,
                  fontWeight: FontWeight.bold,
                ),
          ),
        ],
      ),
    );
  }

  (String, Color) _estadoInfo(String estado) {
    switch (estado.toUpperCase()) {
      case 'ASIGNADO':
        return ('Nuevo trabajo asignado', Colors.blue);
      case 'EN_CAMINO':
        return ('En camino al sitio', Colors.orange);
      case 'EN_PROCESO':
        return ('Trabajando en el sitio', Colors.purple);
      case 'ATENDIDO':
        return ('Trabajo finalizado', Colors.green);
      default:
        return (estado, Colors.grey);
    }
  }

  IconData _estadoIcon(String estado) {
    switch (estado.toUpperCase()) {
      case 'ASIGNADO':
        return Icons.assignment_outlined;
      case 'EN_CAMINO':
        return Icons.directions_car_outlined;
      case 'EN_PROCESO':
        return Icons.build_outlined;
      case 'ATENDIDO':
        return Icons.check_circle_outline;
      default:
        return Icons.info_outline;
    }
  }
}

class _UbicacionCard extends StatelessWidget {
  final TechnicianAssignment asignacion;
  const _UbicacionCard({required this.asignacion});

  @override
  Widget build(BuildContext context) {
    final lat = asignacion.latitud;
    final lng = asignacion.longitud;
    final colorScheme = Theme.of(context).colorScheme;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _SeccionTitulo(icon: Icons.location_on, titulo: 'Ubicación del incidente'),
            const SizedBox(height: 12),
            if (lat != null && lng != null) ...[
              Row(
                children: [
                  Icon(Icons.gps_fixed_outlined,
                      size: 16, color: colorScheme.onSurfaceVariant),
                  const SizedBox(width: 6),
                  Text(
                    'Lat: ${lat.toStringAsFixed(6)},  Lng: ${lng.toStringAsFixed(6)}',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                ],
              ),
              const SizedBox(height: 12),
              // Mapa interactivo con la ruta por calles hasta el incidente.
              _RutaIncidenteMapa(destinoLat: lat, destinoLng: lng),
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  icon: const Icon(Icons.open_in_new, size: 18),
                  label: const Text('Abrir navegación en Google Maps'),
                  onPressed: () => _abrirMapa(context, lat, lng),
                ),
              ),
            ] else
              Text(
                'Ubicación no disponible',
                style: Theme.of(context)
                    .textTheme
                    .bodyMedium
                    ?.copyWith(color: colorScheme.onSurfaceVariant),
              ),
          ],
        ),
      ),
    );
  }

  Future<void> _abrirMapa(BuildContext context, double lat, double lng) async {
    // Modo navegación (direcciones por calles desde la ubicación actual).
    final uri = Uri.parse(
      'https://www.google.com/maps/dir/?api=1&destination=$lat,$lng&travelmode=driving',
    );
    final messenger = ScaffoldMessenger.of(context);
    try {
      final abierto = await launchUrl(uri, mode: LaunchMode.externalApplication);
      if (!abierto && context.mounted) {
        messenger.showSnackBar(
          SnackBar(content: Text('No se pudo abrir el mapa. Coordenadas: $lat, $lng')),
        );
      }
    } catch (_) {
      if (context.mounted) {
        messenger.showSnackBar(
          SnackBar(content: Text('No se pudo abrir el mapa. Coordenadas: $lat, $lng')),
        );
      }
    }
  }
}

/// Mapa interactivo con la ruta por calles desde la ubicación del técnico hasta
/// el incidente. La ruta se traza con OSRM (sigue las calles); si falla, cae a
/// una línea recta. El marcador del técnico se actualiza en vivo con el tracking.
class _RutaIncidenteMapa extends ConsumerStatefulWidget {
  final double destinoLat;
  final double destinoLng;
  const _RutaIncidenteMapa({required this.destinoLat, required this.destinoLng});

  @override
  ConsumerState<_RutaIncidenteMapa> createState() => _RutaIncidenteMapaState();
}

class _RutaIncidenteMapaState extends ConsumerState<_RutaIncidenteMapa> {
  final MapController _mapController = MapController();
  List<LatLng> _ruta = [];
  LatLng? _origen;
  bool _cargando = true;

  LatLng get _destino => LatLng(widget.destinoLat, widget.destinoLng);

  @override
  void initState() {
    super.initState();
    _cargarRuta();
  }

  Future<void> _cargarRuta() async {
    // Preferir la última ubicación del tracking activo; si no, GPS del dispositivo.
    LatLng? origen;
    final tracking = ref.read(technicianTrackingProvider);
    if (tracking.lastLocation != null) {
      origen = LatLng(
          tracking.lastLocation!.latitud, tracking.lastLocation!.longitud);
    } else {
      origen = await _ubicacionDispositivo();
    }

    final ruta = origen != null
        ? await _rutaPorCalles(origen, _destino)
        : <LatLng>[];

    if (!mounted) return;
    setState(() {
      _origen = origen;
      _ruta = ruta;
      _cargando = false;
    });

    final puntos = ruta.isNotEmpty
        ? ruta
        : [if (origen != null) origen, _destino];
    if (puntos.length >= 2) {
      try {
        _mapController.fitCamera(
          CameraFit.coordinates(
            coordinates: puntos,
            padding: const EdgeInsets.all(40),
          ),
        );
      } catch (_) {}
    }
  }

  Future<LatLng?> _ubicacionDispositivo() async {
    try {
      if (!await Geolocator.isLocationServiceEnabled()) return null;
      var permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
      }
      if (permission == LocationPermission.denied ||
          permission == LocationPermission.deniedForever) {
        return null;
      }
      final pos = await Geolocator.getCurrentPosition();
      return LatLng(pos.latitude, pos.longitude);
    } catch (_) {
      return null;
    }
  }

  Future<List<LatLng>> _rutaPorCalles(LatLng o, LatLng d) async {
    try {
      final url = 'https://router.project-osrm.org/route/v1/driving/'
          '${o.longitude},${o.latitude};${d.longitude},${d.latitude}'
          '?overview=full&geometries=geojson';
      final resp = await Dio().get(
        url,
        options: Options(receiveTimeout: const Duration(seconds: 15)),
      );
      final coords =
          (resp.data['routes'][0]['geometry']['coordinates'] as List);
      final puntos = coords
          .map((c) =>
              LatLng((c[1] as num).toDouble(), (c[0] as num).toDouble()))
          .toList();
      if (puntos.isNotEmpty) return puntos;
    } catch (_) {}
    return [o, d]; // Fallback: línea recta si OSRM no responde.
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final tracking = ref.watch(technicianTrackingProvider);
    final tecnicoLive = tracking.lastLocation != null
        ? LatLng(tracking.lastLocation!.latitud, tracking.lastLocation!.longitud)
        : _origen;

    return ClipRRect(
      borderRadius: BorderRadius.circular(8),
      child: SizedBox(
        height: 220,
        child: Stack(
          children: [
            FlutterMap(
              mapController: _mapController,
              options: MapOptions(
                initialCenter: _destino,
                initialZoom: 14,
              ),
              children: [
                TileLayer(
                  urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                  userAgentPackageName: 'com.plataforma.emergencias',
                ),
                if (_ruta.length >= 2)
                  PolylineLayer(
                    polylines: [
                      Polyline(
                        points: _ruta,
                        color: colorScheme.primary,
                        strokeWidth: 5,
                      ),
                    ],
                  ),
                MarkerLayer(
                  markers: [
                    Marker(
                      point: _destino,
                      width: 40,
                      height: 40,
                      child: Icon(Icons.location_pin,
                          size: 40, color: colorScheme.error),
                    ),
                    if (tecnicoLive != null)
                      Marker(
                        point: tecnicoLive,
                        width: 36,
                        height: 36,
                        child: Icon(Icons.navigation,
                            size: 30, color: colorScheme.primary),
                      ),
                  ],
                ),
              ],
            ),
            if (_cargando)
              const Positioned(
                top: 8,
                right: 8,
                child: SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _CopilotEntry extends StatelessWidget {
  final int incidentId;
  const _CopilotEntry({required this.incidentId});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return Card(
      color: colorScheme.secondaryContainer,
      child: ListTile(
        leading:
            Icon(Icons.build_circle, color: colorScheme.onSecondaryContainer),
        title: Text(
          'Copiloto IA',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: colorScheme.onSecondaryContainer,
          ),
        ),
        subtitle: Text(
          'Sugerencias de herramientas y repuestos para este trabajo',
          style: TextStyle(color: colorScheme.onSecondaryContainer),
        ),
        trailing: Icon(Icons.arrow_forward_ios,
            size: 16, color: colorScheme.onSecondaryContainer),
        onTap: () => Navigator.pushNamed(
          context,
          AppConstants.routeTechnicianCopilot,
          arguments: incidentId,
        ),
      ),
    );
  }
}

/// Muestra las evidencias del incidente al técnico. Obtiene el incidente
/// completo (con evidencias) vía el endpoint de detalle, permitido para el
/// técnico asignado del mismo tenant.
class _EvidenciasTecnico extends ConsumerWidget {
  final int incidentId;
  const _EvidenciasTecnico({required this.incidentId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final incidenteAsync = ref.watch(selectedIncidentProvider(incidentId));
    return incidenteAsync.maybeWhen(
      data: (incidente) {
        if (incidente.evidencias.isEmpty) return const SizedBox.shrink();
        return Column(
          children: [
            EvidenciasCard(evidencias: incidente.evidencias),
            const SizedBox(height: 12),
          ],
        );
      },
      orElse: () => const SizedBox.shrink(),
    );
  }
}

class _BotonAccion extends StatelessWidget {
  final TechnicianAssignment asignacion;
  final bool isLoading;
  final VoidCallback? onPressed;

  const _BotonAccion({
    required this.asignacion,
    required this.isLoading,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    final (bgColor, fgColor) = _botonColores(asignacion.estadoIncidente, colorScheme);

    return SizedBox(
      width: double.infinity,
      height: 56,
      child: FilledButton.icon(
        style: FilledButton.styleFrom(
          backgroundColor: bgColor,
          foregroundColor: fgColor,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        ),
        onPressed: onPressed,
        icon: isLoading
            ? const SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
              )
            : Icon(_accionIcono(asignacion.estadoIncidente)),
        label: Text(
          isLoading ? 'Actualizando...' : (asignacion.accionLabel ?? ''),
          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
        ),
      ),
    );
  }

  (Color, Color) _botonColores(String estado, ColorScheme cs) {
    switch (estado.toUpperCase()) {
      case 'ASIGNADO':
        return (Colors.blue, Colors.white);
      case 'EN_CAMINO':
        return (Colors.orange, Colors.white);
      case 'EN_PROCESO':
        return (Colors.green, Colors.white);
      default:
        return (cs.primary, cs.onPrimary);
    }
  }

  IconData _accionIcono(String estado) {
    switch (estado.toUpperCase()) {
      case 'ASIGNADO':
        return Icons.directions_car;
      case 'EN_CAMINO':
        return Icons.build;
      case 'EN_PROCESO':
        return Icons.check_circle;
      default:
        return Icons.arrow_forward;
    }
  }
}

class _IncidenteFinalizadoCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Card(
      color: Colors.green.shade50,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          children: [
            Icon(Icons.check_circle, color: Colors.green.shade700, size: 36),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '¡Trabajo finalizado!',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          color: Colors.green.shade700,
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'El pago fue generado automáticamente.',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Colors.green.shade600,
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

// ── Helpers de UI compartidos ─────────────────────────────────────────────────

class _SeccionTitulo extends StatelessWidget {
  final IconData icon;
  final String titulo;
  const _SeccionTitulo({required this.icon, required this.titulo});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, size: 18, color: Theme.of(context).colorScheme.primary),
        const SizedBox(width: 8),
        Text(titulo,
            style: Theme.of(context)
                .textTheme
                .titleSmall
                ?.copyWith(fontWeight: FontWeight.bold)),
      ],
    );
  }
}

class _InfoFila extends StatelessWidget {
  final String label;
  final String valor;
  final Color? color;
  const _InfoFila({required this.label, required this.valor, this.color});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        children: [
          SizedBox(
            width: 90,
            child: Text(
              '$label:',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
            ),
          ),
          Expanded(
            child: Text(
              valor,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                    color: color,
                  ),
            ),
          ),
        ],
      ),
    );
  }
}
