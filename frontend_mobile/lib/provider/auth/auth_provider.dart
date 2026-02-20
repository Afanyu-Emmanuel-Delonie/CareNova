import 'package:flutter/material.dart';
import 'package:frontend_mobile/data/services/auth_service.dart';

class AuthProvider extends ChangeNotifier {
  final AuthService _authService = AuthService();

  bool _isLoading = false;
  bool _isAuthenticated = false;
  bool _isInitializing = true;
  String? _errorMessage;
  String? _email;

  bool get isLoading => _isLoading;
  bool get isAuthenticated => _isAuthenticated;
  bool get isInitializing => _isInitializing;
  String? get errorMessage => _errorMessage;
  String? get email => _email;

  // Called on app startup to check for existing token
  Future<void> checkLoginStatus() async {
    // TODO: use flutter_secure_storage to check for JWT token
    await Future.delayed(const Duration(seconds: 1));
    _isInitializing = false;
    notifyListeners();
  }

  Future<bool> register({
    required String name,
    required String email,
    required String password,
  }) async {
    _setLoading(true);
    _errorMessage = null;

    try {
      final response = await _authService.registerUser(
        name: name,
        email: email,
        password: password,
      );

      if (response.statusCode == 201 || response.statusCode == 200) {
        _email = email;
        _setLoading(false);
        return true;
      }
      _setLoading(false);
      return false;
    } catch (e) {
      _setLoading(false);
      _errorMessage = "Email already in use or server error.";
      return false;
    }
  }

  Future<void> requestOtp(String email) async {
    _setLoading(true);
    clearError();

    try {
      final success = await _authService.requestOtp(email);
      if (success) {
        _email = email;
      } else {
        _errorMessage = 'Failed to send OTP. Please try again.';
      }
    } catch (e) {
      _errorMessage = 'Something went wrong. Please try again.';
    } finally {
      _setLoading(false);
    }
  }

  Future<void> verifyOtp(String otp) async {
    if (_email == null) {
      _errorMessage = 'Email is missing. Please restart the process.';
      notifyListeners();
      return;
    }

    _setLoading(true);
    clearError();

    try {
      final response = await _authService.verifyOtp(_email!, otp);
      if (response.statusCode == 200) {
        _email = null;
        _isAuthenticated = true;
      } else {
        _errorMessage = 'Invalid OTP. Please try again.';
      }
    } catch (e) {
      _errorMessage = 'Something went wrong. Please try again.';
    } finally {
      _setLoading(false);
    }
  }

  void setAuthenticated(bool value) {
    _isAuthenticated = value;
    notifyListeners();
  }

  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }

  // Private — only used internally
  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }
}