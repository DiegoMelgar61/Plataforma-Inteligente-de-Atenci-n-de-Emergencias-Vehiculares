class AppConstants {
  AppConstants._();

  // Roles
  static const String roleAdmin = 'admin';
  static const String roleTaller = 'taller';
  static const String roleCliente = 'cliente';

  // Incident status
  static const String statusPendiente = 'pendiente';
  static const String statusAsignado = 'asignado';
  static const String statusEnProceso = 'en_proceso';
  static const String statusResuelto = 'resuelto';
  static const String statusCancelado = 'cancelado';

  // Roles
  static const String roleTecnico = 'TECNICO';

  // Named routes
  static const String routeSplash = '/';
  static const String routeLogin = '/login';
  static const String routeHome = '/home';
  static const String routeTechnicianHome = '/technician-home';
  static const String routeReport = '/report';
  static const String routeOfflineReport = '/offline-report';
  static const String routeSync = '/sync';
  static const String routeIncidents = '/incidents';
  static const String routeIncidentDetail = '/incident-detail';
  static const String routeMap = '/map';
  static const String routeProfile = '/profile';
  static const String routeMyPayments = '/my-payments';
  static const String routeMakePayment = '/make-payment';
  static const String routeEmergencyChat = '/emergency-chat';
}
