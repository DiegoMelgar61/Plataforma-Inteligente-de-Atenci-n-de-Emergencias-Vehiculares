import 'package:flutter/material.dart';
import '../core/constants.dart';
import '../data/models/models.dart';
import 'screens/splash/splash_screen.dart';
import 'screens/auth/login_screen.dart';
import 'screens/home/home_screen.dart';
import 'screens/report/report_screen.dart';
import 'screens/report/offline_report_screen.dart';
import 'screens/report/sync_screen.dart';
import 'screens/incidents/incidents_screen.dart';
import 'screens/incidents/incident_detail_screen.dart';
import 'screens/map/map_screen.dart';
import 'screens/profile/profile_screen.dart';
import 'screens/payments/my_payments_screen.dart';
import 'screens/payments/make_payment_screen.dart';
import 'screens/technician/technician_home_screen.dart';
import 'screens/chat/emergency_chat_screen.dart';

class AppRoutes {
  AppRoutes._();

  static Map<String, WidgetBuilder> get routes => {
        AppConstants.routeSplash: (_) => const SplashScreen(),
        AppConstants.routeLogin: (_) => const LoginScreen(),
        AppConstants.routeHome: (_) => const HomeScreen(),
        AppConstants.routeTechnicianHome: (_) => const TechnicianHomeScreen(),
        AppConstants.routeReport: (_) => const ReportScreen(),
        AppConstants.routeOfflineReport: (_) => const OfflineReportScreen(),
        AppConstants.routeSync: (_) => const SyncScreen(),
        AppConstants.routeIncidents: (_) => const IncidentsScreen(),
        AppConstants.routeMap: (_) => const MapScreen(),
        AppConstants.routeProfile: (_) => const ProfileScreen(),
        AppConstants.routeMyPayments: (_) => const MyPaymentsScreen(),
      };

  static Route<dynamic>? onGenerateRoute(RouteSettings settings) {
    if (settings.name == AppConstants.routeIncidentDetail) {
      final incidentId = settings.arguments as int;
      return MaterialPageRoute(
        builder: (_) => IncidentDetailScreen(incidentId: incidentId),
        settings: settings,
      );
    }
    if (settings.name == AppConstants.routeMakePayment) {
      final payment = settings.arguments as Payment;
      return MaterialPageRoute(
        builder: (_) => MakePaymentScreen(payment: payment),
        settings: settings,
      );
    }
    if (settings.name == AppConstants.routeEmergencyChat) {
      final incidentId = settings.arguments as int;
      return MaterialPageRoute(
        builder: (_) => EmergencyChatScreen(incidentId: incidentId),
        settings: settings,
      );
    }
    return null;
  }
}
