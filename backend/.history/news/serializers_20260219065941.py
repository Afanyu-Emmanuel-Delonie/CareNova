from rest_framework import serializers
from .models import NewsArticle

class NewsArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsArticle
        fields = [
            'id', 'title', 'slug', 'content', 'image', 
            'is_top_news', 'tags', 'created_at'
        ]