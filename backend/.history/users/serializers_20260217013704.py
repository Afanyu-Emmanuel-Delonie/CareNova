from rest_framework import serializers
from .models import User, Profile

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'role']
    
    def create(self, validate_data):
        user = User.objects.create_user
