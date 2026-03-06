from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from django.db.models import Q
from .models import Appointment


@shared_task
def cleanup_old_appointments():
    """
    Delete appointments that are either:
    - Past appointments older than 30 days (by appointment_date), or
    - Cancelled appointments last updated more than 30 days ago.
    """
    now = timezone.now()
    cutoff_date = now.date() - timedelta(days=30)
    cutoff_dt = now - timedelta(days=30)

    to_delete = Appointment.objects.filter(
        Q(appointment_date__lt=cutoff_date) |
        Q(status=Appointment.Status.CANCELLED, updated_at__lt=cutoff_dt)
    )
    deleted_count, _ = to_delete.delete()
    return deleted_count
