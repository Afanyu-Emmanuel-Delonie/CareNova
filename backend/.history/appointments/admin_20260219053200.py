from django.contrib import admin
from .models import Appointment, Review, AvailabilitySlot


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'is_emergency',
        'is_recurring',
        'occurrence_number',
        'status',
        'doctor',
        'patient',
        'appointment_date',
        'appointment_time',
    )
    list_filter = (
        'status',
        'is_emergency',
        'is_recurring',
        'appointment_date',
    )
    search_fields = (
        'doctor__profile__last_name',
        'patient__profile__last_name',
        'reason',
        'recurrence_group_id',
    )
    list_editable = ('status',)
    readonly_fields = (
        'recurrence_group_id',
        'occurrence_number',
        'created_at',
        'updated_at',
    )
    fieldsets = (
        ('Participants', {
            'fields': ('doctor', 'patient'),
        }),
        ('Schedule', {
            'fields': ('appointment_date', 'appointment_time', 'status'),
        }),
        ('Priority & Reason', {
            'fields': ('is_emergency', 'reason'),
        }),
        ('Recurrence', {
            'fields': ('is_recurring', 'recurrence_group_id', 'occurrence_number'),
            'classes': ('collapse',),
        }),
        ('Clinical Notes', {
            'fields': ('clinical_note', 'prescriptions'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'appointment', 'doctor', 'patient', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    readonly_fields = ('created_at',)
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
    list_editable = ('is_booked',)
    search_fields = (
        'doctor__profile__first_name',
        'doctor__profile__last_name',
        'doctor__specialization',
    )