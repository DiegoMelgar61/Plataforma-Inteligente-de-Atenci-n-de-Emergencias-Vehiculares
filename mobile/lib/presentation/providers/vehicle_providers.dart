import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/models/vehicle_models.dart';
import '../../data/repositories/vehicle_repository.dart';
import 'core_providers.dart';

final vehicleRepositoryProvider = Provider<VehicleRepository>((ref) {
  return VehicleRepository(ref.watch(apiClientProvider));
});

// ── Vehicles ──────────────────────────────────────────────────────────────────

final vehiclesProvider = FutureProvider.autoDispose<List<Vehicle>>((ref) async {
  return ref.read(vehicleRepositoryProvider).getVehicles();
});

// ── Vehicle form state ────────────────────────────────────────────────────────

class VehicleFormState {
  final bool isLoading;
  final String? errorMessage;
  final bool success;

  const VehicleFormState({
    this.isLoading = false,
    this.errorMessage,
    this.success = false,
  });

  VehicleFormState copyWith({
    bool? isLoading,
    String? errorMessage,
    bool clearError = false,
    bool? success,
  }) =>
      VehicleFormState(
        isLoading: isLoading ?? this.isLoading,
        errorMessage: clearError ? null : (errorMessage ?? this.errorMessage),
        success: success ?? this.success,
      );
}

class VehicleFormNotifier extends StateNotifier<VehicleFormState> {
  VehicleFormNotifier(this._repo, this._ref) : super(const VehicleFormState());

  final VehicleRepository _repo;
  final Ref _ref;

  Future<bool> createVehicle({
    String? marca,
    String? modelo,
    int? anio,
    String? placa,
  }) async {
    state = state.copyWith(isLoading: true, clearError: true, success: false);
    try {
      await _repo.createVehicle(marca: marca, modelo: modelo, anio: anio, placa: placa);
      _ref.invalidate(vehiclesProvider);
      state = state.copyWith(isLoading: false, success: true);
      return true;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: e.toString().replaceAll('Exception: ', ''),
      );
      return false;
    }
  }

  Future<bool> updateVehicle(
    int id, {
    String? marca,
    String? modelo,
    int? anio,
    String? placa,
  }) async {
    state = state.copyWith(isLoading: true, clearError: true, success: false);
    try {
      await _repo.updateVehicle(id, marca: marca, modelo: modelo, anio: anio, placa: placa);
      _ref.invalidate(vehiclesProvider);
      state = state.copyWith(isLoading: false, success: true);
      return true;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: e.toString().replaceAll('Exception: ', ''),
      );
      return false;
    }
  }

  Future<bool> deleteVehicle(int id) async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      await _repo.deleteVehicle(id);
      _ref.invalidate(vehiclesProvider);
      state = state.copyWith(isLoading: false);
      return true;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: e.toString().replaceAll('Exception: ', ''),
      );
      return false;
    }
  }

  void clearError() => state = state.copyWith(clearError: true);
}

final vehicleFormProvider =
    StateNotifierProvider<VehicleFormNotifier, VehicleFormState>((ref) {
  return VehicleFormNotifier(ref.read(vehicleRepositoryProvider), ref);
});
