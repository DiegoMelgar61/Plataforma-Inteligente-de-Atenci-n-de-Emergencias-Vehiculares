import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/constants.dart';
import '../../../core/extensions.dart';
import '../../../data/models/models.dart';
import '../../providers/providers.dart';
import '../../../shared/widgets.dart';

class IncidentsScreen extends ConsumerStatefulWidget {
  const IncidentsScreen({super.key});

  @override
  ConsumerState<IncidentsScreen> createState() => _IncidentsScreenState();
}

class _IncidentsScreenState extends ConsumerState<IncidentsScreen> {
  String _selectedFilter = 'TODOS';

  static const _filters = [
    ('TODOS', 'Todos'),
    ('PENDIENTE', 'Pendiente'),
    ('ASIGNADO', 'Asignado'),
    ('EN_PROCESO', 'En Proceso'),
    ('ATENDIDO', 'Resuelto'),
    ('CANCELADO', 'Cancelado'),
  ];

  List<Incident> _applyFilter(List<Incident> incidents) {
    if (_selectedFilter == 'TODOS') return incidents;
    return incidents
        .where((i) => i.estado.toUpperCase() == _selectedFilter)
        .toList();
  }

  @override
  Widget build(BuildContext context) {
    final incidentsAsync = ref.watch(myIncidentsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Mis Incidentes'),
        centerTitle: false,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_outlined),
            tooltip: 'Actualizar',
            onPressed: () => ref.invalidate(myIncidentsProvider),
          ),
        ],
      ),
      body: incidentsAsync.when(
        loading: () =>
            const AppLoadingIndicator(message: 'Cargando incidentes...'),
        error: (error, _) => Center(
          child: AppErrorCard(
            message: error.toString().withoutException,
            onRetry: () => ref.invalidate(myIncidentsProvider),
          ),
        ),
        data: (incidents) {
          if (incidents.isEmpty) {
            return EmptyStateWidget(
              icon: Icons.car_crash_outlined,
              title: 'Sin incidentes registrados',
              subtitle: 'Cuando reportes una emergencia, aparecerá aquí.',
              action: FilledButton.icon(
                onPressed: () =>
                    Navigator.pushNamed(context, AppConstants.routeReport),
                icon: const Icon(Icons.add_alert),
                label: const Text('Reportar emergencia'),
              ),
            );
          }

          final filtered = _applyFilter(incidents);

          return RefreshIndicator(
            onRefresh: () async => ref.invalidate(myIncidentsProvider),
            child: Column(
              children: [
                // Filter chips
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  padding: const EdgeInsets.symmetric(
                      horizontal: 12, vertical: 10),
                  child: Row(
                    children: _filters
                        .map(
                          (f) => Padding(
                            padding: const EdgeInsets.only(right: 8),
                            child: FilterChip(
                              label: Text(f.$2),
                              selected: _selectedFilter == f.$1,
                              onSelected: (_) =>
                                  setState(() => _selectedFilter = f.$1),
                            ),
                          ),
                        )
                        .toList(),
                  ),
                ),
                if (filtered.isEmpty)
                  Expanded(
                    child: EmptyStateWidget(
                      icon: Icons.filter_list_off,
                      title: 'Sin incidentes',
                      subtitle:
                          'No hay incidentes con el estado seleccionado.',
                    ),
                  )
                else
                  Expanded(
                    child: ListView.builder(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 16, vertical: 8),
                      itemCount: filtered.length,
                      itemBuilder: (context, index) {
                        final incident = filtered[index];
                        return IncidentCard(
                          incident: incident,
                          onTap: () => Navigator.pushNamed(
                            context,
                            AppConstants.routeIncidentDetail,
                            arguments: incident.idIncidente,
                          ),
                        );
                      },
                    ),
                  ),
              ],
            ),
          );
        },
      ),
    );
  }
}
