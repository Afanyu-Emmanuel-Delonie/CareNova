import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/validators/auth_validators.dart';
import '../../../core/widgets/app_text_field.dart';
import '../../../provider/auth/auth_provider.dart';
import 'otp_screen.dart';

class RegisterScreen extends StatefulWidget {
  final VoidCallback onLoginTap;
  const RegisterScreen({super.key, required this.onLoginTap});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  // Registration Logic
  Future<void> _onSubmit() async {
    if (!_formKey.currentState!.validate()) return;

    final auth = context.read<AuthProvider>();

    final success = await auth.register(
      name: _nameController.text.trim(),
      email: _emailController.text.trim(),
      password: _passwordController.text.trim(),
    );

    if (success) {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => OtpScreen(email: _emailController.text.trim()),
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(auth.errorMessage ?? 'Registration failed'),
          backgroundColor: AppColors.error,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final bgColor = isDarkMode ? AppColors.darkBackground : AppColors.lightBackground;

    return Scaffold(
      backgroundColor: bgColor,
      body: SafeArea(
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const SizedBox(height: 60),

              Image.asset(
                isDarkMode
                    ? 'assets/app_images/carenova-icon-dark.png'
                    : 'assets/app_images/carenova-icon-light.png',
                width: 80,
              ),

              const SizedBox(height: 16),

              Text(
                'Create Account',
                style: GoogleFonts.inter(
                  fontSize: 25,
                  fontWeight: FontWeight.bold,
                  color: isDarkMode ? AppColors.darkTextPrimary : AppColors.lightTextPrimary,
                ),
              ),

              const SizedBox(height: 8),

              Text(
                'Join CareNova today',
                style: GoogleFonts.inter(
                  fontSize: 14,
                  color: isDarkMode ? AppColors.darkTextSecondary : AppColors.lightTextSecondary,
                ),
              ),

              const SizedBox(height: 40),

              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20),
                child: Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [

                      _label('Full Name', isDarkMode),
                      const SizedBox(height: 8),
                      AppTextField(
                        hint: 'John Doe',
                        prefixIcon: Icons.person_outline,
                        controller: _nameController,
                        validator: AuthValidators.validateFullName,
                      ),

                      const SizedBox(height: 16),

                      _label('Email Address', isDarkMode),
                      const SizedBox(height: 8),
                      AppTextField(
                        hint: 'you@example.com',
                        prefixIcon: Icons.email_outlined,
                        keyboardType: TextInputType.emailAddress,
                        controller: _emailController,
                        validator: AuthValidators.validateEmail,
                      ),

                      const SizedBox(height: 16),

                      _label('Password', isDarkMode),
                      const SizedBox(height: 8),
                      AppTextField(
                        hint: 'Min. 8 characters',
                        prefixIcon: Icons.lock_outline,
                        isPassword: true,
                        controller: _passwordController,
                        validator: AuthValidators.validatePassword,
                      ),

                      const SizedBox(height: 16),

                      _label('Confirm Password', isDarkMode),
                      const SizedBox(height: 8),
                      AppTextField(
                        hint: 'Re-enter your password',
                        prefixIcon: Icons.lock_outline,
                        isPassword: true,
                        controller: _confirmPasswordController,
                        validator: (value) => AuthValidators.validateConfirmPassword(
                          value,
                          _passwordController.text,
                        ),
                      ),

                      const SizedBox(height: 32),

                      // ✅ Button calls _onSubmit with registration logic
                      ElevatedButton(
                        onPressed: _onSubmit,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppColors.indigoPrimary,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                        child: Text(
                          'Create Account',
                          style: GoogleFonts.inter(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),

                      const SizedBox(height: 24),

                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            'Already have an account? ',
                            style: GoogleFonts.inter(
                              color: isDarkMode
                                  ? AppColors.darkTextSecondary
                                  : AppColors.lightTextSecondary,
                            ),
                          ),
                          // ✅ Login tap just toggles back via AuthGate
                          GestureDetector(
                            onTap: widget.onLoginTap,
                            child: Text(
                              'Login',
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

                      const SizedBox(height: 40),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _label(String text, bool isDarkMode) {
    return Text(
      text,
      style: GoogleFonts.inter(
        color: isDarkMode ? AppColors.darkTextSecondary : AppColors.lightTextSecondary,
        fontSize: 16,
        fontWeight: FontWeight.w400,
      ),
    );
  }
}