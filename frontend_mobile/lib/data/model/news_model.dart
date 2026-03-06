class NewsArticle {
  final int id;
  final String title;
  final String slug;
  final String content;
  final String? image;
  final bool isTopNews;
  final String tags;
  final String author;
  final String authorName;
  final List<NewsParagraph> paragraphs;
  final int likeCount;
  final int commentCount;
  final DateTime createdAt;
  final DateTime updatedAt;

  NewsArticle({
    required this.id,
    required this.title,
    required this.slug,
    required this.content,
    this.image,
    required this.isTopNews,
    required this.tags,
    required this.author,
    required this.authorName,
    required this.paragraphs,
    required this.likeCount,
    required this.commentCount,
    required this.createdAt,
    required this.updatedAt,
  });

  factory NewsArticle.fromJson(Map<String, dynamic> json) {
    return NewsArticle(
      id: json['id'] as int,
      title: json['title'] as String? ?? '',
      slug: json['slug'] as String? ?? '',
      content: json['content'] as String? ?? '',
      image: json['image'] as String?,
      isTopNews: json['is_top_news'] as bool? ?? false,
      tags: json['tags'] as String? ?? '',
      author: json['author'] as String? ?? '',
      authorName: json['author_name'] as String? ?? '',
      paragraphs: (json['paragraphs'] as List<dynamic>?)
          ?.map((e) {
        if (e is Map<String, dynamic>) {
          return NewsParagraph.fromJson(e);
        }
        return NewsParagraph(
          id: 0,
          order: 0,
          subheading: '',
          body: e.toString(),
          image: null,
        );
      })
          .toList() ??
          [],
      likeCount: json['like_count'] as int? ?? 0,
      commentCount: json['comment_count'] as int? ?? 0,
      createdAt: DateTime.tryParse(json['created_at'] as String? ?? '') ??
          DateTime.now(),
      updatedAt: DateTime.tryParse(json['updated_at'] as String? ?? '') ??
          DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'title': title,
    'slug': slug,
    'content': content,
    'image': image,
    'is_top_news': isTopNews,
    'tags': tags,
    'author': author,
    'author_name': authorName,
    'paragraphs': paragraphs.map((p) => p.toJson()).toList(),
    'like_count': likeCount,
    'comment_count': commentCount,
    'created_at': createdAt.toIso8601String(),
    'updated_at': updatedAt.toIso8601String(),
  };
}

class NewsParagraph {
  final int id;
  final int order;
  final String subheading;
  final String body;
  final String? image;

  NewsParagraph({
    required this.id,
    required this.order,
    required this.subheading,
    required this.body,
    this.image,
  });

  factory NewsParagraph.fromJson(Map<String, dynamic> json) {
    return NewsParagraph(
      id: json['id'] as int? ?? 0,
      order: (json['order'] as num?)?.toInt() ?? 0,
      subheading: json['subheading'] as String? ?? '',
      body: json['body'] as String? ?? '',
      image: json['image'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'order': order,
    'subheading': subheading,
    'body': body,
    'image': image,
  };
}

class PaginatedNews {
  final int count;
  final String? next;
  final String? previous;
  final List<NewsArticle> results;

  PaginatedNews({
    required this.count,
    this.next,
    this.previous,
    required this.results,
  });

  factory PaginatedNews.fromJson(Map<String, dynamic> json) {
    return PaginatedNews(
      count: json['count'] as int? ?? 0,
      next: json['next'] as String?,
      previous: json['previous'] as String?,
      results: (json['results'] as List<dynamic>?)
          ?.map((e) => NewsArticle.fromJson(e as Map<String, dynamic>))
          .toList() ??
          [],
    );
  }
}