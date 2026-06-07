import 'dart:async';
import 'dart:convert';

import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:geolocator/geolocator.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../../core/config.dart';
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

final sincronizacionProvider =
    StateNotifierProvider<SincronizacionNotifier, SincronizacionState>((ref) {
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
        errorMessage: clearError ? null : (errorMessage ?? this.errorMessage),
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
    _ref.invalidate(technicianTrackingProvider);
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

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
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

// ── Payments ──────────────────────────────────────────────────────────────────

final myPaymentsProvider =
    FutureProvider.autoDispose<List<Payment>>((ref) async {
  return ref.read(paymentsRepositoryProvider).listarMisPagos();
});

// ── Vehicles ──────────────────────────────────────────────────────────────────

final vehiclesProvider = FutureProvider.autoDispose<List<Vehicle>>((ref) async {
  return ref.read(vehicleRepositoryProvider).getVehicles();
});

// ── WS Notifications (global list) ───────────────────────────────────────────

class NotificationsNotifier extends StateNotifier<List<Map<String, dynamic>>> {
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
        errorMessage: clearError ? null : (errorMessage ?? this.errorMessage),
      );
}

class ReportFormNotifier extends StateNotifier<ReportFormState> {
  ReportFormNotifier(this._incidentRepo) : super(const ReportFormState());

  final IncidentRepository _incidentRepo;

  void setVehicle(String? vehicleId) =>
      state = state.copyWith(selectedVehicleId: vehicleId);

  void setDescription(String desc) => state = state.copyWith(description: desc);

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
        textoDescripcion:
            state.description.trim().isEmpty ? null : state.description.trim(),
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

final reportFormProvider =
    StateNotifierProvider.autoDispose<ReportFormNotifier, ReportFormState>(
  (ref) => ReportFormNotifier(ref.watch(incidentRepositoryProvider)),
);

// ── Technician: asignación activa ─────────────────────────────────────────────

final miAsignacionProvider =
    FutureProvider.autoDispose<TechnicianAssignment?>((ref) async {
  return ref.read(technicianRepositoryProvider).getMiAsignacion();
});

// ── Technician: cambio de estado (máquina de estados) ────────────────────────

class TechnicianStateUpdateNotifier extends StateNotifier<AsyncValue<void>> {
  TechnicianStateUpdateNotifier(this._repo)
      : super(const AsyncValue.data(null));

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
  (ref) =>
      TechnicianStateUpdateNotifier(ref.watch(technicianRepositoryProvider)),
);

// ── Technician: tracking GPS por WebSocket ────────────────────────────────────

class TechnicianTrackingState {
  final bool isTracking;
  final bool isConnecting;
  final String? incidentId;
  final TechnicianLocation? lastLocation;
  final String? errorMessage;

  const TechnicianTrackingState({
    this.isTracking = false,
    this.isConnecting = false,
    this.incidentId,
    this.lastLocation,
    this.errorMessage,
  });

  TechnicianTrackingState copyWith({
    bool? isTracking,
    bool? isConnecting,
    String? incidentId,
    TechnicianLocation? lastLocation,
    String? errorMessage,
    bool clearError = false,
    bool clearIncident = false,
  }) =>
      TechnicianTrackingState(
        isTracking: isTracking ?? this.isTracking,
        isConnecting: isConnecting ?? this.isConnecting,
        incidentId: clearIncident ? null : (incidentId ?? this.incidentId),
        lastLocation: lastLocation ?? this.lastLocation,
        errorMessage: clearError ? null : (errorMessage ?? this.errorMessage),
      );
}

class TechnicianTrackingNotifier
    extends StateNotifier<TechnicianTrackingState> {
  TechnicianTrackingNotifier(this._client)
      : super(const TechnicianTrackingState());

  final ApiClient _client;
  WebSocketChannel? _channel;
  StreamSubscription<dynamic>? _wsSubscription;
  Timer? _timer;

  Future<void> start(String incidentId) async {
    if (state.isTracking && state.incidentId == incidentId) return;
    await stop();
    state = TechnicianTrackingState(isConnecting: true, incidentId: incidentId);

    final token = await _client.getToken();
    if (token == null || token.isEmpty) {
      state = const TechnicianTrackingState(
        errorMessage: 'No hay sesión activa para iniciar tracking GPS',
      );
      return;
    }

    final hasPermission = await _ensureLocationPermission();
    if (!hasPermission) {
      state = TechnicianTrackingState(
        incidentId: incidentId,
        errorMessage: 'Permiso de ubicación requerido para iniciar tracking',
      );
      return;
    }

    try {
      final wsUrl =
          '${AppConfig.wsBaseUrl}/tracking/ws/incidents/$incidentId?token=$token';
      _channel = WebSocketChannel.connect(Uri.parse(wsUrl));
      _wsSubscription = _channel!.stream.listen(
        _handleServerMessage,
        onError: (_) => _setDisconnected('Conexión de tracking interrumpida'),
        onDone: () => _setDisconnected(null),
        cancelOnError: false,
      );

      state = TechnicianTrackingState(isTracking: true, incidentId: incidentId);
      await _sendCurrentLocation();
      _timer = Timer.periodic(
        const Duration(seconds: 10),
        (_) => _sendCurrentLocation(),
      );
    } catch (e) {
      await stop();
      state = TechnicianTrackingState(
          errorMessage: 'No se pudo iniciar tracking: $e');
    }
  }

  Future<void> stop() async {
    _timer?.cancel();
    _timer = null;
    await _wsSubscription?.cancel();
    _wsSubscription = null;
    await _channel?.sink.close();
    _channel = null;
    state = const TechnicianTrackingState();
  }

  Future<bool> _ensureLocationPermission() async {
    final serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) return false;

    var permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
    }
    return permission == LocationPermission.always ||
        permission == LocationPermission.whileInUse;
  }

  Future<void> _sendCurrentLocation() async {
    final incidentId = state.incidentId;
    final channel = _channel;
    if (incidentId == null || channel == null) return;

    try {
      final position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );
      channel.sink.add(jsonEncode({
        'lat': position.latitude,
        'lng': position.longitude,
      }));
      state = state.copyWith(
        isTracking: true,
        isConnecting: false,
        clearError: true,
        lastLocation: TechnicianLocation(
          idIncidente: incidentId,
          latitud: position.latitude,
          longitud: position.longitude,
          timestamp: DateTime.now(),
        ),
      );
    } catch (e) {
      state = state.copyWith(errorMessage: 'No se pudo enviar ubicación: $e');
    }
  }

  void _handleServerMessage(dynamic message) {
    try {
      final data = jsonDecode(message as String) as Map<String, dynamic>;
      if (data['tipo'] == 'tracking_finalizado') {
        stop();
      }
    } catch (_) {
      // Messages from the tracking server are informational; invalid payloads do not stop GPS.
    }
  }

  void _setDisconnected(String? message) {
    _timer?.cancel();
    _timer = null;
    _channel = null;
    state = TechnicianTrackingState(errorMessage: message);
  }

  @override
  void dispose() {
    _timer?.cancel();
    _wsSubscription?.cancel();
    _channel?.sink.close();
    super.dispose();
  }
}

final technicianTrackingProvider =
    StateNotifierProvider<TechnicianTrackingNotifier, TechnicianTrackingState>(
        (ref) {
  return TechnicianTrackingNotifier(ref.watch(apiClientProvider));
});
