import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/models/auth_models.dart';
import '../../data/repositories/auth_repository.dart';
import 'core_providers.dart';
import 'incident_providers.dart';
import 'vehicle_providers.dart';
import 'technician_providers.dart';

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository(ref.watch(apiClientProvider));
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

  Future<bool> register({
    required String email,
    required String password,
    required String fullName,
    String? phone,
  }) async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      await _repo.register(
          email: email, password: password, fullName: fullName, phone: phone);
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
