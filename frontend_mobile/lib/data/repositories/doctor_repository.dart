import 'package:flutter/material.dart';
import '../../core/api/api_client.dart';
import '../model/doctor_model.dart';

class DoctorRepository {
  final ApiClient _apiClient = ApiClient();

  Future<Map<String, dynamic>> fetchDoctors({
    String? search,
    String? category,
    String? specialization,
    double? minRating,
    bool? isVerified = true,
    int page = 1,
  }) async {
    try {
      final Map<String, dynamic> params = {
        'page': page,
        if (isVerified != null) 'is_verified': isVerified,
        if (search != null && search.isNotEmpty) 'search': search,
        if (category != null && category.isNotEmpty) 'category': category,
        if (specialization != null && specialization.isNotEmpty)
          'specialization': specialization,
        if (minRating != null) 'min_rating': minRating,
      };

      final response = await _apiClient.get(
        '/users/doctors/',
        queryParameters: params,
      );

      if (response.statusCode != 200) {
        throw Exception(
            'Failed to fetch doctors. Status: ${response.statusCode}');
      }

      final data = response.data as Map<String, dynamic>;

      return {
        'doctors': (data['results'] as List<dynamic>).map((d) {
          debugPrint('Doctor raw: $d'); // <-- debug here, after data is defined
          return Doctor.fromJson(d as Map<String, dynamic>);
        }).toList(),
        'nextPage': data['next'] != null ? page + 1 : null,
        'total': data['count'] as int? ?? 0,
      };
    } catch (e) {
      rethrow;
    }
  }

  Future<List<Doctor>> fetchAllDoctors() async {
    final List<Doctor> allDoctors = [];
    int page = 1;
    bool hasMore = true;

    try {
      while (hasMore) {
        final response = await _apiClient.get(
          '/users/doctors/',
          queryParameters: {
            'page': page,
            'is_verified': true,
          },
        );

        if (response.statusCode != 200) break;

        final data = response.data as Map<String, dynamic>;

        final results = (data['results'] as List<dynamic>).map((d) {
          debugPrint('Doctor raw keys: ${(d as Map<String, dynamic>).keys.toList()}');
          debugPrint('Doctor raw data: $d');
          return Doctor.fromJson(d as Map<String, dynamic>);
        }).toList();

        allDoctors.addAll(results);
        hasMore = data['next'] != null;
        page++;
      }
    } catch (e) {
      debugPrint('fetchAllDoctors error: $e');
    }

    return allDoctors;
  }
}