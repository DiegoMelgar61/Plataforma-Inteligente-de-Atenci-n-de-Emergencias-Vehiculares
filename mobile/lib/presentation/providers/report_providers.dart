import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/repositories/incident_repository.dart';
import 'incident_providers.dart';

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
