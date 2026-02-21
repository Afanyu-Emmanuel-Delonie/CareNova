class Appointment {
  final int id;
  final String doctorId;
  final String patientName;
  final String? doctorName;
  final String? patientBloodGroup;
  final String? patientPhone;
  final DateTime appointmentDate;
  final String appointmentTime;
  final bool isEmergency;
  final String? reason;
  final AppointmentStatus status;
  final String? doctorSpecialization;

  Appointment({
    required this.id,
    required this.doctorId,
    required this.patientName,
    this.patientBloodGroup,
    this.patientPhone,
    required this.appointmentDate,
    required this.appointmentTime,
    required this.isEmergency,
    this.reason,
    required this.status,
    this.doctorName,
    this.doctorSpecialization,
  });

  factory Appointment.fromJson(Map<String, dynamic> json) {
    return Appointment(
      id: json['id'] as int,
      doctorId: json['doctor_id'] as String,
      patientName: json['patient_name'] as String? ?? '',
      patientBloodGroup: json['patient_blood_group'] as String?,
      patientPhone: json['patient_phone'] as String?,
      appointmentDate: DateTime.parse(json['appointment_date'] as String),
      appointmentTime: json['appointment_time'] as String? ?? '',
      isEmergency: json['is_emergency'] as bool? ?? false,
      reason: json['reason'] as String?,
      status: AppointmentStatus.fromString(
          json['status'] as String? ?? 'PENDING'),
    );
  }

  Appointment withDoctor({
    required String name,
    required String specialization,
  }) {
    return Appointment(
      id: id,
      doctorId: doctorId,
      patientName: patientName,
      patientBloodGroup: patientBloodGroup,
      patientPhone: patientPhone,
      appointmentDate: appointmentDate,
      appointmentTime: appointmentTime,
      isEmergency: isEmergency,
      reason: reason,
      status: status,
      doctorName: name,
      doctorSpecialization: specialization,
    );
  }

  String get formattedTime {
    try {
      final parts = appointmentTime.split(':');
      final hour = int.parse(parts[0]);
      final minute = parts[1].padLeft(2, '0');
      final period = hour >= 12 ? 'PM' : 'AM';
      final displayHour = hour > 12 ? hour - 12 : (hour == 0 ? 12 : hour);
      return '$displayHour:$minute $period';
    } catch (_) {
      return appointmentTime;
    }
  }

  String get formattedDate {
    const months = [
      'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ];
    return '${appointmentDate.day} ${months[appointmentDate.month - 1]} ${appointmentDate.year}';
  }

  bool get isUpcoming => appointmentDate.isAfter(DateTime.now());
}

enum AppointmentStatus {
  pending,
  confirmed,
  cancelled,
  completed;

  static AppointmentStatus fromString(String value) {
    switch (value.toUpperCase()) {
      case 'CONFIRMED':
        return AppointmentStatus.confirmed;
      case 'CANCELLED':
        return AppointmentStatus.cancelled;
      case 'COMPLETED':
        return AppointmentStatus.completed;
      case 'PENDING':
      default:
        return AppointmentStatus.pending;
    }
  }

  String get label {
    switch (this) {
      case AppointmentStatus.pending:
        return 'Pending';
      case AppointmentStatus.confirmed:
        return 'Confirmed';
      case AppointmentStatus.cancelled:
        return 'Cancelled';
      case AppointmentStatus.completed:
        return 'Completed';
    }
  }

  int get colorValue {
    switch (this) {
      case AppointmentStatus.pending:
        return 0xFFF59E0B;
      case AppointmentStatus.confirmed:
        return 0xFF10B981;
      case AppointmentStatus.cancelled:
        return 0xFFEF4444;
      case AppointmentStatus.completed:
        return 0xFF6366F1;
    }
  }
}