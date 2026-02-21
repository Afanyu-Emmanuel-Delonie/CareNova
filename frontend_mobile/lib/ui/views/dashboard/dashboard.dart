import 'dart:async';

import 'package:flutter/material.dart';
import 'package:frontend_mobile/ui/views/dashboard/view_model/dashboard_viewmodel.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/widgets/doctor_card.dart';
import '../../../core/widgets/news_section.dart';
import '../../../data/model/appointment_model.dart';
import '../../../data/model/category_model.dart';
import '../../../data/model/doctor_model.dart';
import '../../../provider/appointments/appointment_provider.dart';
import '../../../provider/auth/auth_provider.dart';
import '../../../provider/auth/doctor_provider.dart';
import '../../../provider/news/news_provider.dart';


class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  int? _selectedCategoryId;
  final TextEditingController _searchController = TextEditingController();
  Timer? _searchDebounce;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final profile = context.read<AuthProvider>().profile;
      context.read<AuthProvider>().fetchCategories();
      context.read<DoctorProvider>().loadDoctors(minRating: 4.0);
      if (DashboardViewModel.isPatient(profile?.role)) {
        context.read<AppointmentProvider>().loadAppointments();
      }
      context.read<NewsProvider>().loadNews();
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    _searchDebounce?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final authProvider = context.watch<AuthProvider>();
    final doctorProvider = context.watch<DoctorProvider>();
    final appointmentProvider = context.watch<AppointmentProvider>();

    final profile = authProvider.profile;
    final isPatient = DashboardViewModel.isPatient(profile?.role);
    final categories = authProvider.categories;
    final isCategoriesLoading = authProvider.isCategoriesLoading;

    // Enriched appointments with doctor info
    final enrichedAppointments = DashboardViewModel.enrichAppointments(
      appointmentProvider.upcomingAppointments,
      doctorProvider.doctors,
    );

    return Scaffold(
      backgroundColor:
      isDarkMode ? AppColors.darkBackground : AppColors.lightBackground,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 24),
              _buildHeader(isDarkMode, profile),
              const SizedBox(height: 32),
              _buildSearchBar(isDarkMode),
              const SizedBox(height: 20),

              // ─── Appointments (patients only) ─────────────────
              if (isPatient) ...[
                _buildSectionHeader(
                  isDarkMode,
                  title: 'Upcoming Appointments',
                  onSeeAll: () {},
                ),
                const SizedBox(height: 10),
                _buildUpcomingAppointmentCard(
                  isDarkMode,
                  appointmentProvider,
                  enrichedAppointments,
                ),
                const SizedBox(height: 20),
              ],

              // ─── Categories ───────────────────────────────────
              _buildSectionTitle(isDarkMode, 'Categories'),
              const SizedBox(height: 10),
              _buildCategorySection(isDarkMode, categories, isCategoriesLoading),


              // ─── Top Doctors ──────────────────────────────────
              _buildSectionHeader(
                isDarkMode,
                title: 'Top Doctors',
                onSeeAll: () {},
              ),
              const SizedBox(height: 10),
              _buildDoctorsSection(isDarkMode, doctorProvider),

              const SizedBox(height: 20),

              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const NewsSection(),
                ]
              ),

              const SizedBox(height: 50),
            ],
          ),
        ),
      ),
    );
  }



  // ─────────────────────────────────────────────────────────
  // Section Helpers
  // ─────────────────────────────────────────────────────────

  Widget _buildSectionHeader(
      bool isDarkMode, {
        required String title,
        required VoidCallback onSeeAll,
      }) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        _buildSectionTitle(isDarkMode, title),
        TextButton(
          onPressed: onSeeAll,
          child: Text(
            'See All',
            style: GoogleFonts.inter(
              fontSize: 14,
              fontWeight: FontWeight.w500,
              color: isDarkMode
                  ? AppColors.darkTextSecondary
                  : AppColors.lightTextSecondary,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSectionTitle(bool isDarkMode, String title) {
    return Text(
      title,
      style: GoogleFonts.inter(
        fontSize: 18,
        fontWeight: FontWeight.w600,
        color: isDarkMode
            ? AppColors.darkTextPrimary
            : AppColors.lightTextPrimary,
      ),
    );
  }

  // ─────────────────────────────────────────────────────────
  // Header
  // ─────────────────────────────────────────────────────────

  Widget _buildHeader(bool isDarkMode, dynamic profile) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Row(
          children: [
            CircleAvatar(
              radius: 24,
              backgroundImage: profile?.profilePicture != null &&
                  profile!.profilePicture!.isNotEmpty
                  ? NetworkImage(profile.profilePicture!) as ImageProvider
                  : const AssetImage('assets/app_images/profile_avatar.png'),
            ),
            const SizedBox(width: 10),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Welcome back!',
                  style: GoogleFonts.inter(
                    fontSize: 14,
                    color: isDarkMode
                        ? AppColors.darkTextSecondary
                        : AppColors.lightTextSecondary,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  profile?.fullName ?? 'Loading...',
                  style: GoogleFonts.inter(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: isDarkMode
                        ? AppColors.darkTextPrimary
                        : AppColors.indigoPrimary,
                  ),
                ),
              ],
            ),
          ],
        ),
        _buildNotificationBell(isDarkMode),
      ],
    );
  }

  // ─────────────────────────────────────────────────────────
  // Search Bar
  // ─────────────────────────────────────────────────────────

  Widget _buildSearchBar(bool isDarkMode) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: isDarkMode ? AppColors.darkSurface : AppColors.lightSurface,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: [
          Padding(
            padding: const EdgeInsets.only(left: 10.0),
            child: Icon(
              Icons.search,
              color: isDarkMode
                  ? AppColors.darkTextSecondary
                  : AppColors.lightTextSecondary,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: TextField(
              controller: _searchController,
              style: GoogleFonts.inter(
                color: isDarkMode
                    ? AppColors.darkTextPrimary
                    : AppColors.lightTextPrimary,
              ),
              decoration: InputDecoration(
                hintText: 'Search doctors...',
                hintStyle: GoogleFonts.inter(
                  color: isDarkMode
                      ? AppColors.darkTextSecondary
                      : AppColors.lightTextSecondary,
                ),
                border: InputBorder.none,
                focusedBorder: InputBorder.none,
                enabledBorder: InputBorder.none,
              ),
              onChanged: (value) {
                // Debounce — wait 500ms after user stops typing
                _searchDebounce?.cancel();
                _searchDebounce = Timer(const Duration(milliseconds: 500), () {
                  if (value.isEmpty) {
                    context.read<DoctorProvider>().loadDoctors(
                      minRating: 4.0,
                      isRefresh: true,
                    );
                  } else {
                    context.read<DoctorProvider>().search(value.trim());
                  }
                });
              },
            ),
          ),
          // Clear button when text is present
          ValueListenableBuilder<TextEditingValue>(
            valueListenable: _searchController,
            builder: (context, value, _) {
              if (value.text.isEmpty) return const SizedBox.shrink();
              return IconButton(
                icon: Icon(
                  Icons.close_rounded,
                  color: isDarkMode
                      ? AppColors.darkTextSecondary
                      : AppColors.lightTextSecondary,
                  size: 18,
                ),
                onPressed: () {
                  _searchController.clear();
                  context.read<DoctorProvider>().loadDoctors(
                    minRating: 4.0,
                    isRefresh: true,
                  );
                },
              );
            },
          ),
          Container(
            decoration: BoxDecoration(
              color: isDarkMode
                  ? const Color(0xFFd3a1f7)
                  : AppColors.indigoPrimary,
              borderRadius: BorderRadius.circular(12),
            ),
            child: IconButton(
              constraints: const BoxConstraints(),
              padding: const EdgeInsets.all(8),
              icon: Icon(
                Icons.tune_rounded,
                color: isDarkMode ? AppColors.indigoPrimary : Colors.white,
                size: 20,
              ),
              onPressed: () => _showFilterSheet(context, isDarkMode),
            ),
          ),
        ],
      ),
    );
  }

  void _showFilterSheet(BuildContext context, bool isDarkMode) {
    final provider = context.read<DoctorProvider>();

    // Local state inside sheet
    double selectedRating = provider.currentMinRating ?? 0.0;
    String? selectedSpecialization = provider.currentSpecialization;

    final specializations = [
      'Cardiology',
      'Dermatology',
      'Neurology',
      'Pediatrics',
      'Orthopedics',
      'Gynecology',
      'Psychiatry',
      'General Medicine',
    ];

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setSheetState) {
            return Container(
              padding: const EdgeInsets.fromLTRB(24, 16, 24, 32),
              decoration: BoxDecoration(
                color:
                isDarkMode ? AppColors.darkSurface : AppColors.lightSurface,
                borderRadius:
                const BorderRadius.vertical(top: Radius.circular(24)),
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // ── Handle ──
                  Center(
                    child: Container(
                      width: 40,
                      height: 4,
                      decoration: BoxDecoration(
                        color: isDarkMode
                            ? Colors.white24
                            : Colors.black.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                  ),

                  const SizedBox(height: 20),

                  // ── Title ──
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Filter Doctors',
                        style: GoogleFonts.inter(
                          fontSize: 18,
                          fontWeight: FontWeight.w600,
                          color: isDarkMode
                              ? AppColors.darkTextPrimary
                              : AppColors.lightTextPrimary,
                        ),
                      ),
                      TextButton(
                        onPressed: () {
                          setSheetState(() {
                            selectedRating = 0.0;
                            selectedSpecialization = null;
                          });
                        },
                        child: Text(
                          'Reset',
                          style: GoogleFonts.inter(
                            color: AppColors.indigoPrimary,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 24),

                  // ── Min Rating ──
                  Text(
                    'Minimum Rating',
                    style: GoogleFonts.inter(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: isDarkMode
                          ? AppColors.darkTextPrimary
                          : AppColors.lightTextPrimary,
                    ),
                  ),

                  const SizedBox(height: 8),

                  Row(
                    children: [
                      Expanded(
                        child: SliderTheme(
                          data: SliderTheme.of(context).copyWith(
                            activeTrackColor: AppColors.indigoPrimary,
                            inactiveTrackColor:
                            AppColors.indigoPrimary.withOpacity(0.2),
                            thumbColor: AppColors.indigoPrimary,
                            overlayColor:
                            AppColors.indigoPrimary.withOpacity(0.1),
                          ),
                          child: Slider(
                            value: selectedRating,
                            min: 0.0,
                            max: 5.0,
                            divisions: 10,
                            onChanged: (value) {
                              setSheetState(() => selectedRating = value);
                            },
                          ),
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: AppColors.indigoPrimary.withOpacity(0.12),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          selectedRating == 0.0
                              ? 'Any'
                              : '${selectedRating.toStringAsFixed(1)}+',
                          style: GoogleFonts.inter(
                            fontSize: 13,
                            fontWeight: FontWeight.w600,
                            color: AppColors.indigoPrimary,
                          ),
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 20),

                  // ── Specialization ──
                  Text(
                    'Specialization',
                    style: GoogleFonts.inter(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: isDarkMode
                          ? AppColors.darkTextPrimary
                          : AppColors.lightTextPrimary,
                    ),
                  ),

                  const SizedBox(height: 10),

                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: specializations.map((spec) {
                      final isSelected = selectedSpecialization == spec;
                      return GestureDetector(
                        onTap: () {
                          setSheetState(() {
                            selectedSpecialization =
                            isSelected ? null : spec;
                          });
                        },
                        child: AnimatedContainer(
                          duration: const Duration(milliseconds: 150),
                          padding: const EdgeInsets.symmetric(
                              horizontal: 14, vertical: 8),
                          decoration: BoxDecoration(
                            color: isSelected
                                ? AppColors.indigoPrimary
                                : AppColors.indigoPrimary.withOpacity(0.08),
                            borderRadius: BorderRadius.circular(20),
                            border: Border.all(
                              color: isSelected
                                  ? AppColors.indigoPrimary
                                  : Colors.transparent,
                            ),
                          ),
                          child: Text(
                            spec,
                            style: GoogleFonts.inter(
                              fontSize: 13,
                              fontWeight: FontWeight.w500,
                              color: isSelected
                                  ? Colors.white
                                  : isDarkMode
                                  ? AppColors.darkTextSecondary
                                  : AppColors.lightTextSecondary,
                            ),
                          ),
                        ),
                      );
                    }).toList(),
                  ),

                  const SizedBox(height: 28),

                  // ── Apply Button ──
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.indigoPrimary,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(14),
                        ),
                      ),
                      onPressed: () {
                        Navigator.pop(context);
                        context.read<DoctorProvider>().applyFilters(
                          specialization: selectedSpecialization,
                          minRating: selectedRating == 0.0
                              ? null
                              : selectedRating,
                        );
                      },
                      child: Text(
                        'Apply Filters',
                        style: GoogleFonts.inter(
                          fontSize: 15,
                          fontWeight: FontWeight.w600,
                          color: Colors.white,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            );
          },
        );
      },
    );
  }

  // ─────────────────────────────────────────────────────────
  // Notification Bell
  // ─────────────────────────────────────────────────────────

  Widget _buildNotificationBell(bool isDarkMode) {
    return Stack(
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
    );
  }

  // ─────────────────────────────────────────────────────────
  // Doctors Section
  // ─────────────────────────────────────────────────────────

  Widget _buildDoctorsSection(bool isDarkMode, DoctorProvider provider) {
    if (provider.isLoading && provider.doctors.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }

    if (provider.error != null && provider.doctors.isEmpty) {
      return Center(
        child: Column(
          children: [
            Text(
              provider.error!,
              style: GoogleFonts.inter(
                color: isDarkMode
                    ? AppColors.darkTextSecondary
                    : AppColors.lightTextSecondary,
              ),
            ),
            const SizedBox(height: 8),
            ElevatedButton(
              onPressed: () =>
                  context.read<DoctorProvider>().loadDoctors(isRefresh: true),
              child: const Text('Retry'),
            ),
          ],
        ),
      );
    }

    if (provider.doctors.isEmpty) {
      return Center(
        child: Text(
          'No doctors available',
          style: GoogleFonts.inter(
            color: isDarkMode
                ? AppColors.darkTextSecondary
                : AppColors.lightTextSecondary,
          ),
        ),
      );
    }

    final topDoctors = provider.doctors.take(6).toList();

    return SizedBox(
      height: 255,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        itemCount: topDoctors.length,
        itemBuilder: (context, index) {
          return SizedBox(
            width: 230,
            child: Padding(
              padding: EdgeInsets.only(
                right: index == topDoctors.length - 1 ? 0 : 12,
              ),
              child: DoctorCard(
                doctor: topDoctors[index],
                onTap: () {},
              ),
            ),
          );
        },
      ),
    );
  }

  // ─────────────────────────────────────────────────────────
  // Appointments Section
  // ─────────────────────────────────────────────────────────

  Widget _buildUpcomingAppointmentCard(
      bool isDarkMode,
      AppointmentProvider provider,
      List<Appointment> enrichedAppointments,
      ) {
    if (provider.isLoading) {
      return const SizedBox(
        height: 180,
        child: Center(child: CircularProgressIndicator()),
      );
    }

    if (enrichedAppointments.isEmpty) {
      return Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          color: isDarkMode ? AppColors.darkSurface : AppColors.lightSurface,
        ),
        child: Center(
          child: Text(
            'No upcoming appointments',
            style: GoogleFonts.inter(
              color: isDarkMode
                  ? AppColors.darkTextSecondary
                  : AppColors.lightTextSecondary,
            ),
          ),
        ),
      );
    }

    return SizedBox(
      height: 210,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        itemCount: enrichedAppointments.length,
        itemBuilder: (context, index) {
          final appointment = enrichedAppointments[index];

          return Container(
            width: MediaQuery.of(context).size.width * 0.80,
            margin: EdgeInsets.only(
              right: index == enrichedAppointments.length - 1 ? 0 : 16,
            ),
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: isDarkMode
                    ? [const Color(0xFF6C3FC5), const Color(0xFF9B6FE0)]
                    : [const Color(0xFF7909CC), const Color(0xFF9B3FE8)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFF7909CC).withOpacity(0.3),
                  blurRadius: 16,
                  offset: const Offset(0, 6),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ── Label + Status ──
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Upcoming Appointment',
                      style: GoogleFonts.inter(
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                        color: Colors.white.withOpacity(0.75),
                        letterSpacing: 0.5,
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        appointment.status.label,
                        style: GoogleFonts.inter(
                          fontSize: 11,
                          fontWeight: FontWeight.w600,
                          color: Colors.white,
                        ),
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 14),

                // ── Doctor info ──
                Row(
                  children: [
                    const CircleAvatar(
                      radius: 26,
                      backgroundImage: AssetImage(
                          'assets/app_images/profile_avatar.png'),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            appointment.doctorName ?? 'Doctor',
                            style: GoogleFonts.inter(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                              color: Colors.white,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                          const SizedBox(height: 3),
                          Text(
                            appointment.doctorSpecialization ??
                                appointment.reason ??
                                'No details provided',
                            style: GoogleFonts.inter(
                              fontSize: 13,
                              fontWeight: FontWeight.w400,
                              color: Colors.white.withOpacity(0.75),
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ],
                      ),
                    ),
                    if (appointment.isEmergency)
                      Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: Colors.red.withOpacity(0.3),
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(
                          Icons.emergency_rounded,
                          color: Colors.white,
                          size: 20,
                        ),
                      ),
                  ],
                ),

                const SizedBox(height: 20),
                Divider(color: Colors.white.withOpacity(0.2), height: 1),
                const SizedBox(height: 16),

                // ── Date + Time ──
                Row(
                  children: [
                    Expanded(
                      child: Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(7),
                            decoration: BoxDecoration(
                              color: Colors.white.withOpacity(0.15),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: const Icon(Icons.calendar_today_rounded,
                                color: Colors.white, size: 16),
                          ),
                          const SizedBox(width: 10),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Date',
                                style: GoogleFonts.inter(
                                  fontSize: 11,
                                  color: Colors.white.withOpacity(0.6),
                                ),
                              ),
                              Text(
                                appointment.formattedDate,
                                style: GoogleFonts.inter(
                                  fontSize: 13,
                                  fontWeight: FontWeight.w600,
                                  color: Colors.white,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                    Container(
                        height: 36,
                        width: 1,
                        color: Colors.white.withOpacity(0.2)),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(7),
                            decoration: BoxDecoration(
                              color: Colors.white.withOpacity(0.15),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: const Icon(Icons.access_time_rounded,
                                color: Colors.white, size: 16),
                          ),
                          const SizedBox(width: 10),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Time',
                                style: GoogleFonts.inter(
                                  fontSize: 11,
                                  color: Colors.white.withOpacity(0.6),
                                ),
                              ),
                              Text(
                                appointment.formattedTime,
                                style: GoogleFonts.inter(
                                  fontSize: 13,
                                  fontWeight: FontWeight.w600,
                                  color: Colors.white,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  // ─────────────────────────────────────────────────────────
  // Categories Section
  // ─────────────────────────────────────────────────────────

  Widget _buildCategorySection(
      bool isDarkMode, List<Category> categories, bool isLoading) {
    if (isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (categories.isEmpty) {
      return Center(
        child: Text(
          'No categories available',
          style: GoogleFonts.inter(
            color: isDarkMode
                ? AppColors.darkTextSecondary
                : AppColors.lightTextSecondary,
          ),
        ),
      );
    }

    return SizedBox(
      height: 110,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        itemCount: categories.length,
        itemBuilder: (context, index) {
          final category = categories[index];
          final isSelected = _selectedCategoryId == category.id;

          return GestureDetector(
            onTap: () {
              setState(() {
                _selectedCategoryId = isSelected ? null : category.id;
              });
              context.read<DoctorProvider>().applyFilters(
                category: isSelected ? null : category.id.toString(),
              );
            },
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              margin: const EdgeInsets.only(right: 16),
              child: Column(
                children: [
                  AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: isSelected
                          ? AppColors.indigoPrimary
                          : isDarkMode
                          ? AppColors.darkSurface
                          : AppColors.indigoPrimary.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                        color: isSelected
                            ? AppColors.indigoPrimary
                            : Colors.transparent,
                        width: 2,
                      ),
                      boxShadow: isSelected
                          ? [
                        BoxShadow(
                          color:
                          AppColors.indigoPrimary.withOpacity(0.4),
                          blurRadius: 10,
                          offset: const Offset(0, 4),
                        ),
                      ]
                          : [],
                    ),
                    child: category.icon != null
                        ? Image.network(
                      category.icon!,
                      width: 28,
                      height: 28,
                      color: isSelected ? Colors.white : null,
                      colorBlendMode: BlendMode.srcIn,
                      errorBuilder: (context, error, stackTrace) {
                        return Icon(
                          Icons.medical_services_outlined,
                          color: isSelected
                              ? Colors.white
                              : AppColors.indigoPrimary,
                          size: 28,
                        );
                      },
                      loadingBuilder: (context, child, loadingProgress) {
                        if (loadingProgress == null) return child;
                        return SizedBox(
                          width: 28,
                          height: 28,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: isSelected
                                ? Colors.white
                                : AppColors.indigoPrimary,
                            value: loadingProgress.expectedTotalBytes !=
                                null
                                ? loadingProgress
                                .cumulativeBytesLoaded /
                                loadingProgress.expectedTotalBytes!
                                : null,
                          ),
                        );
                      },
                    )
                        : Icon(
                      Icons.medical_services_outlined,
                      color: isSelected
                          ? Colors.white
                          : AppColors.indigoPrimary,
                      size: 28,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    category.name,
                    style: GoogleFonts.inter(
                      fontSize: 12,
                      fontWeight:
                      isSelected ? FontWeight.w600 : FontWeight.w500,
                      color: isSelected
                          ? AppColors.indigoPrimary
                          : isDarkMode
                          ? AppColors.darkTextSecondary
                          : AppColors.lightTextSecondary,
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}