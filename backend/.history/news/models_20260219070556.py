from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model

User = get_user_model()


class NewsArticle(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField(
        help_text="Optional summary or intro. Full body is composed of paragraphs below.",
        blank=True,
    )
    image = models.ImageField(upload_to='news_images/', null=True, blank=True)
    is_top_news = models.BooleanField(default=False)
    tags = models.CharField(
        max_length=255,
        blank=True,
        help_text="Comma-separated tags e.g. Health, COVID-19",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='authored_articles',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_top_news', '-created_at']
        verbose_name_plural = "News Articles"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def comment_count(self):
        return self.comments.count()


class ArticleParagraph(models.Model):
    """
    An ordered paragraph block belonging to a NewsArticle.
    Allows rich multi-section articles (e.g. subheading + body text per block).
    """
    article = models.ForeignKey(
        NewsArticle,
        on_delete=models.CASCADE,
        related_name='paragraphs',
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order of this paragraph within the article.",
    )
    subheading = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional subheading for this section.",
    )
    body = models.TextField()
    image = models.ImageField(
        upload_to='news_paragraph_images/',
        null=True,
        blank=True,
        help_text="Optional image to accompany this paragraph.",
    )

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"[{self.article.title}] §{self.order}"


class ArticleLike(models.Model):
    """Tracks which users have liked a given article. One like per user per article."""
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='news_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['article', 'user'], name='unique_like_per_user'),
        ]

    def __str__(self):
        return f"{self.user} liked '{self.article}'"


class ArticleComment(models.Model):
    """A comment left by a user on a news article. Supports one level of replies."""
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='news_comments')
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        help_text="Set to reply to an existing comment.",
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.author} on '{self.article}'"