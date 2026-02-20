import 'package:dio/dio.dart';
import 'package:frontend_mobile/core/api/api_client.dart';

class AuthService {
  final ApiClient _apiClient = ApiClient();

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
}