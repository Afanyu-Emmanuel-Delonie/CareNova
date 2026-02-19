from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from ...models import Profile, DoctorProfile, PatientProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    profile = Profile.object.create(user)
