from rest_framework import serializers
from .models import User, PatientProfile, DoctorProfile, LabTechnicianProfile, AdminProfile, OTP
from django.contrib.auth.password_validation import validate_password
from