import random
from rest_framework.views import APIView
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User, Profile
from .serializers import UserRegistrationSerializer, OTPVerificationSerializer, CustomTokenObtainPairSerializer, ProfileSerializer

"""
this section covers the user authentification section
this takes user registration, login, otp verification
more over we use jwt authentification
"""
class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # OTP Generation 
            otp_code = str(random.randint(100000, 999999))
            user.otp = otp_code
            user.save()
            
            return Response({
                "message": "User created. Check email for OTP.",
                "otp_debug": otp_code
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.error, status=status.HTTP_BAD_REQUEST)

class VerifyOTPView(APIView):
    @extend_schema(
        request=UserRegistrationSerializer,
        responses={201: UserRegistrationSerializer},
        description="Register a new user and generate an OTP for activation"
    )
    
    def post(self, request):  # sourcery skip: extract-method
        serializer = OTPVerificationSerializer(data=request.data)
        
        if serializer.is_valid():
             email = serializer.validated_data['email']
             otp = serializer.validated_data['otp']
            
             try:
                user = User.objects.get(email=email, otp=otp)
                user.is_active = True 
                user.is_verified = True
                user.otp = None
                user.save()
                return Response({"message": "Account activated successfully!"}, status=status.HTTP_200_OK)
             except User.DoesNotExist:
                return Response({"error": "Invalid OTP or email"}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
"""
this section of the application now will cover the user profiles with crude operations
"""

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
   def get_object(self):
        # This will either get the profile or create one on the fly 
        # if the signal failed or the user is old.
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

