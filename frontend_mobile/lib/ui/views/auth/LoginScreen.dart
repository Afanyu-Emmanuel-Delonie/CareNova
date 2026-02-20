import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/validators/auth_validators.dart';
import '../../../core/widgets/app_text_field.dart';
import '../../../provider/auth/auth_provider.dart';

class LoginScreen extends StatefulWidget {
  final VoidCallback onRegisterTap;
  const LoginScreen({super.key, required this.onRegisterTap});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _onSubmit() async {
    if (!_formKey.currentState!.validate()) return;

    final auth = context.read<AuthProvider>();

    final success = await auth.login(
      email: _emailController.text.trim(),
      password: _passwordController.text.trim(),
    );

    if (!mounted) return;

    if (!success) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Row(
            children: [
              const Icon(Icons.error_outline, color: Colors.white),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  auth.errorMessage ?? 'Login failed. Please try again.',
                  style: GoogleFonts.inter(color: Colors.white),
                ),
              ),
            ],
          ),
          backgroundColor: Colors.red.shade600,
          behavior: SnackBarBehavior.floating,
          margin: const EdgeInsets.all(16),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          duration: const Duration(seconds: 3),
        ),
      );
    }
    // On success: AuthGate watches isAuthenticated and automatically
    // switches to DashboardScreen — no manual navigation needed.
  }

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      backgroundColor: isDarkMode ? AppColors.lightTextPrimary : AppColors.indigoPrimary,
      body: SafeArea(
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const SizedBox(height: 100),

              Image.asset(
                'assets/app_images/carenova-icon.png',
                width: 100,
              ),

              const SizedBox(height: 20),

              Text(
                'Welcome Back, Login.',
                style: GoogleFonts.inter(
                  fontSize: 25,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),

              const SizedBox(height: 40),

              ConstrainedBox(
                constraints: BoxConstraints(
                  minHeight: MediaQuery.of(context).size.height * 0.65,
                ),
                child: Container(
                  width: double.infinity,
                  decoration: BoxDecoration(
                    color: isDarkMode
                        ? AppColors.darkBackground
                        : AppColors.lightBackground,
                    borderRadius: const BorderRadius.only(
                      topLeft: Radius.circular(30),
                      topRight: Radius.circular(30),
                    ),
                  ),
                  padding:
                  const EdgeInsets.symmetric(horizontal: 20, vertical: 30),
                  child: Form(
                    key: _formKey,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        const SizedBox(height: 20),

                        Text(
                          'Email Address',
                          style: GoogleFonts.inter(
                            color: isDarkMode
                                ? AppColors.darkTextSecondary
                                : AppColors.lightTextSecondary,
                            fontSize: 16,
                            fontWeight: FontWeight.w400,
                          ),
                        ),

                        const SizedBox(height: 8),

                        AppTextField(
                          hint: 'you@example.com',
                          prefixIcon: Icons.email_outlined,
                          keyboardType: TextInputType.emailAddress,
                          controller: _emailController,
                          validator: AuthValidators.validateEmail,
                        ),

                        const SizedBox(height: 16),

                        Text(
                          'Password',
                          style: GoogleFonts.inter(
                            color: isDarkMode
                                ? AppColors.darkTextSecondary
                                : AppColors.lightTextSecondary,
                            fontSize: 16,
                            fontWeight: FontWeight.w400,
                          ),
                        ),

                        const SizedBox(height: 8),

                        AppTextField(
                          hint: 'Enter your password',
                          prefixIcon: Icons.lock_outline,
                          isPassword: true,
                          controller: _passwordController,
                          validator: AuthValidators.validatePassword,
                        ),

                        const SizedBox(height: 8),

                        Align(
                          alignment: Alignment.centerRight,
                          child: TextButton(
                            onPressed: () {
                              // TODO: implement forgot password
                            },
                            child: Text(
                              'Forgot Password?',
                              style: GoogleFonts.inter(
                                color: isDarkMode
                                    ? AppColors.darkTextSecondary
                                    : AppColors.lightTextSecondary,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ),
                        ),

                        const SizedBox(height: 24),

                        Consumer<AuthProvider>(
                          builder: (context, auth, _) {
                            return ElevatedButton(
                              onPressed: auth.isLoading ? null : _onSubmit,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: AppColors.indigoPrimary,
                                foregroundColor: Colors.white,
                                disabledBackgroundColor:
                                AppColors.indigoPrimary.withOpacity(0.6),
                                padding:
                                const EdgeInsets.symmetric(vertical: 16),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(12),
                                ),
                              ),
                              child: auth.isLoading
                                  ? const SizedBox(
                                height: 20,
                                width: 20,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2.5,
                                  color: Colors.white,
                                ),
                              )
                                  : Text(
                                'Login',
                                style: GoogleFonts.inter(
                                  fontSize: 16,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            );
                          },
                        ),

                        const SizedBox(height: 40),

                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(
                              "Don't have an account? ",
                              style: GoogleFonts.inter(
                                color: isDarkMode
                                    ? AppColors.darkTextSecondary
                                    : AppColors.lightTextSecondary,
                              ),
                            ),
                            GestureDetector(
                              onTap: widget.onRegisterTap,
                              child: Text(
                                'Sign Up',
                                style: GoogleFonts.inter(
                                  color: isDarkMode
                                      ? AppColors.indigoPrimary
                                      : AppColors.lightTextPrimary,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}