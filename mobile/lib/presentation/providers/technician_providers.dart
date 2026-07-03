import 'dart:async';
import 'dart:convert';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:geolocator/geolocator.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../../core/config.dart';
import '../../core/api_client.dart';
import '../../data/models/assignment_models.dart';
import '../../data/repositories/technician_repository.dart';
import 'core_providers.dart';

final technicianRepositoryProvider = Provider<TechnicianRepository>((ref) {
  return TechnicianRepository(ref.watch(apiClientProvider));
});

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

  Future<void> updateState(int idIncidente, String nuevoEstado) async {
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
  final int? incidentId;
  final TechnicianLocation? lastLocation;
  final String? errorMessage;
  final String? avisoCancelacion; // aviso push cuando el cliente cancela

  const TechnicianTrackingState({
    this.isTracking = false,
    this.isConnecting = false,
    this.incidentId,
    this.lastLocation,
    this.errorMessage,
    this.avisoCancelacion,
  });

  TechnicianTrackingState copyWith({
    bool? isTracking,
    bool? isConnecting,
    int? incidentId,
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

  Future<void> start(int incidentId) async {
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
      final tipo = data['tipo'];
      if (tipo == 'servicio_cancelado') {
        // El cliente canceló: cortar el tracking y dejar un aviso para la UI.
        _timer?.cancel();
        _timer = null;
        _wsSubscription?.cancel();
        _wsSubscription = null;
        _channel?.sink.close();
        _channel = null;
        state = TechnicianTrackingState(
          avisoCancelacion: (data['mensaje'] as String?) ??
              'El servicio fue cancelado por el cliente.',
        );
        return;
      }
      if (tipo == 'tracking_finalizado') {
        stop();
      }
    } catch (_) {
      // Messages from the tracking server are informational; invalid payloads do not stop GPS.
    }
  }

  /// Limpia el aviso de cancelación una vez mostrado en pantalla.
  void limpiarAviso() {
    if (state.avisoCancelacion != null) {
      state = const TechnicianTrackingState();
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
