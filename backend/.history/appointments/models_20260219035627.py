from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
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
        'users.PatientProfile', 
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
    
    #clinical note tracking
    clinical_note = models.TextField(blank=True, null=True)
    prescriptions = models.tex
    
    # Internal Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_emergency', 'appointment_date', 'appointment_time']

    def __str__(self):
        prefix = "[EMERGENCY] " if self.is_emergency else ""
        return f"{prefix}{self.patient} -> {self.doctor} ({self.appointment_date})"


class Review(models.Model):
    # Link to appointment to ensure review only happens for an actual visit.
    appointment = models.OneToOneField(
        'appointments.Appointment',
        on_delete=models.CASCADE,
        related_name='review',
    )
    doctor = models.ForeignKey(
        'users.DoctorProfile',
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    patient = models.ForeignKey(
        'users.PatientProfile',
        on_delete=models.CASCADE,
        related_name='given_reviews',
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5",
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['appointment', 'patient'], name='unique_review_per_visit'),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.rating} stars for {self.doctor}"


class AvailabilitySlot(models.Model):
    doctor = models.ForeignKey(
        'users.DoctorProfile',
        on_delete=models.CASCADE,
        related_name='availability_slots',
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['doctor', 'date', 'start_time'], name='unique_doctor_slot'),
        ]
        ordering = ['date', 'start_time']

    def __str__(self):
        status = "Booked" if self.is_booked else "Available"
        return f"{self.doctor} - {self.date} at {self.start_time} ({status})"


