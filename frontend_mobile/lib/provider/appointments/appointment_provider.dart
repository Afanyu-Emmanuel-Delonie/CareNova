import 'package:flutter/material.dart';

import '../../data/model/appointment_model.dart';
import '../../data/repositories/appointment_repository.dart';

class AppointmentProvider extends ChangeNotifier {
  final AppointmentRepository _repo = AppointmentRepository();

  List<Appointment> _appointments = [];
  bool _isLoading = false;
  String? _error;
  int _currentPage = 1;
  bool _hasMore = true;

  List<Appointment> get appointments => _appointments;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get hasMore => _hasMore;

  List<Appointment> get upcomingAppointments => _appointments
      .where((a) => a.isUpcoming && a.status != AppointmentStatus.cancelled)
      .toList()
    ..sort((a, b) => a.appointmentDate.compareTo(b.appointmentDate));

  Appointment? get nextAppointment =>
      upcomingAppointments.isNotEmpty ? upcomingAppointments.first : null;

  Future<void> loadAppointments({bool isRefresh = false}) async {
    if (_isLoading) return;
    if (!_hasMore && !isRefresh) return;

    if (isRefresh) {
      _currentPage = 1;
      _appointments = [];
      _hasMore = true;
      _error = null;
    }

    _isLoading = true;
    notifyListeners();

    try {
      final data = await _repo.fetchAppointments(page: _currentPage);
      final newAppointments = data['appointments & doctors'] as List<Appointment>;
      _appointments.addAll(newAppointments);
      _hasMore = data['nextPage'] != null;
      if (_hasMore) _currentPage++;
      _error = null;
    } catch (e) {
      _error = 'Failed to load appointments & doctors. Please try again.';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> cancelAppointment(int appointmentId, {String? reason}) async {
    try {
      await _repo.cancelAppointment(
        appointmentId: appointmentId,
        reason: reason,
      );
      // update local state immediately
      _appointments = _appointments.map((a) {
        if (a.id == appointmentId) {
          return Appointment(
            id: a.id,
            doctorId: a.doctorId,
            patientName: a.patientName,
            patientBloodGroup: a.patientBloodGroup,
            patientPhone: a.patientPhone,
            appointmentDate: a.appointmentDate,
            appointmentTime: a.appointmentTime,
            isEmergency: a.isEmergency,
            reason: a.reason,
            status: AppointmentStatus.cancelled,
            doctorName: a.doctorName,
            doctorSpecialization: a.doctorSpecialization,
            doctorBio: a.doctorBio,
            licenseNumber: a.licenseNumber,
            doctorProfilePicture: a.doctorProfilePicture,
            doctorIsVerified: a.doctorIsVerified,
          );
        }
        return a;
      }).toList();
      notifyListeners();
      return true;
    } catch (e) {
      _error = 'Failed to cancel appointment.';
      notifyListeners();
      return false;
    }
  }
}