from django.contrib import admin
from .models import NewsArticle, ArticleParagraph, ArticleLike, ArticleComment


class ArticleParagraphInline(admin.StackedInline):
    model = ArticleParagraph
    extra = 1
    fields = ('order', 'subheading', 'body', 'image')
    ordering = ('order',)


class ArticleCommentInline(admin.TabularInline):
    model = ArticleComment
    extra = 0
    readonly_fields = ('author', 'body', 'parent', 'created_at')
    can_delete = True


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'is_top_news', 'like_count', 'comment_count', 'created_at')
    list_filter = ('is_top_news', 'created_at')
    list_editable = ('is_top_news',)
    search_fields = ('title', 'content', 'tags', 'author__email')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ArticleParagraphInline, ArticleCommentInline]
    fieldsets = (
        ('Article', {
            'fields': ('title', 'slug', 'author', 'content', 'image', 'tags', 'is_top_news'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def like_count(self, obj):
        return obj.likes.count()
    like_count.short_description = 'Likes'

    def comment_count(self, obj):
        return obj.comments.count()
    comment_count.short_description = 'Comments'


@admin.register(ArticleComment)
class ArticleCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'article', 'parent', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('author__email', 'body', 'article__title')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ArticleLike)
class ArticleLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'article', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'article__title')
    readonly_fields = ('created_at',)