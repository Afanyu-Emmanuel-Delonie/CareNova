from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import NewsArticle, ArticleParagraph, ArticleLike, ArticleComment


class ArticleParagraphSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleParagraph
        fields = ['id', 'order', 'subheading', 'body', 'image']


class ArticleCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = ArticleComment
        fields = ['id', 'author', 'author_name', 'parent', 'body', 'replies', 'created_at', 'updated_at']
        read_only_fields = ['author', 'created_at', 'updated_at']

    @extend_schema_field(str)
    def get_author_name(self, obj):
        profile = obj.author.profile
        return f"{profile.first_name} {profile.last_name}"

    @extend_schema_field(ArticleCommentSerializer(many=True))
    def get_replies(self, obj):
        # Only serialize one level deep; parent comments include their direct replies
        if obj.parent is None:
            return ArticleCommentSerializer(
                obj.replies.all(), many=True, context=self.context
            ).data
        return []


class NewsArticleSerializer(serializers.ModelSerializer):
    paragraphs = ArticleParagraphSerializer(many=True, read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = NewsArticle
        fields = [
            'id', 'title', 'slug', 'content', 'image',
            'is_top_news', 'tags',
            'author', 'author_name',
            'paragraphs',
            'like_count', 'comment_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['slug', 'author', 'created_at', 'updated_at']

    @extend_schema_field(str)
    def get_author_name(self, obj):
        if obj.author and hasattr(obj.author, 'profile'):
            profile = obj.author.profile
            return f"{profile.first_name} {profile.last_name}"
        return None


class NewsArticleWriteSerializer(serializers.ModelSerializer):
    """
    Used for create/update operations. Accepts nested paragraphs so
    the entire article body can be submitted in one request.
    """
    paragraphs = ArticleParagraphSerializer(many=True, required=False)

    class Meta:
        model = NewsArticle
        fields = ['title', 'content', 'image', 'is_top_news', 'tags', 'paragraphs']

    def create(self, validated_data):
        paragraphs_data = validated_data.pop('paragraphs', [])
        article = NewsArticle.objects.create(**validated_data)
        for para in paragraphs_data:
            ArticleParagraph.objects.create(article=article, **para)
        return article

    def update(self, instance, validated_data):
        paragraphs_data = validated_data.pop('paragraphs', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if paragraphs_data is not None:
            # Full replacement: delete existing and recreate
            instance.paragraphs.all().delete()
            for para in paragraphs_data:
                ArticleParagraph.objects.create(article=instance, **para)

        return instance