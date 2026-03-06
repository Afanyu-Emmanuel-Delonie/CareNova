import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:frontend_mobile/core/widgets/app_bar.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:readmore/readmore.dart';

import '../../../core/theme/app_colors.dart';
import '../../../data/model/doctor_model.dart';

class DoctorsProfile extends StatelessWidget{
  final Doctor doctor;
  const DoctorsProfile({super.key, required this.doctor});

  @override
  Widget build(BuildContext context) {

    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(

      backgroundColor:
      isDarkMode ? AppColors.darkBackground : AppColors.lightBackground,

      appBar: AppBarWidget(
          title: 'Doctor\'s  Profile ',
          showBackButton: true,
          showNotification: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
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
                          backgroundImage: doctor.profilePicture != null
                              ? NetworkImage(doctor.profilePicture!) as ImageProvider
                              : const AssetImage('assets/app_images/profile_avatar.png'),
                        ),

                        if(doctor.isVerified)
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
                          'Dr. ${doctor.fullName}',
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
                          'Specialty: ${doctor.specialization}',
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
                              'LEC No: ${doctor.licenseNumber}',
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

                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Container(
                        width: double.infinity,
                        padding: const EdgeInsets.symmetric(
                            horizontal: 8, vertical: 10),
                        decoration: BoxDecoration(
                          color: AppColors.indigoPrimary.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(5),
                        ),
                       child: Column(
                         children: [
                           Text(
                             'Average Rating',
                             style: GoogleFonts.inter(
                               fontSize: 12,
                               fontWeight: FontWeight.w500
                             )
                           ),

                           SizedBox(height: 10.0,),

                           Row(
                             mainAxisAlignment: MainAxisAlignment.center,
                             children: [
                               Icon(
                                 Icons.star,
                                 size: 20,
                                 color: Colors.amber,
                               ),

                               SizedBox(width: 5.0,),

                               Text(
                                 '${doctor.averageRating}',
                                 style: GoogleFonts.inter(
                                   fontSize: 16,
                                   fontWeight: FontWeight.bold,
                                   color: AppColors.indigoPrimary,
                                 ),
                               )
                             ],
                           )


                         ],
                       ),
                      ),
                    ),

                    SizedBox(width: 10.0,),

                    Expanded(
                      child: Container(
                        width: double.infinity,
                        padding: const EdgeInsets.symmetric(
                            horizontal: 8, vertical: 10),
                        decoration: BoxDecoration(
                          color: AppColors.indigoPrimary.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(5),
                        ),
                        child: Column(
                          children: [
                            Text(
                                'Total Visits',
                                style: GoogleFonts.inter(
                                    fontSize: 12,
                                    fontWeight: FontWeight.w500
                                )
                            ),

                            SizedBox(height: 10.0,),

                            Text(
                              doctor.totalAppointments,
                              style: GoogleFonts.inter(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                                color: AppColors.indigoPrimary,
                              ),
                            )
                          ],
                        ),
                      ),
                    ),

                    SizedBox(width: 10.0,),

                    Expanded(
                      child: Container(
                        width: double.infinity,
                        padding: const EdgeInsets.symmetric(
                            horizontal: 8, vertical: 10),
                        decoration: BoxDecoration(
                          color: AppColors.indigoPrimary.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(5),
                        ),
                        child: Column(
                          children: [
                            Text(
                                'Experience',
                                style: GoogleFonts.inter(
                                    fontSize: 12,
                                    fontWeight: FontWeight.w500
                                )
                            ),

                            SizedBox(height: 10.0,),

                            Text(
                              '${doctor.yearsExperience} yrs',
                              style: GoogleFonts.inter(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                                color: AppColors.indigoPrimary,
                              ),
                            )

                          ],
                        ),
                      ),
                    ),
                  ],
                ),

                SizedBox(height: 20.0,),

                _buildSectionTitle(isDarkMode, 'About Doctor'),

                SizedBox(height: 10.0,),

                ReadMoreText(
                  doctor.bio != null && doctor.bio!.isNotEmpty
                      ? doctor.bio!
                      : 'No bio available',
                  trimLines: 4,
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
              ],
            ),
          )
        ),
      ),
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