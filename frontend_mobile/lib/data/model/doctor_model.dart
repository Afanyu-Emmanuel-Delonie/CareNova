import 'appointment_model.dart';

class Doctor {
  final int id;
  final String uuid;
  final String fullName;
  final int? category;
  final String categoryName;
  final String specialization;
  final String? licenseNumber;
  final String? bio;
  final bool isVerified;
  final double averageRating;
  final String totalAppointments;
  final String emergencyCount;
  final String pendingCount;
  final List<Appointment> appointments;

  Doctor({
    required this.id,
    required this.uuid,
    required this.fullName,
    this.category,
    required this.categoryName,
    required this.specialization,
    this.licenseNumber,
    this.bio,
    required this.isVerified,
    required this.averageRating,
    required this.totalAppointments,
    required this.emergencyCount,
    required this.pendingCount,
    this.appointments = const [],
  });

  factory Doctor.fromJson(Map<String, dynamic> json) {
    final appointmentsList = (json['appointments'] as List<dynamic>?)
        ?.map((a) => Appointment.fromJson(a as Map<String, dynamic>))
        .toList() ??
        [];

    // Extract UUID from the first appointment's doctor_id
    final uuid = appointmentsList.isNotEmpty
        ? appointmentsList.first.doctorId
        : '';

    return Doctor(
      id: json['id'] as int,
      uuid: uuid,
      fullName: json['full_name'] as String? ?? '',
      category: json['category'] as int?,
      categoryName: json['category_name'] as String? ?? 'General',
      specialization: json['specialization'] as String? ?? '',
      licenseNumber: json['license_number'] as String?,
      bio: json['bio'] as String?,
      isVerified: json['is_verified'] as bool? ?? false,
      averageRating: (json['average_rating'] as num?)?.toDouble() ?? 0.0,
      totalAppointments: json['total_appointments']?.toString() ?? '0',
      emergencyCount: json['emergency_count']?.toString() ?? '0',
      pendingCount: json['pending_count']?.toString() ?? '0',
      appointments: appointmentsList,
    );
  }
}