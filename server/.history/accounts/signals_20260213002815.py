from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, PatientProfile, DoctorProfile, LabTechnicianProfile, AdminProfile

@receiver(post_save, )