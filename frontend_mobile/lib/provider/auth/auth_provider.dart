import 'package:flutter/material.dart';
import 'package:frontend_mobile/data/services/auth_service.dart';
import 'package:dio/dio.dart';

import '../../data/model/category_model.dart';
import '../../data/model/user_profile.dart';

class AuthProvider extends ChangeNotifier {
  final AuthService _authService = AuthService();

  bool _isLoading = false;
  bool _isAuthenticated = false;
  bool _isInitializing = true;
  bool _isCategoriesLoading = false;
  String? _errorMessage;
  String? _email;
  UserProfile? _profile;
  List<Category> _categories = [];

  bool get isLoading => _isLoading;
  bool get isAuthenticated => _isAuthenticated;
  bool get isInitializing => _isInitializing;
  bool get isCategoriesLoading => _isCategoriesLoading;
  String? get errorMessage => _errorMessage;
  String? get email => _email;
  UserProfile? get profile => _profile;
  List<Category> get categories => _categories;

  // ─── Startup ──────────────────────────────────────────────────────
  Future<void> checkLoginStatus() async {
    final hasToken = await _authService.hasValidToken();
    if (hasToken) {
      _isAuthenticated = true;
      await fetchProfile();
      final stillHasToken = await _authService.hasValidToken();
      if (!stillHasToken) {
        _isAuthenticated = false;
      }
    }
    _isInitializing = false;
    notifyListeners();
  }

  // ─── Fetch Profile ────────────────────────────────────────────────
  Future<void> fetchProfile() async {
    try {
      final response = await _authService.getProfile();
      if (response.statusCode == 200) {
        _profile = UserProfile.fromJson(response.data);
        notifyListeners();
      }
    } catch (e) {
      debugPrint('fetchProfile error: $e');
    }
  }

  // ─── Register ─────────────────────────────────────────────────────
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

      _extractErrorMessage(response.data);
      _setLoading(false);
      return false;
    } on DioException catch (e) {
      _setLoading(false);
      if (e.response?.data != null) {
        final data = e.response!.data;
        if (data is Map) {
          final firstKey = data.keys.first;
          final messages = data[firstKey];
          if (messages is List && messages.isNotEmpty) {
            _errorMessage = messages.first.toString();
          } else {
            _errorMessage = messages.toString();
          }
        } else {
          _errorMessage = data.toString();
        }
      } else {
        _errorMessage = 'Registration failed. Please try again.';
      }
      notifyListeners();
      return false;
    } catch (e) {
      _setLoading(false);
      _errorMessage = 'Something went wrong. Please try again.';
      notifyListeners();
      return false;
    }
  }

  // ─── Login ────────────────────────────────────────────────────────
  Future<bool> login({
    required String email,
    required String password,
  }) async {
    _setLoading(true);
    _errorMessage = null;

    try {
      final response = await _authService.loginUser(
        email: email,
        password: password,
      );

      if (response.statusCode == 200) {
        final data = response.data;
        final accessToken = data['access'] as String?;
        final refreshToken = data['refresh'] as String?;

        if (accessToken == null || refreshToken == null) {
          _errorMessage = 'Login failed: tokens missing from response.';
          _setLoading(false);
          return false;
        }

        await _authService.saveTokens(
          accessToken: accessToken,
          refreshToken: refreshToken,
        );

        _isAuthenticated = true;
        _setLoading(false);

        await fetchProfile();
        return true;
      }

      if (response.statusCode == 401) {
        final data = response.data;
        _errorMessage = (data is Map)
            ? (data['detail'] ?? data['error'] ?? data['message'] ?? 'Invalid credentials.')
            : 'Invalid email or password.';
      } else {
        _errorMessage = 'Login failed. Please try again.';
      }

      _setLoading(false);
      return false;
    } catch (e, stack) {
      debugPrint('login error: $e\n$stack');
      _setLoading(false);
      _errorMessage = 'Something went wrong. Please try again.';
      return false;
    }
  }

  // ─── Logout ───────────────────────────────────────────────────────
  Future<void> logout() async {
    await _authService.clearTokens();
    _isAuthenticated = false;
    _profile = null;
    _email = null;
    _categories = [];
    notifyListeners();
  }

  // ─── OTP ──────────────────────────────────────────────────────────
  Future<void> requestOtp(String email) async {
    _setLoading(true);
    clearError();

    try {
      final success = await _authService.requestOtp(email);
      if (success) {
        _email = email;
      } else {
        _errorMessage = 'Failed to send OTP. Please try again.';
        notifyListeners();
      }
    } catch (e) {
      _errorMessage = 'Something went wrong. Please try again.';
      notifyListeners();
    } finally {
      _setLoading(false);
    }
  }

  Future<bool> verifyOtp(String otp, {String? fallbackEmail}) async {
    _email ??= fallbackEmail;

    if (_email == null) {
      _errorMessage = 'Email is missing. Please restart the process.';
      notifyListeners();
      return false;
    }

    _setLoading(true);
    _errorMessage = null;

    try {
      final response = await _authService.verifyOtp(_email!, otp);

      if (response.statusCode == 200) {
        _email = null;
        _setLoading(false);
        return true;
      }

      _errorMessage = response.data?['error']
          ?? response.data?['message']
          ?? 'Invalid OTP. Please try again.';
      _setLoading(false);
      return false;
    } catch (e, stack) {
      debugPrint('verifyOtp error: $e\n$stack');
      _setLoading(false);
      _errorMessage = 'Invalid or expired OTP. Please try again.';
      return false;
    }
  }

  // ─── Categories ───────────────────────────────────────────────────
  Future<void> fetchCategories() async {
    _isCategoriesLoading = true;
    notifyListeners();

    try {
      _categories = await _authService.getCategories();
    } catch (e) {
      debugPrint('fetchCategories error: $e');
    } finally {
      _isCategoriesLoading = false;
      notifyListeners();
    }
  }

  // ─── Helpers ──────────────────────────────────────────────────────
  void _extractErrorMessage(dynamic data) {
    if (data is Map) {
      _errorMessage = data['detail']
          ?? data['error']
          ?? data['message']
          ?? 'Something went wrong.';
    } else {
      _errorMessage = 'Something went wrong.';
    }
    notifyListeners();
  }

  void setAuthenticated(bool value) {
    _isAuthenticated = value;
    notifyListeners();
  }

  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }

  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }
}