from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class RegistrationSerializer(serializers.ModelSerializer):
    """ Serializers for user registration"""
    
    password = serializers.CharField(
        write_only=True,
        required
    )