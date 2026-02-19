from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_emergency', 'status', 'doctor', 'patient', 'appointment_date', 'appointment_time')
    list_filter = ('status', 'is_emergency', 'appointment_date')
    search_fields = ('doctor__profile__last_name', 'patient__profile__last_name', 'reason')
    list_editable = ('status',)
