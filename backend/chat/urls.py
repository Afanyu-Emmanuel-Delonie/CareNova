from django.urls import path
from .views import (
    ChatGroupViewSet,
    PrivateChatViewSet,
    UserPresenceViewSet,
    BlockedUserViewSet,
    PatientComplaintViewSet,
)

urlpatterns = [

    # ── Chat Groups ─────────────────────────────────────────────────────────
    path(
        'groups/',
        ChatGroupViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='chat-group-list-create',
    ),
    path(
        'groups/<int:pk>/',
        ChatGroupViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy',
        }),
        name='chat-group-detail',
    ),
    path(
        'groups/<int:pk>/join/',
        ChatGroupViewSet.as_view({'post': 'join'}),
        name='chat-group-join',
    ),
    path(
        'groups/<int:pk>/messages/',
        ChatGroupViewSet.as_view({'get': 'messages'}),
        name='chat-group-messages',
    ),

    # ── Private Chat ────────────────────────────────────────────────────────
    # NOTE: 'send/' and 'history/' are collection-level (no <pk>) and must
    # come before any hypothetical <pk> pattern — kept here for consistency.
    path(
        'private/',
        PrivateChatViewSet.as_view({'get': 'list'}),
        name='private-chat-inbox',
    ),
    path(
        'private/send/',
        PrivateChatViewSet.as_view({'post': 'send_private_message'}),
        name='private-chat-send',
    ),
    path(
        'private/history/<int:other_user_id>/',
        PrivateChatViewSet.as_view({'get': 'history'}),
        name='private-chat-history',
    ),

    # ── Presence ────────────────────────────────────────────────────────────
    # set-status is a collection-level action; must come before <int:pk>.
    path(
        'presence/',
        UserPresenceViewSet.as_view({'get': 'list'}),
        name='presence-list',
    ),
    path(
        'presence/set-status/',
        UserPresenceViewSet.as_view({'post': 'set_status'}),
        name='presence-set-status',
    ),
    path(
        'presence/<int:pk>/',
        UserPresenceViewSet.as_view({'get': 'retrieve'}),
        name='presence-detail',
    ),

    # ── Moderation — Blocking ───────────────────────────────────────────────
    # block/ and unblock/ are collection-level; must come before <int:pk>.
    path(
        'moderation/blocked/',
        BlockedUserViewSet.as_view({'get': 'list'}),
        name='blocked-list',
    ),
    path(
        'moderation/blocked/block/',
        BlockedUserViewSet.as_view({'post': 'block_user'}),
        name='blocked-block',
    ),
    path(
        'moderation/blocked/unblock/',
        BlockedUserViewSet.as_view({'post': 'unblock_user'}),
        name='blocked-unblock',
    ),

    # ── Moderation — Complaints ─────────────────────────────────────────────
    # file/ is a collection-level action; must come before <int:pk>.
    path(
        'moderation/complaints/',
        PatientComplaintViewSet.as_view({'get': 'list'}),
        name='complaint-list',
    ),
    path(
        'moderation/complaints/file/',
        PatientComplaintViewSet.as_view({'post': 'file_complaint'}),
        name='complaint-file',
    ),
    path(
        'moderation/complaints/<int:pk>/',
        PatientComplaintViewSet.as_view({'get': 'retrieve'}),
        name='complaint-detail',
    ),
    path(
        'moderation/complaints/<int:pk>/resolve/',
        PatientComplaintViewSet.as_view({'patch': 'resolve_complaint'}),
        name='complaint-resolve',
    ),
]