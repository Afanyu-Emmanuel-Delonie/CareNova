import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:frontend_mobile/data/model/appointment_model.dart';
import 'package:frontend_mobile/data/model/doctor_model.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'package:readmore/readmore.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/widgets/app_bar.dart';
import '../../../provider/appointments/appointment_provider.dart';

class AppointmentDetails extends StatelessWidget{

  final Appointment appointment;
  const AppointmentDetails({super.key, required this.appointment});

  @override
  Widget build(BuildContext context) {

    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(

      backgroundColor:
      isDarkMode ? AppColors.darkBackground : AppColors.lightBackground,

      appBar: AppBarWidget(
        title: 'Appointment Details',
        showBackButton: true,
        showNotification: true,
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 10.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Stack(
                    children: [
                      CircleAvatar(
                        radius: 50,
                        backgroundImage: appointment.doctorProfilePicture != null
                            ? NetworkImage(appointment.doctorProfilePicture!) as ImageProvider
                            : const AssetImage('assets/app_images/profile_avatar.png'),
                      ),

                      if(appointment.doctorIsVerified)
                        Positioned(
                          bottom: 5,
                          right: 0,
                          child: const Icon(
                            Icons.verified_rounded,
                            size: 25,
                            color: AppColors.indigoPrimary,
                          ),
                        )
                    ],
                  ),

                  SizedBox(width: 20.0,),
                  
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                     children: [
                       Text(
                         'Dr. ${appointment.doctorName}',
                         style: GoogleFonts.inter(
                           fontSize: 16,
                           fontWeight: FontWeight.bold,
                           color: isDarkMode
                               ? AppColors.darkTextPrimary
                               : AppColors.indigoPrimary,
                         ),
                       ),

                       SizedBox(height: 5.0,),

                       Text(
                         'Specialty: ${appointment.doctorSpecialization}',
                         style: GoogleFonts.inter(
                           fontSize: 12,
                           fontWeight:
                           FontWeight.w500,
                           color: isDarkMode
                               ? AppColors.darkTextSecondary
                               : AppColors.lightTextSecondary,
                         ),
                       ),

                       SizedBox(height: 10.0,),

                       Row(
                         children: [
                           Icon(
                             Icons.description_outlined,
                             size: 20,
                             color: isDarkMode
                                 ? AppColors.darkTextPrimary
                                 : AppColors.indigoPrimary,
                           ),

                           SizedBox(width: 5.0,),

                           Text(
                             'LEC No: ${appointment.licenseNumber}',
                             style: GoogleFonts.inter(
                               fontSize: 12,
                               fontWeight: FontWeight.bold,
                               color: isDarkMode
                                   ? AppColors.darkTextPrimary
                                   : AppColors.indigoPrimary,
                             ),
                           )
                         ],
                       )
                     ],
                  )
                ],
              ),

              SizedBox(height: 20.0,),

              _buildSectionTitle(isDarkMode, 'About Doctor'),

              SizedBox(height: 10.0,),

              ReadMoreText(
                appointment.doctorBio != null && appointment.doctorBio!.isNotEmpty
                    ? appointment.doctorBio!
                    : 'No bio available',
                trimLines: 3,
                colorClickableText: AppColors.indigoPrimary,
                trimMode: TrimMode.Line,
                trimCollapsedText: 'Read More',
                trimExpandedText: 'Read Less',
                style: GoogleFonts.inter(
                  fontSize: 14,
                  fontWeight: FontWeight.w500,
                  color: isDarkMode
                      ? AppColors.darkTextSecondary
                      : AppColors.lightTextSecondary,
                ),

              ),

              SizedBox(height: 20.0,),

              _buildSectionTitle(isDarkMode, 'Appointment Details'),

              SizedBox(height: 10.0,),

              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: isDarkMode ? AppColors.darkSurface : AppColors.lightSurface,
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'Appointment Note',
                          style: GoogleFonts.inter(
                            fontSize: 14,
                            fontWeight: FontWeight.w600,
                            color: isDarkMode
                                ? AppColors.darkTextPrimary
                                : AppColors.indigoPrimary,
                          ),
                        ),

                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 8, vertical: 3),
                          decoration: BoxDecoration(
                            color: AppColors.indigoPrimary.withOpacity(0.12),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            appointment.status.label,
                            style: GoogleFonts.inter(
                              fontSize: 11,
                              fontWeight: FontWeight.w600,
                              color: AppColors.indigoPrimary,
                            ),
                          ),
                        )
                      ],
                    ),

                    SizedBox(height: 10.0,),

                    ReadMoreText(
                      appointment.reason != null && appointment.reason!.isNotEmpty
                          ? appointment.reason!
                          : 'No note available',
                      trimLines: 3,
                      colorClickableText: AppColors.indigoPrimary,
                      trimMode: TrimMode.Line,
                      trimCollapsedText: 'Read More',
                      trimExpandedText: 'Read Less',
                      style: GoogleFonts.inter(
                        fontSize: 14,
                        fontWeight: FontWeight.w500,
                        color: isDarkMode
                            ? AppColors.darkTextSecondary
                            : AppColors.lightTextSecondary,
                      ),

                    ),

                    const SizedBox(height: 20),

                    // ── Date + Time ──
                    Row(
                      children: [
                        Expanded(
                          child: Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.all(7),
                                decoration: BoxDecoration(
                                  color: AppColors.indigoPrimary.withOpacity(0.15),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: const Icon(Icons.calendar_today_rounded,
                                    color: AppColors.indigoPrimary, size: 16),
                              ),
                              const SizedBox(width: 10),
                              Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    'Date',
                                    style: GoogleFonts.inter(
                                      fontSize: 11,
                                      color: AppColors.indigoPrimary.withOpacity(0.6),
                                    ),
                                  ),
                                  Text(
                                    appointment.formattedDate,
                                    style: GoogleFonts.inter(
                                      fontSize: 13,
                                      fontWeight: FontWeight.w600,
                                      color: AppColors.indigoPrimary,
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
                            color: AppColors.indigoPrimary.withOpacity(0.2)),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.all(7),
                                decoration: BoxDecoration(
                                  color: AppColors.indigoPrimary.withOpacity(0.2),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: const Icon(Icons.access_time_rounded,
                                    color: AppColors.indigoPrimary, size: 16),
                              ),
                              const SizedBox(width: 10),
                              Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    'Time',
                                    style: GoogleFonts.inter(
                                      fontSize: 11,
                                      color: AppColors.indigoPrimary.withOpacity(0.6),
                                    ),
                                  ),
                                  Text(
                                    appointment.formattedTime,
                                    style: GoogleFonts.inter(
                                      fontSize: 13,
                                      fontWeight: FontWeight.w600,
                                      color: AppColors.indigoPrimary,
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
                )
              ),

              SizedBox(height: 20.0,),

              Text(
                'Note You will have to pay a consultation fee of 10,000 RWF before the consultation as the consultation fee is not included in the appointment fee',
                style: GoogleFonts.inter(
                  fontSize: 14,
                  fontWeight: FontWeight.w500,
                  color: isDarkMode
                      ? AppColors.darkTextSecondary
                      : AppColors.lightTextSecondary,
                ),
              )
            ],
          ),
        )
      ),

      bottomNavigationBar: Container(
        padding: const EdgeInsets.fromLTRB(20, 12, 20, 32),
        decoration: BoxDecoration(
          color: isDarkMode ? AppColors.darkSurface : AppColors.lightSurface,
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.08),
              blurRadius: 10,
              offset: const Offset(0, -4),
            ),
          ],
        ),
        child: ElevatedButton(
          style: ElevatedButton.styleFrom(
            backgroundColor: AppColors.error,
            padding: const EdgeInsets.symmetric(vertical: 16),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(14),
            ),
          ),
          onPressed: () async {
            final success = await context.read<AppointmentProvider>().cancelAppointment(appointment.id);
            if (success) {
              Navigator.pop(context);
            }
          },
          child: Text(
            'Cancel Appointment',
            style: GoogleFonts.inter(
              fontSize: 15,
              fontWeight: FontWeight.w600,
              color: Colors.white,
            ),
          ),
        ),
      )
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

}