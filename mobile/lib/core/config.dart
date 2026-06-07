class AppConfig {
  AppConfig._();

  static const String baseUrl =
      'https://atencion-de-emergencias-vehiculares.onrender.com';

  static const String wsBaseUrl =
      'wss://atencion-de-emergencias-vehiculares.onrender.com';

  static const String tokenKey = 'auth_token';
  // Render free tier sleeps after inactivity; cold start can take 40-60s.
  static const int connectTimeout = 60000;
  static const int receiveTimeout = 60000;
}
