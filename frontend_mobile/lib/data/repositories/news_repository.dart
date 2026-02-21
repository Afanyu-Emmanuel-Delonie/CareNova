import 'dart:convert';

import 'package:flutter/material.dart';

import '../../core/api/api_client.dart';
import '../model/news_model.dart';

class NewsRepository {
  final ApiClient _client = ApiClient();

  Future<PaginatedNews> getNews({int? page, String? tag}) async {
    try {
      final queryParams = <String, dynamic>{};
      if (page != null) queryParams['page'] = page;
      if (tag != null && tag.isNotEmpty) queryParams['tag'] = tag;

      final response = await _client.get(
        'news/news/',
        queryParameters: queryParams.isNotEmpty ? queryParams : null,
      );

      debugPrint('News status: ${response.statusCode}');
      debugPrint('News response: ${response.data}');

      if (response.statusCode != 200) {
        throw NewsException(
          'Failed to load news. Status: ${response.statusCode}',
        );
      }

      final data = response.data is String
          ? jsonDecode(response.data as String)
          : response.data;

      return PaginatedNews.fromJson(data as Map<String, dynamic>);
    } on NewsException {
      rethrow;
    } catch (e) {
      throw NewsException('Unexpected error: $e');
    }
  }

  Future<NewsArticle> getNewsById(int id) async {
    try {
      final response = await _client.get('news/news/$id/');

      debugPrint('Article status: ${response.statusCode}');

      if (response.statusCode != 200) {
        throw NewsException(
          'Failed to load article. Status: ${response.statusCode}',
        );
      }

      final data = response.data is String
          ? jsonDecode(response.data as String)
          : response.data;

      return NewsArticle.fromJson(data as Map<String, dynamic>);
    } on NewsException {
      rethrow;
    } catch (e) {
      throw NewsException('Unexpected error: $e');
    }
  }
}

class NewsException implements Exception {
  final String message;
  NewsException(this.message);

  @override
  String toString() => 'NewsException: $message';
}