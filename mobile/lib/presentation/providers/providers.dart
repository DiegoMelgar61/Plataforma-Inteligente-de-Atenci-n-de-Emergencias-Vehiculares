import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/api_client.dart';
import '../../data/local/offline_storage.dart';
import '../../data/models/models.dart';
import '../../data/repositories/repositories.dart';

// ── Service providers ─────────────────────────────────────────────────────────

final apiClientProvider = Provider<ApiClient>((ref) => ApiClient());

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository(ref.watch(apiClientProvider));
});

final incidentRepositoryProvider = Provider<IncidentRepository>((ref) {
  return IncidentRepository(ref.watch(apiClientProvider));
});

final vehicleRepositoryProvider = Provider<VehicleRepository>((ref) {
  return VehicleRepository(ref.watch(apiClientProvider));
});

final paymentsRepositoryProvider = Provider<PaymentsRepository>((ref) {
  return PaymentsRepository(ref.watch(apiClientProvider));
});

final technicianRepositoryProvider = Provider<TechnicianRepository>((ref) {
  return TechnicianRepository(ref.watch(apiClientProvider));
});

final offlineSyncRepositoryProvider = Provider<OfflineSyncRepository>((ref) {
  return OfflineSyncRepository(ref.watch(apiClientProvider));
});

// ── Offline connectivity/sync ─────────────────────────────────────────────────

final connectivityProvider = StreamProvider<bool>((ref) {
  return Connectivity().onConnectivityChanged.map(
        (result) => result != ConnectivityResult.none,
      );
});

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

  const SincronizacionCompletada({
    required this.sincronizados,
    required this.omitidos,
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
      state = SincronizacionCompletada(
        sincronizados: sincronizados,
        omitidos: omitidos,
      );
      _ref.invalidate(pendientesCountProvider);
      _ref.invalidate(myIncidentsProvider);
    } catch (e) {
      state = SincronizacionError(e.toString().replaceAll('Exception: ', ''));
    }
  }

  void reset() => state = const SincronizacionIdle();
}

final sincronizacionProvider = StateNotifierProvider<SincronizacionNotifier,
    SincronizacionState>((ref) {
  return SincronizacionNotifier(ref.watch(offlineSyncRepositoryProvider), ref);
});

// ── Auth state ────────────────────────────────────────────────────────────────

class AuthState {
  final bool isAuthenticated;
  final User? currentUser;
  final bool isLoading;
  final String? errorMessage;

  const AuthState({
    this.isAuthenticated = false,
    this.currentUser,
    this.isLoading = false,
    this.errorMessage,
  });

  AuthState copyWith({
    bool? isAuthenticated,
    User? currentUser,
    bool? isLoading,
    String? errorMessage,
    bool clearError = false,
    bool clearUser = false,
  }) =>
      AuthState(
        isAuthenticated: isAuthenticated ?? this.isAuthenticated,
        currentUser: clearUser ? null : (currentUser ?? this.currentUser),
        isLoading: isLoading ?? this.isLoading,
        errorMessage:
            clearError ? null : (errorMessage ?? this.errorMessage),
      );
}

class AuthNotifier extends StateNotifier<AuthState> {
  AuthNotifier(this._repo, this._ref) : super(const AuthState());

  final AuthRepository _repo;
  final Ref _ref;

  Future<bool> login(String email, String password) async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      await _repo.login(email, password);
      final user = await _repo.getCurrentUser();
      state = state.copyWith(
        isAuthenticated: true,
        isLoading: false,
        currentUser: user,
      );
      return true;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: e.toString().replaceAll('Exception: ', ''),
      );
      return false;
    }
  }

  Future<void> logout() async {
    await _repo.logout();
    _ref.invalidate(myIncidentsProvider);
    _ref.invalidate(vehiclesProvider);
    _ref.invalidate(miAsignacionProvider);
    state = const AuthState();
  }

  Future<bool> checkAuth() async {
    final hasToken = await _repo.hasToken();
    if (hasToken) {
      final user = await _repo.getCurrentUser();
      state = state.copyWith(isAuthenticated: true, currentUser: user);
    } else {
      state = const AuthState();
    }
    return hasToken;
  }

  void clearError() => state = state.copyWith(clearError: true);
}

final authProvider =
    StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(ref.watch(authRepositoryProvider), ref);
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

// ── Payments ──────────────────────────────────────────────────────────────────

final myPaymentsProvider =
    FutureProvider.autoDispose<List<Payment>>((ref) async {
  return ref.read(paymentsRepositoryProvider).listarMisPagos();
});

// ── Vehicles ──────────────────────────────────────────────────────────────────

final vehiclesProvider =
    FutureProvider.autoDispose<List<Vehicle>>((ref) async {
  return ref.read(vehicleRepositoryProvider).getVehicles();
});

// ── WS Notifications (global list) ───────────────────────────────────────────

class NotificationsNotifier
    extends StateNotifier<List<Map<String, dynamic>>> {
  NotificationsNotifier() : super(const []);

  void add(Map<String, dynamic> notification) {
    state = [notification, ...state];
  }

  void clear() => state = const [];
}

final notificationsProvider =
    StateNotifierProvider<NotificationsNotifier, List<Map<String, dynamic>>>(
  (ref) => NotificationsNotifier(),
);

// ── Report form state ─────────────────────────────────────────────────────────

class ReportFormState {
  final String? selectedVehicleId; // UUID string
  final String description;
  final double? latitude;
  final double? longitude;
  final List<String> filePaths;
  final bool isSubmitting;
  final String? errorMessage;

  const ReportFormState({
    this.selectedVehicleId,
    this.description = '',
    this.latitude,
    this.longitude,
    this.filePaths = const [],
    this.isSubmitting = false,
    this.errorMessage,
  });

  ReportFormState copyWith({
    String? selectedVehicleId,
    String? description,
    double? latitude,
    double? longitude,
    List<String>? filePaths,
    bool? isSubmitting,
    String? errorMessage,
    bool clearError = false,
    bool clearVehicle = false,
  }) =>
      ReportFormState(
        selectedVehicleId:
            clearVehicle ? null : (selectedVehicleId ?? this.selectedVehicleId),
        description: description ?? this.description,
        latitude: latitude ?? this.latitude,
        longitude: longitude ?? this.longitude,
        filePaths: filePaths ?? this.filePaths,
        isSubmitting: isSubmitting ?? this.isSubmitting,
        errorMessage:
            clearError ? null : (errorMessage ?? this.errorMessage),
      );
}

class ReportFormNotifier extends StateNotifier<ReportFormState> {
  ReportFormNotifier(this._incidentRepo) : super(const ReportFormState());

  final IncidentRepository _incidentRepo;

  void setVehicle(String? vehicleId) =>
      state = state.copyWith(selectedVehicleId: vehicleId);

  void setDescription(String desc) =>
      state = state.copyWith(description: desc);

  void setLocation(double lat, double lng) =>
      state = state.copyWith(latitude: lat, longitude: lng);

  void addFile(String path) =>
      state = state.copyWith(filePaths: [...state.filePaths, path]);

  void removeFile(String path) => state = state.copyWith(
      filePaths: state.filePaths.where((p) => p != path).toList());

  void reset() => state = const ReportFormState();

  Future<bool> submit() async {
    if (state.latitude == null || state.longitude == null) {
      state = state.copyWith(
          errorMessage: 'Obtén tu ubicación GPS antes de enviar');
      return false;
    }
    state = state.copyWith(isSubmitting: true, clearError: true);
    try {
      await _incidentRepo.reportIncident(
        latitud: state.latitude!,
        longitud: state.longitude!,
        idVehiculo: state.selectedVehicleId,
        textoDescripcion: state.description.trim().isEmpty
            ? null
            : state.description.trim(),
        imagenesPath: state.filePaths,
      );
      state = const ReportFormState();
      return true;
    } catch (e) {
      state = state.copyWith(
        isSubmitting: false,
        errorMessage: e.toString().replaceAll('Exception: ', ''),
      );
      return false;
    }
  }
}

final reportFormProvider = StateNotifierProvider.autoDispose<ReportFormNotifier,
    ReportFormState>(
  (ref) => ReportFormNotifier(ref.watch(incidentRepositoryProvider)),
);

// ── Technician: asignación activa ─────────────────────────────────────────────

final miAsignacionProvider =
    FutureProvider.autoDispose<TechnicianAssignment?>((ref) async {
  return ref.read(technicianRepositoryProvider).getMiAsignacion();
});

// ── Technician: cambio de estado (máquina de estados) ────────────────────────

class TechnicianStateUpdateNotifier extends StateNotifier<AsyncValue<void>> {
  TechnicianStateUpdateNotifier(this._repo) : super(const AsyncValue.data(null));

  final TechnicianRepository _repo;

  Future<void> updateState(String idIncidente, String nuevoEstado) async {
    state = const AsyncValue.loading();
    try {
      await _repo.updateIncidentState(idIncidente, nuevoEstado);
      state = const AsyncValue.data(null);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  void reset() => state = const AsyncValue.data(null);
}

final technicianStateUpdateProvider = StateNotifierProvider.autoDispose<
    TechnicianStateUpdateNotifier, AsyncValue<void>>(
  (ref) => TechnicianStateUpdateNotifier(ref.watch(technicianRepositoryProvider)),
);
