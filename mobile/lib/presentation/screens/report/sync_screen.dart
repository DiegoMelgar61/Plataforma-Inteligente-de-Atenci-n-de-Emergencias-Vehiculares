import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../../core/constants.dart';
import '../../../data/local/offline_storage.dart';
import '../../../data/models/models.dart';
import '../../providers/providers.dart';

class SyncScreen extends ConsumerStatefulWidget {
  const SyncScreen({super.key});

  @override
  ConsumerState<SyncScreen> createState() => _SyncScreenState();
}

class _SyncScreenState extends ConsumerState<SyncScreen> {
  late Future<List<EmergenciaLocal>> _future;

  @override
  void initState() {
    super.initState();
    _future = OfflineStorage.obtenerPendientes();
  }

  void _reload() {
    setState(() => _future = OfflineStorage.obtenerPendientes());
    ref.invalidate(pendientesCountProvider);
  }

  Future<void> _sync() async {
    await ref.read(sincronizacionProvider.notifier).sincronizarPendientes();
    _reload();
  }

  @override
  Widget build(BuildContext context) {
    final syncState = ref.watch(sincronizacionProvider);
    final syncing = syncState is SincronizacionEnProgreso;

    return Scaffold(
      appBar: AppBar(title: const Text('Emergencias offline')),
      body: RefreshIndicator(
        onRefresh: () async => _reload(),
        child: FutureBuilder<List<EmergenciaLocal>>(
          future: _future,
          builder: (context, snapshot) {
            final pendientes = snapshot.data ?? const <EmergenciaLocal>[];

            return ListView(
              padding: const EdgeInsets.all(16),
              children: [
                if (syncState is SincronizacionCompletada) ...[
                  _ResultCard(
                    message:
                        '${syncState.sincronizados} sincronizadas, ${syncState.omitidos} omitidas',
                    color: Theme.of(context).colorScheme.primaryContainer,
                  ),
                  if (syncState.sincronizados > 0) ...[
                    const SizedBox(height: 8),
                    FilledButton.icon(
                      onPressed: () => Navigator.pushNamedAndRemoveUntil(
                        context,
                        AppConstants.routeIncidents,
                        ModalRoute.withName(AppConstants.routeHome),
                      ),
                      icon: const Icon(Icons.list_alt),
                      label: const Text('Ver mis incidentes'),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Los incidentes sincronizados ya estan disponibles.',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ],
                  const SizedBox(height: 8),
                ],
                if (syncState is SincronizacionError)
                  _ResultCard(
                    message: syncState.mensaje,
                    color: Theme.of(context).colorScheme.errorContainer,
                  ),
                if (snapshot.connectionState == ConnectionState.waiting)
                  const Center(child: CircularProgressIndicator())
                else if (pendientes.isEmpty)
                  const Padding(
                    padding: EdgeInsets.only(top: 80),
                    child: Center(child: Text('Todo sincronizado')),
                  )
                else ...[
                  FilledButton.icon(
                    onPressed: syncing ? null : _sync,
                    icon: syncing
                        ? const SizedBox(
                            width: 18,
                            height: 18,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.sync),
                    label: Text(syncing ? 'Sincronizando...' : 'Sincronizar ahora'),
                  ),
                  const SizedBox(height: 16),
                  ...pendientes.map(_EmergencyCard.new),
                ],
              ],
            );
          },
        ),
      ),
    );
  }
}

class _EmergencyCard extends StatelessWidget {
  final EmergenciaLocal emergencia;

  const _EmergencyCard(this.emergencia);

  @override
  Widget build(BuildContext context) {
    final hasError = emergencia.error_sync != null;
    final status = emergencia.sincronizado
        ? 'Sincronizado'
        : hasError
            ? 'Error'
            : 'Pendiente';
    final color = emergencia.sincronizado
        ? Colors.green
        : hasError
            ? Theme.of(context).colorScheme.error
            : Colors.orange;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    emergencia.descripcion,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: Theme.of(context).textTheme.titleSmall,
                  ),
                ),
                Chip(
                  label: Text(status),
                  labelStyle: TextStyle(color: color),
                  side: BorderSide(color: color.withOpacity(0.4)),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              DateFormat('dd/MM/yyyy HH:mm').format(emergencia.fecha_creacion),
              style: Theme.of(context).textTheme.bodySmall,
            ),
            if (hasError) ...[
              const SizedBox(height: 8),
              Text(
                emergencia.error_sync!,
                style: TextStyle(color: Theme.of(context).colorScheme.error),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _ResultCard extends StatelessWidget {
  final String message;
  final Color color;

  const _ResultCard({required this.message, required this.color});

  @override
  Widget build(BuildContext context) {
    return Card(
      color: color,
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Text(message),
      ),
    );
  }
}
