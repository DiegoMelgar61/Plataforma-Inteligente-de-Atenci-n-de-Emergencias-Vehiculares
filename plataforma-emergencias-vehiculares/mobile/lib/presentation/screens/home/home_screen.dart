import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/constants.dart';
import '../../../data/models/models.dart';
import '../../../core/extensions.dart';
import '../../providers/providers.dart';
import '../../../shared/widgets.dart';
import '../incidents/incidents_screen.dart';
import '../map/map_screen.dart';
import '../profile/profile_screen.dart';
import '../payments/my_payments_screen.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  int _currentIndex = 0;

  static const List<Widget> _tabs = [
    _DashboardTab(),
    IncidentsScreen(),
    MapScreen(),
    MyPaymentsScreen(),
    ProfileScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: _tabs,
      ),
      floatingActionButton: _currentIndex == 0
          ? FloatingActionButton.extended(
              onPressed: () =>
                  Navigator.pushNamed(context, AppConstants.routeReport),
              icon: const Icon(Icons.add_alert),
              label: const Text('Reportar emergencia'),
              backgroundColor: colorScheme.error,
              foregroundColor: colorScheme.onError,
            )
          : null,
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (index) =>
            setState(() => _currentIndex = index),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.dashboard_outlined),
            selectedIcon: Icon(Icons.dashboard),
            label: 'Inicio',
          ),
          NavigationDestination(
            icon: Icon(Icons.list_alt_outlined),
            selectedIcon: Icon(Icons.list_alt),
            label: 'Incidentes',
          ),
          NavigationDestination(
            icon: Icon(Icons.map_outlined),
            selectedIcon: Icon(Icons.map),
            label: 'Mapa',
          ),
          NavigationDestination(
            icon: Icon(Icons.receipt_long_outlined),
            selectedIcon: Icon(Icons.receipt_long),
            label: 'Mis Pagos',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outlined),
            selectedIcon: Icon(Icons.person),
            label: 'Perfil',
          ),
        ],
      ),
    );
  }
}

// ── Dashboard tab ─────────────────────────────────────────────────────────────

class _DashboardTab extends ConsumerWidget {
  const _DashboardTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);
    final incidentsAsync = ref.watch(myIncidentsProvider);
    final colorScheme = Theme.of(context).colorScheme;
    final userName =
        authState.currentUser?.nombreCompleto.split(' ').first ?? 'Usuario';

    return Scaffold(
      appBar: AppBar(
        title: const Text('Emergencias Vehiculares'),
        centerTitle: false,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_outlined),
            tooltip: 'Actualizar',
            onPressed: () => ref.invalidate(myIncidentsProvider),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async => ref.invalidate(myIncidentsProvider),
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Welcome card
            Card(
              color: colorScheme.primaryContainer,
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Row(
                  children: [
                    CircleAvatar(
                      radius: 30,
                      backgroundColor: colorScheme.primary,
                      child: Text(
                        authState.currentUser?.initials ?? 'U',
                        style: TextStyle(
                          color: colorScheme.onPrimary,
                          fontWeight: FontWeight.bold,
                          fontSize: 20,
                        ),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '¡Hola, $userName!',
                            style: Theme.of(context)
                                .textTheme
                                .titleLarge
                                ?.copyWith(
                                  fontWeight: FontWeight.bold,
                                  color: colorScheme.onPrimaryContainer,
                                ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            authState.currentUser?.roleLabel ?? 'Cliente',
                            style: Theme.of(context)
                                .textTheme
                                .bodyMedium
                                ?.copyWith(
                                  color: colorScheme.onPrimaryContainer
                                      .withOpacity(0.75),
                                ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),

            // Stats row
            incidentsAsync.when(
              loading: () => const SizedBox.shrink(),
              error: (_, __) => const SizedBox.shrink(),
              data: (incidents) => _StatsRow(incidents: incidents),
            ),
            const SizedBox(height: 20),

            // Recent incidents
            Text(
              'Incidentes recientes',
              style: Theme.of(context)
                  .textTheme
                  .titleMedium
                  ?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            incidentsAsync.when(
              loading: () => const AppLoadingIndicator(),
              error: (error, _) => AppErrorCard(
                message: error.toString().withoutException,
                onRetry: () => ref.invalidate(myIncidentsProvider),
              ),
              data: (incidents) {
                if (incidents.isEmpty) {
                  return const EmptyStateWidget(
                    icon: Icons.check_circle_outline,
                    title: 'Sin incidentes registrados',
                    subtitle:
                        'Presiona el botón "Reportar emergencia" cuando necesites ayuda.',
                  );
                }
                return Column(
                  children: incidents
                      .take(3)
                      .map(
                        (incident) => IncidentCard(
                          incident: incident,
                          onTap: () => Navigator.pushNamed(
                            context,
                            AppConstants.routeIncidentDetail,
                            arguments: incident.idIncidente,
                          ),
                        ),
                      )
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

class _StatsRow extends StatelessWidget {
  final List<Incident> incidents;
  const _StatsRow({required this.incidents});

  @override
  Widget build(BuildContext context) {
    final active = incidents.where((i) => i.isActive).length; // uses Incident.isActive getter
    final resolved =
        incidents.where((i) => i.estado.toUpperCase() == 'ATENDIDO').length;
    final total = incidents.length;

    return Row(
      children: [
        Expanded(
            child: _StatCard(value: '$total', label: 'Total', icon: Icons.list)),
        const SizedBox(width: 10),
        Expanded(
            child: _StatCard(
                value: '$active',
                label: 'Activos',
                icon: Icons.pending_actions,
                color: Colors.orange)),
        const SizedBox(width: 10),
        Expanded(
            child: _StatCard(
                value: '$resolved',
                label: 'Resueltos',
                icon: Icons.check_circle,
                color: Colors.green)),
      ],
    );
  }
}

class _StatCard extends StatelessWidget {
  final String value;
  final String label;
  final IconData icon;
  final Color? color;

  const _StatCard({
    required this.value,
    required this.label,
    required this.icon,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    final c = color ?? Theme.of(context).colorScheme.primary;
    return Card(
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 12),
        child: Column(
          children: [
            Icon(icon, color: c, size: 28),
            const SizedBox(height: 6),
            Text(
              value,
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: c,
                  ),
            ),
            Text(
              label,
              style: Theme.of(context).textTheme.labelSmall,
            ),
          ],
        ),
      ),
    );
  }
}
