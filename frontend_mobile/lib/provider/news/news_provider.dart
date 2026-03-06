import 'package:flutter/foundation.dart';
import 'package:frontend_mobile/data/model/news_model.dart';
import 'package:frontend_mobile/data/repositories/news_repository.dart';

enum NewsStatus { initial, loading, loaded, error }

class NewsProvider extends ChangeNotifier {
  final NewsRepository _repository = NewsRepository();

  // ── List state ──────────────────────────────────────────────────────────────

  NewsStatus _listStatus = NewsStatus.initial;
  List<NewsArticle> _articles = [];
  String? _listError;

  int _currentPage = 1;
  bool _hasNextPage = false;
  String? _activeTag;

  NewsStatus get listStatus => _listStatus;
  List<NewsArticle> get articles => _articles;
  String? get listError => _listError;
  bool get hasNextPage => _hasNextPage;
  String? get activeTag => _activeTag;

  // ── Detail state ─────────────────────────────────────────────────────────────

  NewsStatus _detailStatus = NewsStatus.initial;
  NewsArticle? _selectedArticle;
  String? _detailError;

  NewsStatus get detailStatus => _detailStatus;
  NewsArticle? get selectedArticle => _selectedArticle;
  String? get detailError => _detailError;

  // ── Actions ──────────────────────────────────────────────────────────────────

  Future<void> loadNews({String? tag}) async {
    _listStatus = NewsStatus.loading;
    _articles = [];
    _currentPage = 1;
    _activeTag = tag;
    _listError = null;
    notifyListeners();

    try {
      final paginated = await _repository.getNews(page: 1, tag: tag);
      _articles = paginated.results;
      _hasNextPage = paginated.next != null;
      _listStatus = NewsStatus.loaded;
    } on NewsException catch (e) {
      _listError = e.message;
      _listStatus = NewsStatus.error;
    } catch (e) {
      _listError = e.toString();
      _listStatus = NewsStatus.error;
    }

    notifyListeners();
  }

  Future<void> loadNextPage() async {
    if (_listStatus == NewsStatus.loading || !_hasNextPage) return;

    _listStatus = NewsStatus.loading;
    notifyListeners();

    try {
      _currentPage++;
      final paginated = await _repository.getNews(
        page: _currentPage,
        tag: _activeTag,
      );
      _articles = [..._articles, ...paginated.results];
      _hasNextPage = paginated.next != null;
      _listStatus = NewsStatus.loaded;
    } on NewsException catch (e) {
      _currentPage--;
      _listError = e.message;
      _listStatus = NewsStatus.error;
    } catch (e) {
      _currentPage--;
      _listError = e.toString();
      _listStatus = NewsStatus.error;
    }

    notifyListeners();
  }

  Future<void> loadArticleById(int id) async {
    _detailStatus = NewsStatus.loading;
    _selectedArticle = null;
    _detailError = null;
    notifyListeners();

    try {
      _selectedArticle = await _repository.getNewsById(id);
      _detailStatus = NewsStatus.loaded;
    } on NewsException catch (e) {
      _detailError = e.message;
      _detailStatus = NewsStatus.error;
    } catch (e) {
      _detailError = e.toString();
      _detailStatus = NewsStatus.error;
    }

    notifyListeners();
  }

  Future<void> filterByTag(String? tag) => loadNews(tag: tag);

  Future<void> refresh() => loadNews(tag: _activeTag);
}