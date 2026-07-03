import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/models/payment_models.dart';
import '../../data/repositories/payments_repository.dart';
import 'core_providers.dart';

final paymentsRepositoryProvider = Provider<PaymentsRepository>((ref) {
  return PaymentsRepository(ref.watch(apiClientProvider));
});

// ── Payments ──────────────────────────────────────────────────────────────────

final myPaymentsProvider =
    FutureProvider.autoDispose<List<Payment>>((ref) async {
  return ref.read(paymentsRepositoryProvider).listarMisPagos();
});
