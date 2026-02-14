from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration with username"""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        help_text="Password must be at least 8 characters"
    )
    
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'role']
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'role': {'required': True}
        }
    
    def validate_email(self, value):
        """Check if email already exists"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()
    
    def validate_username(self, value):
        """Check if username already exists"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value
    
    def validate_role(self, value):
        """Validate role choice"""
        valid_roles = ['PATIENT', 'DOCTOR', 'LAB_TECH', 'ADMIN']
        if value not in valid_roles:
            raise serializers.ValidationError(
                f"Invalid role. Must be one of: {', '.join(valid_roles)}"
            )
        return value
    
    def create(self, validated_data):
        """Create user with hashed password"""
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            role=validated_data['role']
        )
        return user


class OTPVerificationSerializer(serializers.Serializer):
    """Serializer for OTP verification"""
    
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True, min_length=6, max_length=6)
    otp_type = serializers.ChoiceField(
        required=True,
        choices=['EMAIL_VERIFICATION', 'PASSWORD_RESET', 'LOGIN_OTP']
    )
    
    def validate_code(self, value):
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
    otp_type = serializers.ChoiceField(
        required=True,
        choices=['EMAIL_VERIFICATION', 'PASSWORD_RESET', 'LOGIN_OTP']
    )
    
    def validate_email(self, value):
        """Check if user exists"""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value.lower()
    

class OTPVerificationSerializer(serializers.Serializer):
    """Serializer for OTP verification"""
    
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True, min_length=6, max_length=6)
    otp_type = serializers.ChoiceField(
        required=True,
        choices=['EMAIL_VERIFICATION', 'PASSWORD_RESET', 'LOGIN_OTP']
    )
    
    def validate_code(self, value):
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
    otp_type = serializers.ChoiceField(
        required=True,
        choices=['EMAIL_VERIFICATION', 'PASSWORD_RESET', 'LOGIN_OTP']
    )
    
    def validate_email(self, value):
        """Check if user exists"""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value.lower()
    
    
    