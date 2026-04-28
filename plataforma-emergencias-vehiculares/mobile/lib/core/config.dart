class AppConfig {
  AppConfig._();

  static const String baseUrl =
      'https://plataforma-inteligente-de-atenci-n-de-emergencia-production.up.railway.app';

  static const String wsBaseUrl =
      'wss://plataforma-inteligente-de-atenci-n-de-emergencia-production.up.railway.app';

  static const String tokenKey = 'auth_token';
  static const int connectTimeout = 30000;
  static const int receiveTimeout = 30000;
}
