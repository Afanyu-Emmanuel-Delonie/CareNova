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
        except User.DoesNotExist as e:
            raise serializers.ValidationError("Sorry User does not exist") 
        
        try:
            otp = OTP.objects.filter(user=user, code=code, is_used=False).latest("created_at")
        except OTP.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP.")

        if not otp.is_valid():
            raise serializers.ValidationError("OTP expired or already used.")
        
        data["user"] = user
        data["otp"] = otp 
        
        return data 
    
class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ["email", "password"]
        
        def create()
        