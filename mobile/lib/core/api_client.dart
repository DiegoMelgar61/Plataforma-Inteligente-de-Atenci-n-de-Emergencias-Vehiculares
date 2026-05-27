import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'config.dart';

class ApiClient {
  static final ApiClient _instance = ApiClient._internal();
  factory ApiClient() => _instance;

  late final Dio dio;
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  /// Called when the server responds with 401. Set this in main.dart to
  /// redirect the user back to the login screen.
  void Function()? onUnauthorized;

  ApiClient._internal() {
    dio = Dio(
      BaseOptions(
        baseUrl: AppConfig.baseUrl,
        connectTimeout: const Duration(milliseconds: AppConfig.connectTimeout),
        receiveTimeout: const Duration(milliseconds: AppConfig.receiveTimeout),
        headers: {'Content-Type': 'application/json'},
      ),
    );

    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await _storage.read(key: AppConfig.tokenKey);
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          handler.next(options);
        },
        onError: (DioException e, handler) async {
          if (e.response?.statusCode == 401) {
            await _storage.delete(key: AppConfig.tokenKey);
            onUnauthorized?.call();
          }
          handler.next(e);
        },
      ),
    );
  }

  Future<String?> getToken() => _storage.read(key: AppConfig.tokenKey);

  Future<void> saveToken(String token) =>
      _storage.write(key: AppConfig.tokenKey, value: token);

  Future<void> clearToken() => _storage.delete(key: AppConfig.tokenKey);
}
