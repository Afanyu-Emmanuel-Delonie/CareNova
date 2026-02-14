from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin for User model.
    """
    
    list_display = ['email', 'first_name', 'last_name', 'user_type', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'user_type', 'is_verified']
    search_fields = ['email', 'first_name', 'last_name', 'phone_number']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'phone_number', 'date_of_birth', 'address', 'profile_picture')}),
        (_('User Type'), {'fields': ('user_type',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        (_('Important Dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'user_type', 'is_staff', 'is_active'),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin for UserProfile model.
    """
    
    list_display = ['user', 'blood_group', 'specialization', 'department', 'license_number']
    search_fields = ['user__email', 'license_number', 'specialization']
    list_filter = ['blood_group', 'notifications_enabled', 'sms_notifications_enabled']
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Health Information', {'fields': ('blood_group', 'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship')}),
        ('Professional Information', {'fields': ('license_number', 'specialization', 'department', 'years_of_experience')}),
        ('Additional Info', {'fields': ('bio',)}),
        ('Settings', {'fields': ('notifications_enabled', 'sms_notifications_enabled')}),
    )