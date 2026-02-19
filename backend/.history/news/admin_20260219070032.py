from django.contrib import admin
from .models import NewsArticle

@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_top_news', 'created_at')
    list_filter = ('is_top_news', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}