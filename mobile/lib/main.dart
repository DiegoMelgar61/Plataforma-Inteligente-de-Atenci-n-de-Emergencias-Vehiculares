import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/api_client.dart';
import 'core/constants.dart';
import 'presentation/providers/providers.dart';
import 'presentation/routes.dart';

/// Navigator key for global navigation (used by the 401 interceptor to
/// redirect back to login without needing a BuildContext).
final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();

void main() {
  WidgetsFlutterBinding.ensureInitialized();

  // Wire up the 401 → redirect to login callback on the singleton client.
  ApiClient().onUnauthorized = () {
    navigatorKey.currentState?.pushNamedAndRemoveUntil(
      AppConstants.routeLogin,
      (route) => false,
    );
  };

  runApp(
    const ProviderScope(
      child: PlataformaEmergenciasApp(),
    ),
  );
}

class PlataformaEmergenciasApp extends ConsumerWidget {
  const PlataformaEmergenciasApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    ref.listen<AsyncValue<bool>>(connectivityProvider, (previous, next) {
      next.whenData((online) async {
        if (!online || previous?.value == true) return;

        final pendientes = await ref.read(pendientesCountProvider.future);
        if (pendientes > 0) {
          await ref.read(sincronizacionProvider.notifier).sincronizarPendientes();
        }
      });
    });

    return MaterialApp(
      title: 'Emergencias Vehiculares',
      navigatorKey: navigatorKey,
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFFE53935),
          brightness: Brightness.light,
        ),
        inputDecorationTheme: const InputDecorationTheme(
          filled: true,
          border: OutlineInputBorder(),
        ),
        cardTheme: const CardThemeData(
          elevation: 1,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.all(Radius.circular(12)),
          ),
        ),
      ),
      darkTheme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFFE53935),
          brightness: Brightness.dark,
        ),
        inputDecorationTheme: const InputDecorationTheme(
          filled: true,
          border: OutlineInputBorder(),
        ),
        cardTheme: const CardThemeData(
          elevation: 1,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.all(Radius.circular(12)),
          ),
        ),
      ),
      themeMode: ThemeMode.system,
      initialRoute: AppConstants.routeSplash,
      routes: AppRoutes.routes,
      onGenerateRoute: AppRoutes.onGenerateRoute,
    );
  }
}
