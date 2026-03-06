import '../../../../data/model/appointment_model.dart';
import '../../../../data/model/doctor_model.dart';

class DashboardViewModel {
  static List<Appointment> enrichAppointments(
      List<Appointment> appointments,
      List<Doctor> doctors,
      ) {
    return appointments.map((appointment) {
      try {
        final matched = doctors.firstWhere(
              (d) => d.uuid == appointment.doctorId,
        );

        return appointment.withDoctor(
          name: matched.fullName,
          specialization: matched.specialization.isNotEmpty
              ? matched.specialization
              : matched.categoryName,
          bio: matched.bio,
          license: matched.licenseNumber,
          profilePicture: matched.profilePicture,
          isVerified: matched.isVerified,

        );
      } catch (_) {
        return appointment;
      }


    }).toList();
  }

  static bool isPatient(String? role) {
    return role?.toLowerCase() == 'patient';
  }
}

