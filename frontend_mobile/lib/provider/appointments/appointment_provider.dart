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
      final newAppointments = data['appointments'] as List<Appointment>;
      _appointments.addAll(newAppointments);
      _hasMore = data['nextPage'] != null;
      if (_hasMore) _currentPage++;
      _error = null;
    } catch (e) {
      _error = 'Failed to load appointments. Please try again.';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}