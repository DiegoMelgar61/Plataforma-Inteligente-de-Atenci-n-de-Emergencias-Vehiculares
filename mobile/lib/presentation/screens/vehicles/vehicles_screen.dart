import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/constants.dart';
import '../../providers/providers.dart';
import '../../../shared/widgets.dart';
class VehiclesScreen extends ConsumerWidget {
  const VehiclesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final vehiclesAsync = ref.watch(vehiclesProvider);
    final colorScheme = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Mis vehículos'),
        centerTitle: false,
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => Navigator.pushNamed(context, AppConstants.routeAddVehicle),
        child: const Icon(Icons.add),
      ),
      body: vehiclesAsync.when(
        loading: () => const AppLoadingIndicator(message: 'Cargando vehículos...'),
        error: (error, _) => AppErrorCard(
          message: error.toString().replaceAll('Exception: ', ''),
          onRetry: () => ref.invalidate(vehiclesProvider),
        ),
        data: (vehicles) {
          if (vehicles.isEmpty) {
            return EmptyStateWidget(
              icon: Icons.directions_car_outlined,
              title: 'No tenés vehículos registrados',
              subtitle: 'Agregá un vehículo para poder reportar emergencias',
              action: FilledButton.icon(
                onPressed: () => Navigator.pushNamed(context, AppConstants.routeAddVehicle),
                icon: const Icon(Icons.add),
                label: const Text('Agregar vehículo'),
              ),
            );
          }

          return RefreshIndicator(
            onRefresh: () => ref.refresh(vehiclesProvider.future),
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: vehicles.length,
              itemBuilder: (context, index) {
                final vehicle = vehicles[index];
                return Card(
                  margin: const EdgeInsets.only(bottom: 10),
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Row(
                      children: [
                        CircleAvatar(
                          radius: 24,
                          backgroundColor: colorScheme.secondaryContainer,
                          child: Icon(
                            Icons.directions_car,
                            color: colorScheme.onSecondaryContainer,
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                vehicle.displayName,
                                style: Theme.of(context)
                                    .textTheme
                                    .titleSmall
                                    ?.copyWith(fontWeight: FontWeight.bold),
                              ),
                              if (vehicle.anio != null)
                                Text(
                                  'Año: ${vehicle.anio}',
                                  style: Theme.of(context)
                                      .textTheme
                                      .bodySmall
                                      ?.copyWith(
                                        color: colorScheme.onSurfaceVariant,
                                      ),
                                ),
                            ],
                          ),
                        ),
                        PopupMenuButton<String>(
                          onSelected: (value) async {
                            if (value == 'edit') {
                              final result = await Navigator.pushNamed(
                                context,
                                AppConstants.routeAddVehicle,
                                arguments: vehicle,
                              );
                              if (result == true) {
                                ref.invalidate(vehiclesProvider);
                              }
                            } else if (value == 'delete') {
                              final confirmed = await showDialog<bool>(
                                context: context,
                                builder: (ctx) => AlertDialog(
                                  title: const Text('Eliminar vehículo'),
                                  content: Text(
                                      '¿Eliminar ${vehicle.displayName}?'),
                                  actions: [
                                    TextButton(
                                      onPressed: () => Navigator.pop(ctx, false),
                                      child: const Text('Cancelar'),
                                    ),
                                    FilledButton(
                                      onPressed: () => Navigator.pop(ctx, true),
                                      style: FilledButton.styleFrom(
                                        backgroundColor: colorScheme.error,
                                      ),
                                      child: const Text('Eliminar'),
                                    ),
                                  ],
                                ),
                              );
                              if (confirmed == true) {
                                final success = await ref
                                    .read(vehicleFormProvider.notifier)
                                    .deleteVehicle(
                                        int.parse(vehicle.idVehiculo));
                                if (success && context.mounted) {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(
                                        content: Text('Vehículo eliminado')),
                                  );
                                }
                              }
                            }
                          },
                          itemBuilder: (context) => [
                            const PopupMenuItem(
                              value: 'edit',
                              child: ListTile(
                                leading: Icon(Icons.edit_outlined),
                                title: Text('Editar'),
                                contentPadding: EdgeInsets.zero,
                              ),
                            ),
                            const PopupMenuItem(
                              value: 'delete',
                              child: ListTile(
                                leading: Icon(Icons.delete_outlined),
                                title: Text('Eliminar'),
                                contentPadding: EdgeInsets.zero,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          );
        },
      ),
    );
  }
}
