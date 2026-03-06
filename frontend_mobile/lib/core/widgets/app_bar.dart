import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../theme/app_colors.dart';
import 'notification_bell.dart';

class AppBarWidget extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final bool showNotification;
  final int notificationCount;
  final VoidCallback? onNotificationTap;
  final bool showBackButton;
  final List<Widget>? actions;
  final bool centerTitle;

  const AppBarWidget({
    super.key,
    required this.title,
    this.showNotification = true,
    this.notificationCount = 0,
    this.onNotificationTap,
    this.showBackButton = false,
    this.actions,
    this.centerTitle = false,
  });

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return AppBar(
      backgroundColor:
      isDarkMode ? AppColors.darkBackground : AppColors.lightBackground,
      elevation: 0,
      centerTitle: true,
      automaticallyImplyLeading: showBackButton,
      leading: showBackButton
          ? IconButton(
        icon: Icon(
          Icons.arrow_back,
          color: isDarkMode
              ? AppColors.darkTextPrimary
              : AppColors.lightTextPrimary,
        ),
        onPressed: () => Navigator.pop(context),
      )
          : null,
      title: Text(
        title,
        style: GoogleFonts.inter(
          fontSize: 16,
          fontWeight: FontWeight.w500,
          color: isDarkMode
              ? AppColors.darkTextPrimary
              : AppColors.lightTextPrimary,
        ),
      ),
      actions: [
        if (showNotification)
          Padding(
            padding: const EdgeInsets.only(right: 16),
            child: NotificationBell(
              badgeCount: notificationCount,
              onTap: onNotificationTap,
            ),
          ),
        if (actions != null) ...actions!,
      ],
    );

  }
}