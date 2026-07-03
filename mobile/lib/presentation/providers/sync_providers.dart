import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/local/offline_storage.dart';
import '../../data/repositories/sync_repository.dart';
import 'core_providers.dart';
import 'incident_providers.dart';

final offlineSyncRepositoryProvider = Provider<OfflineSyncRepository>((ref) {
  return OfflineSyncRepository(ref.watch(apiClientProvider));
});

// ── Offline sync ──────────────────────────────────────────────────────────────

final pendientesCountProvider = FutureProvider.autoDispose<int>((ref) async {
  final pendientes = await OfflineStorage.obtenerPendientes();
  return pendientes.length;
});

sealed class SincronizacionState {
  const SincronizacionState();
}

class SincronizacionIdle extends SincronizacionState {
  const SincronizacionIdle();
}

class SincronizacionEnProgreso extends SincronizacionState {
  const SincronizacionEnProgreso();
}

class SincronizacionCompletada extends SincronizacionState {
  final int sincronizados;
  final int omitidos;
  // Each entry: {'id_local': '...', 'id_incidente': '...'}
  final List<Map<String, String>> resultados;

  const SincronizacionCompletada({
    required this.sincronizados,
    required this.omitidos,
    this.resultados = const [],
  });
}

class SincronizacionError extends SincronizacionState {
  final String mensaje;

  const SincronizacionError(this.mensaje);
}

class SincronizacionNotifier extends StateNotifier<SincronizacionState> {
  SincronizacionNotifier(this._repo, this._ref)
      : super(const SincronizacionIdle());

  final OfflineSyncRepository _repo;
  final Ref _ref;

  Future<void> sincronizarPendientes() async {
    if (state is SincronizacionEnProgreso) return;

    state = const SincronizacionEnProgreso();
    try {
      final result = await _repo.sincronizarPendientes();
      final sincronizados = (result['sincronizados'] as num?)?.toInt() ?? 0;
      final omitidos = (result['omitidos'] as num?)?.toInt() ?? 0;
      final rawResultados = result['resultados'] as List<dynamic>? ?? [];
      final resultados = rawResultados
          .whereType<Map<String, dynamic>>()
          .map((r) => {
                'id_local': r['id_local']?.toString() ?? '',
                'id_incidente': r['id_incidente']?.toString() ?? '',
              })
          .toList();
      state = SincronizacionCompletada(
        sincronizados: sincronizados,
        omitidos: omitidos,
        resultados: resultados,
      );
      _ref.invalidate(pendientesCountProvider);
      _ref.invalidate(myIncidentsProvider);
    } catch (e) {
      state = SincronizacionError(e.toString().replaceAll('Exception: ', ''));
    }
  }

  void reset() => state = const SincronizacionIdle();
}

final sincronizacionProvider =
    StateNotifierProvider<SincronizacionNotifier, SincronizacionState>((ref) {
  return SincronizacionNotifier(ref.watch(offlineSyncRepositoryProvider), ref);
});
