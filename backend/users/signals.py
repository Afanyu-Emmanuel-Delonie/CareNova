from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Profile
from appointments.models import Appointment
from .notifications import AppointmentNotifications

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance,
            first_name='',
            last_name='',
        )
            
@receiver(post_save, sender=Appointment)
def trigger_appointment_emails(sender, instance, created, **kwargs):
    if created:
        AppointmentNotifications.send_confirmation(instance)
        
        if instance.is_emergency:
            AppointmentNotifications.send_emergency_alert(instance)
