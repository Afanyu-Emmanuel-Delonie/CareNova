import 'package:flutter/material.dart';
import 'package:frontend_mobile/provider/auth/auth_provider.dart';
import 'package:frontend_mobile/ui/views/auth/register_screen.dart';
import 'package:frontend_mobile/ui/views/dashboard/dashboard.dart';
import 'package:provider/provider.dart';

import 'LoginScreen.dart';

class AuthGate extends StatefulWidget {
  const AuthGate({super.key});

  @override
  State<AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<AuthGate> {
  bool _showLogin = true;

  void _toggleView() => setState(() => _showLogin = !_showLogin);

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();

    if (auth.isInitializing) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    if (auth.isAuthenticated) {
      return const DashboardScreen();
    }

    return _showLogin
        ? LoginScreen(onRegisterTap: _toggleView)
        : RegisterScreen(onLoginTap: _toggleView);
  }
}