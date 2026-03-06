import '../../core/api/api_client.dart';
import '../model/appointment_model.dart';

class AppointmentRepository {
  final ApiClient _apiClient = ApiClient();

  Future<Map<String, dynamic>> fetchAppointments({int page = 1}) async {
    try {
      final response = await _apiClient.get(
        '/appointments/appointment/',
        queryParameters: {'page': page},
      );

      if (response.statusCode != 200) {
        throw Exception(
            'Failed to fetch appointments & doctors. Status: ${response.statusCode}');
      }

      final data = response.data as Map<String, dynamic>;

      return {
        'appointments & doctors': (data['results'] as List<dynamic>)
            .map((a) => Appointment.fromJson(a as Map<String, dynamic>))
            .toList(),
        'nextPage': data['next'] != null ? page + 1 : null,
        'total': data['count'] as int? ?? 0,
      };
    } catch (e) {
      rethrow;
    }
  }

  Future<void> cancelAppointment({
    required int appointmentId,
    String? reason,
  }) async {
    try{
      final response = await _apiClient.post(
        '/appointments/appointment/$appointmentId/patient-cancel/',
        {'cancellation_reason': reason ?? ''},
      );

      if ( response.statusCode != 200 ) {
        throw Exception(
            'Failed to cancel appointment. Status: ${response.statusCode}'
        );
    }
  } catch (e) {
    rethrow;
  }
  }
}