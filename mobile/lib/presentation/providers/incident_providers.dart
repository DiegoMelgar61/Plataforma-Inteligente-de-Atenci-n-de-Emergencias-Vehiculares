import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/models/incident_models.dart';
import '../../data/repositories/incident_repository.dart';
import 'core_providers.dart';

final incidentRepositoryProvider = Provider<IncidentRepository>((ref) {
  return IncidentRepository(ref.watch(apiClientProvider));
});

// ── Incidents ─────────────────────────────────────────────────────────────────

final myIncidentsProvider =
    FutureProvider.autoDispose<List<Incident>>((ref) async {
  return ref.read(incidentRepositoryProvider).getMyIncidents();
});

/// Family key is the UUID string of the incident.
final selectedIncidentProvider =
    FutureProvider.autoDispose.family<Incident, String>((ref, id) async {
  return ref.read(incidentRepositoryProvider).getIncidentById(id);
});

final incidentQuotationProvider = FutureProvider.autoDispose
    .family<CotizacionDetalle?, String>((ref, id) async {
  return ref.read(incidentRepositoryProvider).getCotizacion(id);
});

// Ofertas de talleres cercanos (flujo InDrive), visibles cuando el incidente
// está CLASIFICADO y el cliente aún no eligió taller.
final cotizacionesProvider = FutureProvider.autoDispose
    .family<List<CotizacionOferta>, String>((ref, id) async {
  return ref.read(incidentRepositoryProvider).getCotizaciones(id);
});

/// Selección de taller por el cliente. Al elegir, el incidente pasa a EN_CAMINO.
class SeleccionTallerNotifier extends StateNotifier<AsyncValue<void>> {
  SeleccionTallerNotifier(this._repo, this._ref, this._incidentId)
      : super(const AsyncValue.data(null));

  final IncidentRepository _repo;
  final Ref _ref;
  final String _incidentId;

  Future<bool> seleccionar(String idTaller) async {
    state = const AsyncValue.loading();
    try {
      await _repo.seleccionarTaller(_incidentId, idTaller);
      state = const AsyncValue.data(null);
      _ref.invalidate(selectedIncidentProvider(_incidentId));
      _ref.invalidate(cotizacionesProvider(_incidentId));
      return true;
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      return false;
    }
  }
}

final seleccionTallerProvider = StateNotifierProvider.autoDispose
    .family<SeleccionTallerNotifier, AsyncValue<void>, String>((ref, id) {
  return SeleccionTallerNotifier(
      ref.watch(incidentRepositoryProvider), ref, id);
});

class QuotationResponseNotifier extends StateNotifier<AsyncValue<void>> {
  QuotationResponseNotifier(this._repo, this._ref, this._incidentId)
      : super(const AsyncValue.data(null));

  final IncidentRepository _repo;
  final Ref _ref;
  final String _incidentId;

  Future<void> respond({
    required bool accepted,
    String? rejectionReason,
  }) async {
    state = const AsyncValue.loading();
    try {
      await _repo.responderCotizacion(
        _incidentId,
        aceptada: accepted,
        motivoRechazo: rejectionReason,
      );
      _ref.invalidate(incidentQuotationProvider(_incidentId));
      _ref.invalidate(selectedIncidentProvider(_incidentId));
      _ref.invalidate(myIncidentsProvider);
      state = const AsyncValue.data(null);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  void reset() => state = const AsyncValue.data(null);
}

final quotationResponseProvider = StateNotifierProvider.autoDispose
    .family<QuotationResponseNotifier, AsyncValue<void>, String>((ref, id) {
  return QuotationResponseNotifier(
    ref.watch(incidentRepositoryProvider),
    ref,
    id,
  );
});
