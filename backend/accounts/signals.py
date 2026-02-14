from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import (
    User, 
    UserProfile, 
    PatientProfile, 
    DoctorProfile, 
    LabTechnicianProfile, 
    AdminProfile
)
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profiles(sender, instance, created, **kwargs):
    """
    Automatically create appropriate profiles when a new User is created.
    """
    if created:
        try:
            # Create the basic UserProfile for all users
            UserProfile.objects.get_or_create(user=instance)
            logger.info(f"Created UserProfile for {instance.email}")
            
            # Create role-specific profile based on user_type
            if instance.user_type == 'patient':
                PatientProfile.objects.get_or_create(user=instance)
                logger.info(f"Created PatientProfile for {instance.email}")
                
            elif instance.user_type == 'doctor':
                DoctorProfile.objects.get_or_create(user=instance)
                logger.info(f"Created DoctorProfile for {instance.email}")
                
            elif instance.user_type == 'staff':
                LabTechnicianProfile.objects.get_or_create(user=instance)
                logger.info(f"Created LabTechnicianProfile for {instance.email}")
                
            elif instance.user_type == 'admin':
                AdminProfile.objects.get_or_create(user=instance)
                logger.info(f"Created AdminProfile for {instance.email}")
                
        except Exception as e:
            logger.error(f"Error creating profiles for {instance.email}: {str(e)}")


@receiver(post_save, sender=User)
def update_user_profiles(sender, instance, created, **kwargs):
    """
    Handle profile changes when user_type is changed.
    This ensures the correct profile exists for the current user_type.
    """
    if not created:
        try:
            # Ensure UserProfile exists
            if not hasattr(instance, 'profile'):
                UserProfile.objects.get_or_create(user=instance)
            
            # Ensure role-specific profile exists for current user_type
            if instance.user_type == 'patient' and not hasattr(instance, 'patient_profile'):
                PatientProfile.objects.get_or_create(user=instance)
                logger.info(f"Created PatientProfile for existing user {instance.email}")
                
            elif instance.user_type == 'doctor' and not hasattr(instance, 'doctor_profile'):
                DoctorProfile.objects.get_or_create(user=instance)
                logger.info(f"Created DoctorProfile for existing user {instance.email}")
                
            elif instance.user_type == 'staff' and not hasattr(instance, 'lab_technician_profile'):
                LabTechnicianProfile.objects.get_or_create(user=instance)
                logger.info(f"Created LabTechnicianProfile for existing user {instance.email}")
                
            elif instance.user_type == 'admin' and not hasattr(instance, 'admin_profile'):
                AdminProfile.objects.get_or_create(user=instance)
                logger.info(f"Created AdminProfile for existing user {instance.email}")
                
        except Exception as e:
            logger.error(f"Error updating profiles for {instance.email}: {str(e)}")