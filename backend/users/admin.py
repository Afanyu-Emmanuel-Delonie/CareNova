from django.contrib import admin
from .models import User, Profile, DoctorProfile, PatientProfile, Category


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile Info'

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    inlines = (ProfileInline,)
    
    list_display = ('email', 'role', 'get_full_name', 'is_verified', 'is_active')
    list_filter = ('role', 'is_verified', 'is_active')
    search_fields = ('email', 'profile__first_name', 'profile__last_name')
    ordering = ('email',)

    @admin.display(description='Full Name')
    def get_full_name(self, obj):
        if hasattr(obj, 'profile'):
            return f"{obj.profile.first_name} {obj.profile.last_name}"
        return "No Profile"

@admin.register(DoctorProfile)
class DoctorAdmin(admin.ModelAdmin):
    # obj.profile accesses the Profile model, which then accesses the User model email
    list_display = ('get_name', 'get_email', 'category', 'specialization', 'is_verified')
    list_filter = ('category', 'specialization', 'is_verified')
    search_fields = ('profile__last_name', 'profile__user__email', 'specialization', 'category__name')
    list_editable = ('is_verified',)

    @admin.display(description='Doctor Name')
    def get_name(self, obj):
        return f"{obj.profile.first_name} {obj.profile.last_name}"

    @admin.display(description='Email')
    def get_email(self, obj):
        return obj.profile.user.email


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(PatientProfile)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'get_email', 'blood_group', 'emergency_contact')
    search_fields = ('profile__last_name', 'profile__user__email')

    @admin.display(description='Patient Name')
    def get_name(self, obj):
        return f"{obj.profile.first_name} {obj.profile.last_name}"

    @admin.display(description='Email')
    def get_email(self, obj):
        return obj.profile.user.email

