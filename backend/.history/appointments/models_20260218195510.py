from django.db import models
from django.utils.translation import gettext_lazy as _

class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        CONFIRMED = 'CONFIRMED', _('Confirmed')
        CANCELLED = 'CANCELLED', _('Cancelled')
        COMPLETED = 'COMPLETED', _('Completed')

    # Links to our existing profiles
    doctor = models.ForeignKey(
        'users.DoctorProfile', 
        on_delete=models.CASCADE, 
        related_name='doctor_appointments'
    )
    patient = models.ForeignKey(
        'profiles.PatientProfile', 
        on_delete=models.CASCADE, 
        related_name='patient_appointments'
    )

    # Schedule details
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    
    # Priority & Routing
    is_emergency = models.BooleanField(default=False)
    reason = models.TextField(help_text=_("Patient's description of the issue"))
    
    # Management
    status = models.CharField(
        max_length=15, 
        choices=Status.choices, 
        default=Status.PENDING
    )
    
    # Internal Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_emergency', 'appointment_date', 'appointment_time']

    def __str__(self):
        prefix = "[EMERGENCY] " if self.is_emergency else ""
        return f"{prefix}{self.patient} -> {self.doctor} ({self.appointment_date})"
