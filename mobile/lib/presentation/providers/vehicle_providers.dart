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
