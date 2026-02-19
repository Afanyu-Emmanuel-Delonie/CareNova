from django.contrib import admin
from .models import Appointment, Review, AvailabilitySlot


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_emergency', 'status', 'doctor', 'patient', 'appointment_date', 'appointment_time')
    list_filter = ('status', 'is_emergency', 'appointment_date')
    search_fields = ('doctor__profile__last_name', 'patient__profile__last_name', 'reason')
    list_editable = ('status',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'appointment', 'doctor', 'patient', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = (
        'doctor__profile__first_name',
        'doctor__profile__last_name',
        'patient__profile__first_name',
        'patient__profile__last_name',
        'comment',
    )


@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ('id', 'doctor', 'date', 'start_time', 'end_time', 'is_booked')
    list_filter = ('date', 'is_booked')
    search_fields = (
        'doctor__profile__first_name',
        'doctor__profile__last_name',
        'doctor__specialization',
    )
