from rest_framework import serializers
from .models import User, PatientProfile, DoctorProfile, LabTechnicianProfile, AdminProfile, OTP
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model

user = get_user_model()

class VerifyOtpSerilizer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    
    def validate(self, data):
        email = data.get("email")
        code = data.get("code")
        
        try:
            user = User.objects.get(email=email)
        except 