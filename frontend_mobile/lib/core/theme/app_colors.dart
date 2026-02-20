import 'package:flutter/material.dart';

class AppColors {
  // --- BRAND CORE ---
  static const Color indigoPrimary = Color(0xFF4B0082);
  static const Color creamSecondary = Color(0xFFFDF5E6);

  // --- LIGHT MODE PALETTE ---
  static const Color lightBackground = Colors.white;
  static const Color lightSurface = Colors.white;
  static const Color lightTextPrimary = Color(0xFF1A0033);
  static const Color lightTextSecondary = Color(0xFF6B5B7B);

  // --- DARK MODE PALETTE ---
  static const Color darkBackground = Color(0xFF121212);
  static const Color darkSurface = Color(0xFF1E1E1E);
  static const Color darkTextPrimary = Color(0xFFFDF5E6);
  static const Color darkTextSecondary = Color(0xFFBDBDBD);

  // --- FUNCTIONAL / STATUS COLORS ---
  static const Color success = Color(0xFF2D6A4F);
  static const Color error = Color(0xFF9B2226);
  static const Color warning = Color(0xFFE9AE0B);

  // --- UTILITY METHODS ---
  static Color indigoWithOpacity(double opacity) => indigoPrimary.withOpacity(opacity);
}
