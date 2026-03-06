import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';

import '../../../core/theme/app_colors.dart';
import '../../../data/model/news_model.dart';
import '../../provider/news/news_provider.dart';


class NewsSection extends StatelessWidget {
  const NewsSection({super.key});

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final provider = context.watch<NewsProvider>();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSectionHeader(context, isDarkMode),
        const SizedBox(height: 10),
        _buildContent(context, isDarkMode, provider),
        const SizedBox(height: 20),
      ],
    );
  }

  // ─────────────────────────────────────────────────────────
  // Section Header
  // ─────────────────────────────────────────────────────────

  Widget _buildSectionHeader(BuildContext context, bool isDarkMode) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          'Latest News',
          style: GoogleFonts.inter(
            fontSize: 18,
            fontWeight: FontWeight.w600,
            color: isDarkMode
                ? AppColors.darkTextPrimary
                : AppColors.lightTextPrimary,
          ),
        ),
        TextButton(
          onPressed: () {
            // TODO: navigate to full news list
          },
          child: Text(
            'See All',
            style: GoogleFonts.inter(
              fontSize: 14,
              fontWeight: FontWeight.w500,
              color: isDarkMode
                  ? AppColors.darkTextSecondary
                  : AppColors.lightTextSecondary,
            ),
          ),
        ),
      ],
    );
  }

  // ─────────────────────────────────────────────────────────
  // Content States
  // ─────────────────────────────────────────────────────────

  Widget _buildContent(
      BuildContext context, bool isDarkMode, NewsProvider provider) {
    if (provider.listStatus == NewsStatus.loading &&
        provider.articles.isEmpty) {
      return const SizedBox(
        height: 120,
        child: Center(child: CircularProgressIndicator()),
      );
    }

    if (provider.listStatus == NewsStatus.error && provider.articles.isEmpty) {
      return Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: isDarkMode ? AppColors.darkSurface : AppColors.lightSurface,
          borderRadius: BorderRadius.circular(16),
        ),
        child: Center(
          child: Column(
            children: [
              Text(
                provider.listError ?? 'Something went wrong',
                style: GoogleFonts.inter(
                  color: isDarkMode
                      ? AppColors.darkTextSecondary
                      : AppColors.lightTextSecondary,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              ElevatedButton(
                onPressed: () => context.read<NewsProvider>().refresh(),
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      );
    }

    if (provider.articles.isEmpty) {
      return Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: isDarkMode ? AppColors.darkSurface : AppColors.lightSurface,
          borderRadius: BorderRadius.circular(16),
        ),
        child: Center(
          child: Text(
            'No news available',
            style: GoogleFonts.inter(
              color: isDarkMode
                  ? AppColors.darkTextSecondary
                  : AppColors.lightTextSecondary,
            ),
          ),
        ),
      );
    }

    final articles = provider.articles.take(5).toList();

    return Column(
      children: List.generate(articles.length, (index) {
        return Padding(
          padding: EdgeInsets.only(
            bottom: index == articles.length - 1 ? 0 : 12,
          ),
          child: _NewsCard(article: articles[index], isDarkMode: isDarkMode),
        );
      }),
    );
  }
}

// ─────────────────────────────────────────────────────────
// News Card
// ─────────────────────────────────────────────────────────

class _NewsCard extends StatelessWidget {
  final NewsArticle article;
  final bool isDarkMode;

  const _NewsCard({required this.article, required this.isDarkMode});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: isDarkMode ? AppColors.darkSurface : AppColors.lightSurface,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(isDarkMode ? 0.2 : 0.06),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ── Thumbnail ──
          ClipRRect(
            borderRadius: const BorderRadius.only(
              topLeft: Radius.circular(16),
              bottomLeft: Radius.circular(16),
            ),
            child: article.image != null && article.image!.isNotEmpty
                ? Image.network(
              article.image!,
              width: 100,
              height: 100,
              fit: BoxFit.cover,
              errorBuilder: (_, __, ___) => _placeholderImage(),
              loadingBuilder: (context, child, progress) {
                if (progress == null) return child;
                return _placeholderImage(loading: true);
              },
            )
                : _placeholderImage(),
          ),

          // ── Text content ──
          Expanded(
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // ── Top News badge ──
                  if (article.isTopNews) ...[
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: AppColors.indigoPrimary.withOpacity(0.12),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        'Top News',
                        style: GoogleFonts.inter(
                          fontSize: 10,
                          fontWeight: FontWeight.w600,
                          color: AppColors.indigoPrimary,
                        ),
                      ),
                    ),
                    const SizedBox(height: 6),
                  ],

                  // ── Title ──
                  Text(
                    article.title,
                    style: GoogleFonts.inter(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: isDarkMode
                          ? AppColors.darkTextPrimary
                          : AppColors.lightTextPrimary,
                      height: 1.3,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),

                  const SizedBox(height: 8),

                  // ── Author + Date ──
                  Row(
                    children: [
                      Icon(
                        Icons.person_outline_rounded,
                        size: 13,
                        color: isDarkMode
                            ? AppColors.darkTextSecondary
                            : AppColors.lightTextSecondary,
                      ),
                      const SizedBox(width: 4),
                      Expanded(
                        child: Text(
                          article.authorName,
                          style: GoogleFonts.inter(
                            fontSize: 12,
                            color: isDarkMode
                                ? AppColors.darkTextSecondary
                                : AppColors.lightTextSecondary,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Icon(
                        Icons.access_time_rounded,
                        size: 13,
                        color: isDarkMode
                            ? AppColors.darkTextSecondary
                            : AppColors.lightTextSecondary,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        _formatDate(article.createdAt),
                        style: GoogleFonts.inter(
                          fontSize: 12,
                          color: isDarkMode
                              ? AppColors.darkTextSecondary
                              : AppColors.lightTextSecondary,
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 8),

                  // ── Likes + Comments ──
                  Row(
                    children: [
                      Icon(Icons.favorite_border_rounded,
                          size: 14, color: AppColors.indigoPrimary),
                      const SizedBox(width: 4),
                      Text(
                        '${article.likeCount}',
                        style: GoogleFonts.inter(
                          fontSize: 12,
                          color: AppColors.indigoPrimary,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Icon(Icons.chat_bubble_outline_rounded,
                          size: 14,
                          color: isDarkMode
                              ? AppColors.darkTextSecondary
                              : AppColors.lightTextSecondary),
                      const SizedBox(width: 4),
                      Text(
                        '${article.commentCount}',
                        style: GoogleFonts.inter(
                          fontSize: 12,
                          color: isDarkMode
                              ? AppColors.darkTextSecondary
                              : AppColors.lightTextSecondary,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _placeholderImage({bool loading = false}) {
    return Container(
      margin: EdgeInsets.only( bottom: 4, top: 4, left: 6),
      width: 100,
      height: 126,
      color: isDarkMode ? const Color(0xFF2A2A3D) : const Color(0xFFF0EDFF),
      child: loading
          ? Center(
        child: CircularProgressIndicator(
          strokeWidth: 2,
          color: AppColors.indigoPrimary,
        ),
      )
          : Icon(
        Icons.article_outlined,
        color: AppColors.indigoPrimary.withOpacity(0.5),
        size: 32,
      ),
    );
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final diff = now.difference(date);
    if (diff.inDays == 0) return 'Today';
    if (diff.inDays == 1) return 'Yesterday';
    if (diff.inDays < 7) return '${diff.inDays}d ago';
    return '${date.day}/${date.month}/${date.year}';
  }
}