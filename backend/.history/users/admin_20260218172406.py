from django.contrib import admin
from .models import User, Profile, DoctorProfile, PatientProfile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile Information'
    fk_name = 'user'

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # This combines the User and Profile on one screen
    inlines = (ProfileInline,)
    
    list_display = ('email', 'role', 'get_full_name', 'is_verified')
    list_filter = ('role', 'is_verified')
    search_fields = ('email', 'profile__first_name', 'profile__last_name')

    @admin.display(description='Full Name')
    def get_full_name(self, obj):
        # This safely pulls the name from the connected Profile
        if hasattr(obj, 'profile'):
            return f"{obj.profile.first_name} {obj.profile.last_name}"
        return "No Profile Created"

# Keep these to manage specific role data
admin.site.register(DoctorProfile)
admin.site.register(PatientProfile)