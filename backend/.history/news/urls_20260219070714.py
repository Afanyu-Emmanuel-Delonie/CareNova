from django.urls import path
from .views import NewsViewSet

urlpatterns = [

    # ── News Articles ────────────────────────────────────────────────────────
    path(
        'news/',
        NewsViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='news-list-create',
    ),
    path(
        'news/<int:pk>/',
        NewsViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
        name='news-detail',
    ),

    # ── Paragraphs ───────────────────────────────────────────────────────────
    # add_paragraph and delete_paragraph must be ordered: fixed string before <paragraph_id>
    path(
        'news/<int:pk>/paragraphs/',
        NewsViewSet.as_view({'post': 'add_paragraph'}),
        name='news-paragraph-add',
    ),
    path(
        'news/<int:pk>/paragraphs/<int:paragraph_id>/',
        NewsViewSet.as_view({'delete': 'delete_paragraph'}),
        name='news-paragraph-delete',
    ),

    # ── Likes ────────────────────────────────────────────────────────────────
    path(
        'news/<int:pk>/like/',
        NewsViewSet.as_view({'post': 'like'}),
        name='news-like',
    ),

    # ── Comments ─────────────────────────────────────────────────────────────
    # list and add are collection-level; delete targets a specific comment.
    path(
        'news/<int:pk>/comments/',
        NewsViewSet.as_view({'get': 'list_comments'}),
        name='news-comments-list',
    ),
    path(
        'news/<int:pk>/comments/add/',
        NewsViewSet.as_view({'post': 'add_comment'}),
        name='news-comments-add',
    ),
    path(
        'news/<int:pk>/comments/<int:comment_id>/',
        NewsViewSet.as_view({'delete': 'delete_comment'}),
        name='news-comments-delete',
    ),

    # ── Share ────────────────────────────────────────────────────────────────
    path(
        'news/<int:pk>/share/',
        NewsViewSet.as_view({'get': 'share'}),
        name='news-share',
    ),
]