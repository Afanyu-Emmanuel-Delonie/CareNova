from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Profile, DoctorProfile, PatientProfile

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Step 1: Create the base Profile
        profile = Profile.objects.create(user=instance)
        
        # Step 2: Create role-specific profile
        # Note: Access the role directly from the instance
        if instance.role == 'DOCTOR':
            DoctorProfile.objects.create(profile=profile)
        elif instance.role == 'PATIENT':
            PatientProfile.objects.create(profile=profile)