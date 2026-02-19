from django.utils.http import urlencode
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes

from .models import NewsArticle, ArticleParagraph, ArticleLike, ArticleComment
from .serializers import (
    NewsArticleSerializer, NewsArticleWriteSerializer,
    ArticleParagraphSerializer, ArticleCommentSerializer,
)


# ── Permission helper ───────────────────────────────────────────────────────

def is_editor(user):
    """Doctors and admins may create/edit/delete articles."""
    return user.is_authenticated and (user.is_staff or getattr(user, 'role', None) in ('DOCTOR', 'ADMIN'))


# ── News ─────────────────────────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(
        summary="List news articles",
        description=(
            "Returns all published news articles ordered by top-news priority then recency. "
            "Optionally filter by tag using the `tag` query parameter."
        ),
        parameters=[
            OpenApiParameter(
                name="tag",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter articles whose tags field contains this value (case-insensitive).",
                required=False,
            ),
        ],
        responses={200: NewsArticleSerializer(many=True)},
        tags=["News"],
    ),
    retrieve=extend_schema(
        summary="Retrieve a news article",
        description="Returns the full article including all ordered paragraphs, like count, and comments count.",
        responses={
            200: NewsArticleSerializer,
            404: OpenApiResponse(description="Article not found."),
        },
        tags=["News"],
    ),
    create=extend_schema(
        summary="Create a news article",
        description=(
            "Admin or doctor only. Creates a new article. "
            "Paragraphs can be submitted inline as a nested list and will be created in the provided order."
        ),
        request=NewsArticleWriteSerializer,
        responses={
            201: NewsArticleSerializer,
            403: OpenApiResponse(description="Only admins and doctors can create articles."),
        },
        tags=["News"],
    ),
    update=extend_schema(
        summary="Update a news article",
        description=(
            "Admin or doctor only. Fully replaces the article. "
            "If `paragraphs` is included, existing paragraphs are deleted and replaced."
        ),
        request=NewsArticleWriteSerializer,
        responses={
            200: NewsArticleSerializer,
            403: OpenApiResponse(description="Only admins and doctors can edit articles."),
        },
        tags=["News"],
    ),
    partial_update=extend_schema(
        summary="Partially update a news article",
        description="Admin or doctor only. Updates only the supplied fields. Paragraphs are replaced if included.",
        request=NewsArticleWriteSerializer,
        responses={
            200: NewsArticleSerializer,
            403: OpenApiResponse(description="Only admins and doctors can edit articles."),
        },
        tags=["News"],
    ),
    destroy=extend_schema(
        summary="Delete a news article",
        description="Admin or doctor only. Permanently deletes the article and all its paragraphs, likes, and comments.",
        responses={
            204: OpenApiResponse(description="Article deleted."),
            403: OpenApiResponse(description="Only admins and doctors can delete articles."),
        },
        tags=["News"],
    ),
)
class NewsViewSet(viewsets.ModelViewSet):
    queryset = NewsArticle.objects.all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return NewsArticleWriteSerializer
        return NewsArticleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        tag = self.request.query_params.get('tag')
        if tag:
            queryset = queryset.filter(tags__icontains=tag)
        return queryset

    def check_editor_permission(self):
        if not is_editor(self.request.user):
            self.permission_denied(self.request, message="Only admins and doctors can perform this action.")

    def perform_create(self, serializer):
        self.check_editor_permission()
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        self.check_editor_permission()
        serializer.save()

    def perform_destroy(self, instance):
        self.check_editor_permission()
        instance.delete()

    # ── Paragraphs ────────────────────────────────────────────────────────

    @extend_schema(
        summary="Add a paragraph to an article",
        description="Admin or doctor only. Appends a new paragraph block to the article.",
        request=ArticleParagraphSerializer,
        responses={
            201: ArticleParagraphSerializer,
            403: OpenApiResponse(description="Only admins and doctors can add paragraphs."),
        },
        tags=["News"],
    )
    @action(detail=True, methods=['post'], url_path='paragraphs')
    def add_paragraph(self, request, pk=None):
        self.check_editor_permission()
        article = self.get_object()
        serializer = ArticleParagraphSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(article=article)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete a paragraph from an article",
        description="Admin or doctor only. Deletes a specific paragraph by its ID.",
        request=None,
        responses={
            204: OpenApiResponse(description="Paragraph deleted."),
            403: OpenApiResponse(description="Only admins and doctors can delete paragraphs."),
            404: OpenApiResponse(description="Paragraph not found on this article."),
        },
        parameters=[
            OpenApiParameter(
                name="paragraph_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description="ID of the paragraph to delete.",
            ),
        ],
        tags=["News"],
    )
    @action(detail=True, methods=['delete'], url_path='paragraphs/(?P<paragraph_id>[^/.]+)')
    def delete_paragraph(self, request, pk=None, paragraph_id=None):
        self.check_editor_permission()
        article = self.get_object()
        try:
            paragraph = article.paragraphs.get(pk=paragraph_id)
        except ArticleParagraph.DoesNotExist:
            return Response({"error": "Paragraph not found."}, status=status.HTTP_404_NOT_FOUND)
        paragraph.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ── Likes ─────────────────────────────────────────────────────────────

    @extend_schema(
        summary="Toggle like on an article",
        description=(
            "Authenticated users can like or unlike an article. "
            "Calling this endpoint when already liked removes the like (toggle behaviour)."
        ),
        request=None,
        responses={
            200: OpenApiResponse(description="Like toggled. Returns current like count and liked status."),
            401: OpenApiResponse(description="Authentication required."),
        },
        tags=["News"],
    )
    @action(detail=True, methods=['post'], url_path='like', permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        article = self.get_object()
        like, created = ArticleLike.objects.get_or_create(article=article, user=request.user)
        if not created:
            like.delete()
            liked = False
        else:
            liked = True
        return Response({
            "liked": liked,
            "like_count": article.likes.count(),
        }, status=status.HTTP_200_OK)

    # ── Comments ──────────────────────────────────────────────────────────

    @extend_schema(
        summary="List comments on an article",
        description="Returns all top-level comments with their replies nested one level deep.",
        responses={200: ArticleCommentSerializer(many=True)},
        tags=["News"],
    )
    @action(detail=True, methods=['get'], url_path='comments')
    def list_comments(self, request, pk=None):
        article = self.get_object()
        # Only top-level comments; replies are nested inside via serializer
        top_level = article.comments.filter(parent__isnull=True)
        serializer = ArticleCommentSerializer(top_level, many=True, context={'request': request})
        return Response(serializer.data)

    @extend_schema(
        summary="Post a comment on an article",
        description=(
            "Authenticated users can post a comment. "
            "To reply to an existing comment, include `parent` (comment ID) in the request body."
        ),
        request=ArticleCommentSerializer,
        responses={
            201: ArticleCommentSerializer,
            400: OpenApiResponse(description="Validation error."),
            401: OpenApiResponse(description="Authentication required."),
        },
        tags=["News"],
    )
    @action(detail=True, methods=['post'], url_path='comments/add', permission_classes=[permissions.IsAuthenticated])
    def add_comment(self, request, pk=None):
        article = self.get_object()
        serializer = ArticleCommentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(article=article, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete a comment",
        description="The comment author or an admin can delete a comment. Deleting a parent also deletes its replies.",
        request=None,
        parameters=[
            OpenApiParameter(
                name="comment_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description="ID of the comment to delete.",
            ),
        ],
        responses={
            204: OpenApiResponse(description="Comment deleted."),
            403: OpenApiResponse(description="You can only delete your own comments."),
            404: OpenApiResponse(description="Comment not found on this article."),
        },
        tags=["News"],
    )
    @action(
        detail=True, methods=['delete'],
        url_path='comments/(?P<comment_id>[^/.]+)',
        permission_classes=[permissions.IsAuthenticated],
    )
    def delete_comment(self, request, pk=None, comment_id=None):
        article = self.get_object()
        try:
            comment = article.comments.get(pk=comment_id)
        except ArticleComment.DoesNotExist:
            return Response({"error": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)

        if comment.author != request.user and not is_editor(request.user):
            return Response({"error": "You can only delete your own comments."}, status=status.HTTP_403_FORBIDDEN)

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ── Share ─────────────────────────────────────────────────────────────

    @extend_schema(
        summary="Get social share links for an article",
        description=(
            "Generates ready-to-use share URLs for major social platforms. "
            "The `base_url` query parameter should be the public URL of the article page on your frontend. "
            "Returns links for Facebook, Twitter/X, WhatsApp, Telegram, LinkedIn, and Reddit."
        ),
        parameters=[
            OpenApiParameter(
                name="base_url",
                type=OpenApiTypes.URI,
                location=OpenApiParameter.QUERY,
                description="The full public URL of the article on your frontend (e.g. https://carenova.com/news/my-article).",
                required=True,
            ),
        ],
        responses={
            200: OpenApiResponse(description="Share links for each supported platform."),
            400: OpenApiResponse(description="base_url is required."),
        },
        tags=["News"],
    )
    @action(detail=True, methods=['get'], url_path='share')
    def share(self, request, pk=None):
        article = self.get_object()
        base_url = request.query_params.get('base_url')
        if not base_url:
            return Response({"error": "base_url is required."}, status=status.HTTP_400_BAD_REQUEST)

        title = article.title

        share_links = {
            "facebook": f"https://www.facebook.com/sharer/sharer.php?{urlencode({'u': base_url})}",
            "twitter": f"https://twitter.com/intent/tweet?{urlencode({'url': base_url, 'text': title})}",
            "whatsapp": f"https://api.whatsapp.com/send?{urlencode({'text': f'{title} {base_url}'})}",
            "telegram": f"https://t.me/share/url?{urlencode({'url': base_url, 'text': title})}",
            "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?{urlencode({'url': base_url})}",
            "reddit": f"https://reddit.com/submit?{urlencode({'url': base_url, 'title': title})}",
            "copy_link": base_url,
        }

        return Response({
            "article": article.title,
            "share_links": share_links,
        })