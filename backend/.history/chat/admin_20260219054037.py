from django.contrib import admin
from .models import ChatGroup, Message, UserPresence, BlockedUser, PatientComplaint


@admin.register(ChatGroup)
class ChatGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_by', 'member_count', 'created_at')
    search_fields = ('name', 'description', 'created_by__email')
    readonly_fields = ('created_at',)

    # Lets admins add/remove members directly from the group detail page
    filter_horizontal = ('members',)

    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Members'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'group', 'is_read', 'timestamp')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('sender__email', 'receiver__email', 'content')
    readonly_fields = ('timestamp',)


@admin.register(UserPresence)
class UserPresenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'last_seen')
    list_filter = ('status',)
    search_fields = ('user__email',)
    readonly_fields = ('last_seen',)


@admin.register(BlockedUser)
class BlockedUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'blocked_by', 'blocked_user', 'reason', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('blocked_by__email', 'blocked_user__email', 'reason')
    readonly_fields = ('created_at',)


@admin.register(PatientComplaint)
class PatientComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'reported_by', 'patient', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    list_editable = ('status',)
    search_fields = ('reported_by__email', 'patient__email', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Parties', {
            'fields': ('reported_by', 'patient'),
        }),
        ('Complaint', {
            'fields': ('description', 'status'),
        }),
        ('Admin Resolution', {
            'fields': ('admin_notes',),
            'description': 'Internal notes visible only to admins. Not shared with the reporting doctor.',
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )