from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import (
    User, 
    OTP,
    UserProfile, 
    PatientProfile, 
    DoctorProfile, 
    LabTechnicianProfile, 
    AdminProfile
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
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


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ['email', 'otp_code', 'purpose', 'is_verified', 'created_at', 'expires_at']
    list_filter = ['purpose', 'is_verified', 'created_at']
    search_fields = ['email', 'otp_code']
    ordering = ['-created_at']
    readonly_fields = ['created_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'notifications_enabled', 'sms_notifications_enabled']
    search_fields = ['user__email']


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'blood_group', 'insurance_provider', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'insurance_policy_number']
    list_filter = ['blood_group', 'created_at']


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'license_number', 'years_of_experience', 'available_for_consultation']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'license_number', 'specialization']
    list_filter = ['specialization', 'available_for_consultation', 'department']


@admin.register(LabTechnicianProfile)
class LabTechnicianProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'license_number', 'department', 'years_of_experience']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'license_number']
    list_filter = ['department', 'specialization']


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'designation', 'department']
    search_fields = ['user__email', 'employee_id', 'designation']
    list_filter = ['department', 'can_manage_users', 'can_manage_billing']