from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Appointment


@receiver(post_save, sender=Appointment)
def alert_admin_of_emergency(sender, instance, created, **kwargs):
    if created and instance.is_emergency:
        # Hook: replace this print with WebSocket/email notification logic.
        print(f"ALERT: New Emergency Appointment {instance.id} requires monitoring.")
