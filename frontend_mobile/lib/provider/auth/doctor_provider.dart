import 'package:flutter/cupertino.dart';

import '../../data/model/doctor_model.dart';
import '../../data/repositories/doctor_repository.dart';

class DoctorProvider extends ChangeNotifier {
  final DoctorRepository _repo = DoctorRepository();
  double? get currentMinRating => _currentMinRating;
  String? get currentSpecialization => _currentSpecialization;

  List<Doctor> _doctors = [];
  bool _isLoading = false;
  bool _hasMore = true;
  String? _error;
  int _currentPage = 1;
  int _total = 0;

  String? _currentSearch;
  String? _currentCategory;
  String? _currentSpecialization;
  double? _currentMinRating;

  List<Doctor> get doctors => _doctors;
  bool get isLoading => _isLoading;
  bool get hasMore => _hasMore;
  String? get error => _error;
  int get total => _total;

  Future<void> loadDoctors({
    String? search,
    String? category,
    String? specialization,
    double? minRating,
    bool isRefresh = false,
  }) async {
    if (_isLoading) return;
    if (!_hasMore && !isRefresh) return;

    if (isRefresh) {
      _currentPage = 1;
      _doctors = [];
      _hasMore = true;
      _error = null;
      _currentSearch = search;
      _currentCategory = category;
      _currentSpecialization = specialization;
      _currentMinRating = minRating;
    }

    _isLoading = true;
    notifyListeners();

    try {
      final data = await _repo.fetchDoctors(
        search: _currentSearch,
        category: _currentCategory,
        specialization: _currentSpecialization,
        minRating: _currentMinRating,
        page: _currentPage,
      );

      final newDoctors = data['doctors'] as List<Doctor>;
      _doctors.addAll(newDoctors);
      _total = data['total'] as int;
      _hasMore = data['nextPage'] != null;
      if (_hasMore) _currentPage++;
      _error = null;
    } catch (e) {
      _error = 'Failed to load doctors. Please try again.';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> search(String query) async {
    await loadDoctors(
      search: query,
      category: _currentCategory,
      specialization: _currentSpecialization,
      minRating: _currentMinRating,
      isRefresh: true,
    );
  }

  Future<void> applyFilters({
    String? category,
    String? specialization,
    double? minRating,
  }) async {
    await loadDoctors(
      search: _currentSearch,
      category: category,
      specialization: specialization,
      minRating: minRating,
      isRefresh: true,
    );
  }

  void clearFilters() {
    loadDoctors(isRefresh: true);
  }
}