from django.contrib import admin
from .models import User 

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'role', 'is_verified', 'is_active', 'is_staff')
    list_filter = ('role', 'is_verified', 'is_active')
    search_fields = ('email',)
    ordering = ('email',)
    
@admin.register(DoctorProfile)
class DoctorAdmin(admin.ModelAdmin):
    # Pulling names from the related profile model
    list_display = ('get_name', 'specialization', 'license_number', 'is_verified')
    list_filter = ('specialization', 'is_verified')
    search_fields = ('profile__last_name', 'specialization', 'license_number')
    # This allows you to verify doctors directly from the list view
    list_editable = ('is_verified',)

    @admin.display(description='Doctor Name')
    def get_name(self, obj):
        return f"{obj.profile.first_name} {obj.profile.last_name}"

@admin.register(PatientProfile)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'blood_group', 'emergency_contact')
    search_fields = ('profile__last_name', 'blood_group')

    @admin.display(description='Patient Name')
    def get_name(self, obj):
        return f"{obj.profile.first_name} {obj.profile.last_name}"

# Register the base Profile as well
admin.site.register(Profile)

    