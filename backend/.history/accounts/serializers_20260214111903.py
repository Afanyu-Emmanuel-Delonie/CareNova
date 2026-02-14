# accounts/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import OTP, PatientProfile, DoctorProfile, LabTechnicianProfile, AdminProfile

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        help_text="Password must be at least 8 characters"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Confirm your password"
    )
    
    class LoginSerializer(serializers.Serializer):
        email = serializers.EmailField(required=True)
        password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'})
        
        
    
    class Meta:
        model = User
        fields = [
            'email', 
            'password', 
            'password_confirm',
            'first_name', 
            'last_name', 
            'phone_number',
            'user_type',
            'date_of_birth',
            'address'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'user_type': {'required': True},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'phone_number': {'required': False},
            'date_of_birth': {'required': False},
            'address': {'required': False}
        }
    
    def validate_email(self, value):
        """Check if email already exists"""
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()
    
    def validate_user_type(self, value):
        """Validate user_type choice"""
        valid_types = ['patient', 'doctor', 'nurse', 'admin', 'staff']
        if value not in valid_types:
            raise serializers.ValidationError(
                f"Invalid user type. Must be one of: {', '.join(valid_types)}"
            )
        return value
    
    def validate(self, attrs):
        """Validate that passwords match"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password_confirm": "Password fields didn't match."
            })
        return attrs
    
    def create(self, validated_data):
        """Create user with hashed password"""
        # Remove password_confirm as it's not needed for user creation
        validated_data.pop('password_confirm', None)
        
        # Create user
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', ''),
            user_type=validated_data['user_type'],
            date_of_birth=validated_data.get('date_of_birth'),
            address=validated_data.get('address', ''),
            is_active=True,
            is_verified=False  # User needs to verify email
        )
        return user


class OTPVerificationSerializer(serializers.Serializer):
    """Serializer for OTP verification"""
    
    email = serializers.EmailField(required=True)
    otp_code = serializers.CharField(
        required=True, 
        min_length=6, 
        max_length=6,
        help_text="6-digit OTP code"
    )
    
    def validate_otp_code(self, value):
        """Ensure OTP code is numeric"""
        if not value.isdigit():
            raise serializers.ValidationError("OTP code must be numeric.")
        return value
    
    def validate_email(self, value):
        """Normalize email"""
        return value.lower()


class ResendOTPSerializer(serializers.Serializer):
    """Serializer for resending OTP"""
    
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Check if user exists and normalize email"""
        email = value.lower()
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return email


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model - for retrieving user data"""
    
    full_name = serializers.SerializerMethodField()
    age = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'phone_number',
            'date_of_birth',
            'age',
            'address',
            'profile_picture',
            'user_type',
            'is_active',
            'is_verified',
            'date_joined',
            'last_login'
        ]
        read_only_fields = [
            'id',
            'is_active',
            'is_verified',
            'date_joined',
            'last_login'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'phone_number',
            'date_of_birth',
            'address',
            'profile_picture'
        ]


class PatientProfileSerializer(serializers.ModelSerializer):
    """Serializer for Patient Profile"""
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = PatientProfile
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']


class DoctorProfileSerializer(serializers.ModelSerializer):
    """Serializer for Doctor Profile"""
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = DoctorProfile
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']


class LabTechnicianProfileSerializer(serializers.ModelSerializer):
    """Serializer for Lab Technician Profile"""
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = LabTechnicianProfile
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']


class AdminProfileSerializer(serializers.ModelSerializer):
    """Serializer for Admin Profile"""
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = AdminProfile
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for requesting password reset"""
    
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Check if user exists"""
        email = value.lower()
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return email


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for confirming password reset with OTP"""
    
    email = serializers.EmailField(required=True)
    otp_code = serializers.CharField(required=True, min_length=6, max_length=6)
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate_otp_code(self, value):
        """Ensure OTP code is numeric"""
        if not value.isdigit():
            raise serializers.ValidationError("OTP code must be numeric.")
        return value
    
    def validate(self, attrs):
        """Validate that passwords match"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                "new_password_confirm": "Password fields didn't match."
            })
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password (when user is logged in)"""
    
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        """Validate that new passwords match"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                "new_password_confirm": "Password fields didn't match."
            })
        return attrs
    
    def validate_old_password(self, value):
        """Validate old password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value
    
    