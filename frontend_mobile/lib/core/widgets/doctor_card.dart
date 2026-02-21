import 'package:flutter/material.dart';
import 'package:frontend_mobile/core/theme/app_colors.dart';
import 'package:frontend_mobile/data/model/doctor_model.dart';

class DoctorCard extends StatelessWidget {
  final Doctor doctor;
  final VoidCallback? onTap;

  const DoctorCard({
    super.key,
    required this.doctor,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return GestureDetector(
      onTap: onTap,
      child: Container(
        decoration: BoxDecoration(
          color: isDarkMode ? AppColors.darkSurface : AppColors.lightSurface,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.08),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Doctor Image
            ClipRRect(
              borderRadius:
              const BorderRadius.vertical(top: Radius.circular(16)),
              child: Image.asset(
                'assets/app_images/doctor.png',
                height: 150,
                width: double.infinity,
                fit: BoxFit.cover,
              ),
            ),

            // Doctor Info
            Padding(
              padding:
              const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Verified badge + Name row
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          doctor.fullName,
                          style: TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.bold,
                            color: isDarkMode
                                ? Colors.white
                                : Colors.black87,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      if (doctor.isVerified)
                        const Icon(
                          Icons.verified_rounded,
                          size: 16,
                          color: AppColors.indigoPrimary,
                        ),
                    ],
                  ),

                  const SizedBox(height: 4),

                  // Specialization Badge
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: AppColors.indigoPrimary.withOpacity(0.12),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(
                          Icons.medical_services_rounded,
                          size: 12,
                          color: AppColors.indigoPrimary,
                        ),
                        const SizedBox(width: 4),
                        Flexible(
                          child: Text(
                            doctor.specialization.isNotEmpty
                                ? doctor.specialization
                                : doctor.categoryName,
                            style: const TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w500,
                              color: AppColors.indigoPrimary,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 6),

                  // Rating row
                  Row(
                    children: [
                      const Icon(
                        Icons.star_rounded,
                        size: 14,
                        color: Colors.amber,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        doctor.averageRating.toStringAsFixed(1),
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: isDarkMode
                              ? Colors.white70
                              : Colors.black54,
                        ),
                      ),
                      const SizedBox(width: 6),
                      Text(
                        '(${doctor.totalAppointments} appointments)',
                        style: TextStyle(
                          fontSize: 11,
                          color: isDarkMode
                              ? Colors.white38
                              : Colors.black38,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}