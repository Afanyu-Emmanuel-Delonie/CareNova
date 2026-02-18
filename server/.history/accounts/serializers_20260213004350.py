from rest_framework import serializers
from .models import User, PatientProfile, DoctorProfile, LabTechnicianProfile, AdminProfile
from django.contrib.auth.password_validation import validate_password

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
