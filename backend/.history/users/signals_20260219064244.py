from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Profile, DoctorProfile, PatientProfile
from appointments.models import Appointment
from .notifications import AppointmentNotifications

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        
        if instance.role == 'DOCTOR':
            DoctorProfile.objects.create(profile=profile)
        elif instance.role == 'PATIENT':
            PatientProfile.objects.create(profile=profile)
            
@receiver(post_save, sender=Appointment)
def trigger_appointment_emails(sender, instance, created, **kwargs):
    if created:
        # If it's a new appointment, send confirmation to patient
        AppointmentNotifications.send_confirmation(instance)
        
        # If it's marked as an emergency, notify the doctor immediately
        if instance.is_emergency:
            AppointmentNotifications.send_emergency_alert(instance)

