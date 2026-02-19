from rest_framework import viewsets, permissions
from .models import NewsArticle
from .serializers import NewsArticleSerializer

class NewsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public endpoint to read news. 
    Top news is automatically prioritized by the model's Meta ordering.
    """
    queryset = NewsArticle.objects.all()
    serializer_class = NewsArticleSerializer
    permission_classes = [permissions.AllowAny] # Anyone can read news

    def get_queryset(self):
        queryset = super().get_queryset()
        tag = self.request.query_params.get('tag')
        if tag:
            queryset = queryset.filter(tags__icontains=tag)
        return queryset