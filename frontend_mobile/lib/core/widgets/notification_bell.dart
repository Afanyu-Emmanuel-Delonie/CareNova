import 'package:flutter/material.dart';
import '../theme/app_colors.dart';

class NotificationBell extends StatelessWidget {
  final int badgeCount;
  final VoidCallback? onTap;

  const NotificationBell({
    super.key,
    this.badgeCount = 0,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return GestureDetector(
      onTap: onTap,
      child: Stack(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: isDarkMode
                  ? Colors.white10
                  : Colors.black.withOpacity(0.05),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(
              Icons.notifications_none_rounded,
              color: isDarkMode
                  ? AppColors.darkTextPrimary
                  : AppColors.darkBackground,
            ),
          ),
          if (badgeCount > 0)
            Positioned(
              right: 6,
              top: 6,
              child: Container(
                padding: const EdgeInsets.all(3),
                decoration: const BoxDecoration(
                  color: Color(0xFFFE0000),
                  shape: BoxShape.circle,
                ),
                constraints: const BoxConstraints(minWidth: 16, minHeight: 16),
                child: Text(
                  badgeCount > 99 ? '99+' : '$badgeCount',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 9,
                    fontWeight: FontWeight.bold,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),
            ),
          if (badgeCount == 0)
            Positioned(
              right: 10,
              top: 10,
              child: Container(
                height: 8,
                width: 8,
                decoration: const BoxDecoration(
                  color: Color(0xFFFE0000),
                  shape: BoxShape.circle,
                ),
              ),
            ),
        ],
      ),
    );
  }
}