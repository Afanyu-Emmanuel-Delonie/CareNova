from django.db import models
from django.utils.text import slugify

class NewsArticle(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='news_images/', null=True, blank=True)
    is_top_news = models.BooleanField(default=False)
    tags = models.CharField(
    max_length=100, 
    help_text="Comma separated tags e.g. Health, COVID-19"
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