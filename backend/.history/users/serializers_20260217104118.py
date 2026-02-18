from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Profile, DoctorProfile, PatientProfile

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'role']
    
    def create(self, validate_data):
        user = User.objects.create_user(**validate_data)
        return user
    
class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        if not self.user.is_verified:
            raise serializers.ValidationError("Account is not verified. Please verify your email first.")
        
        data['user_id'] = self.user.id
        data['role'] = self.user.role
        data['is_verified'] = self.user.is_verified
        
        return data

class DoctorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorProfile
        fields = ['specialization', 'license_number', 'bio', 'is_verified']
        read_only_fields = ['is_verified']
        
class PatientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientProfile
        fields = ['date_of_birth', 'blood_group', 'allergies', 'emergency_contact']
        
class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=False)
    role = serializers.CharField(source='user.role', read_only=True)
    
    # this section will handle just doctor specific profile data 
    doctor_data = DoctorProfileSerializer(required=False)
    patient_data = PatientProfileSerializer(required=False)
    
    class Meta:
        model = Profile
        fields = ['email', 'role', 'first_name', 'last_name', 'phone_number', 
                  'address', 'profile_picture', 'doctor_data', 'patient_data']
    
    def update(self, instance, validated_data):
        doctor_data = validated_data('doctor_data', None)
        patient_data = validated_data.pop('patient_data', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
 
