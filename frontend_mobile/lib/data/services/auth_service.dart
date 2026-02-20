import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:frontend_mobile/core/api/api_client.dart';

class AuthService {
  final ApiClient _apiClient = ApiClient();
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  // ─── Token Storage ────────────────────────────────────────────────
  Future<void> saveTokens({
    required String accessToken,
    required String refreshToken,
  }) async {
    await _storage.write(key: 'access_token', value: accessToken);
    await _storage.write(key: 'refresh_token', value: refreshToken);
  }

  Future<String?> getAccessToken() => _storage.read(key: 'access_token');
  Future<String?> getRefreshToken() => _storage.read(key: 'refresh_token');

  Future<void> clearTokens() async {
    await _storage.delete(key: 'access_token');
    await _storage.delete(key: 'refresh_token');
  }

  Future<bool> hasValidToken() async {
    final token = await getAccessToken();
    return token != null && token.isNotEmpty;
  }

  // ─── Auth Endpoints ───────────────────────────────────────────────
  Future<bool> requestOtp(String email) async {
    try {
      final response = await _apiClient.post('users/request-otp/', {'email': email});
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  Future<Response> verifyOtp(String email, String otp) async {
    return await _apiClient.post('users/verify-otp/', {'email': email, 'otp': otp});
  }

  Future<Response> registerUser({
    required String name,
    required String email,
    required String password,
  }) async {
    return await _apiClient.post(
      'users/register/',
      {
        'name': name,
        'email': email,
        'password': password,
        'role': 'PATIENT',
      },
    );
  }

  Future<Response> loginUser({
    required String email,
    required String password,
  }) async {
    return await _apiClient.post(
      'users/login/',
      {
        'email': email,
        'password': password,
      },
    );
  }

  Future<Response> getProfile() async {
    return await _apiClient.get('users/me/');
  }
}