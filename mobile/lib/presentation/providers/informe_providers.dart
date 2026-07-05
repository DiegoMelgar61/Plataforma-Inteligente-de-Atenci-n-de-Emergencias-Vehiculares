import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/models/informe_models.dart';
import '../../data/repositories/informe_repository.dart';
import 'core_providers.dart';

final informeRepositoryProvider = Provider<InformeRepository>((ref) {
  return InformeRepository(ref.watch(apiClientProvider));
});

final informeServicioProvider = FutureProvider.autoDispose
    .family<InformeServicio?, int>((ref, idIncidente) async {
  return ref.read(informeRepositoryProvider).getInforme(idIncidente);
});
