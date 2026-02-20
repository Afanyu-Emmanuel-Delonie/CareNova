import 'package:dio/dio.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ApiClient {
  static final ApiClient _instance = ApiClient._internal();
  factory ApiClient() => _instance;

  late Dio dio;
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  ApiClient._internal() {
    dio = Dio(
      BaseOptions(
        baseUrl: dotenv.env['BASE_URL'] ?? 'http://localhost:8000/api/v1/',
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 10),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        validateStatus: (status) => status != null && status < 500,
      ),
    );

    // Attach access token to every request
    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await _storage.read(key: 'access_token');
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          return handler.next(options);
        },
        onResponse: (response, handler) async {
          // If token expired, refresh and retry once
          if (response.statusCode == 401) {
            final data = response.data;
            if (data is Map && data['code'] == 'token_not_valid') {
              final refreshed = await _refreshToken();
              if (refreshed) {
                // Retry the original request with the new token
                final newToken = await _storage.read(key: 'access_token');
                response.requestOptions.headers['Authorization'] = 'Bearer $newToken';

                final retryResponse = await dio.fetch(response.requestOptions);
                return handler.resolve(retryResponse);
              } else {
                // Refresh failed — clear tokens so AuthGate sends user to login
                await _storage.delete(key: 'access_token');
                await _storage.delete(key: 'refresh_token');
              }
            }
          }
          return handler.next(response);
        },
      ),
    );

    dio.interceptors.add(LogInterceptor(
      request: true,
      requestBody: true,
      requestHeader: true,
      responseBody: true,
      responseHeader: true,
      error: true,
    ));
  }

  Future<bool> _refreshToken() async {
    try {
      final refreshToken = await _storage.read(key: 'refresh_token');
      if (refreshToken == null) return false;

      // Use a plain Dio instance (no interceptors) to avoid infinite loop
      final refreshDio = Dio(
        BaseOptions(
          baseUrl: dotenv.env['BASE_URL'] ?? 'http://localhost:8000/api/v1/',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          validateStatus: (status) => status != null && status < 500,
        ),
      );

      final response = await refreshDio.post(
        'users/token/refresh/',
        data: {'refresh': refreshToken},
      );

      if (response.statusCode == 200) {
        final newAccessToken = response.data['access'] as String?;
        if (newAccessToken != null) {
          await _storage.write(key: 'access_token', value: newAccessToken);
          return true;
        }
      }
      return false;
    } catch (e) {
      debugPrint('Token refresh error: $e');
      return false;
    }
  }

  Future<Response> get(String path) => dio.get(path);
  Future<Response> post(String path, dynamic data) => dio.post(path, data: data);
}