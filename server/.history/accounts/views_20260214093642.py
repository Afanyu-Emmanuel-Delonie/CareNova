from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.db import transaction
from .serializers import RegistrationSerializer, OTPVerificationSerializer
from .services import verify_otp, generate_otp, send_otp_email
from rest_framework.generics import CreateAPIView
from rest_framework_simplejwt.tokens import RefreshToken

import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]
      
class RegisterView(CreateAPIView):
    """
    Alternative implementation using DRF's generic views.
    This is more concise and follows DRF conventions.
    """
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            with transaction.atomic():
                user = serializer.save()
                otp = generate_otp(user, "EMAIL_VERIFICATION")
                send_otp_email(user, otp)
                
                logger.info(f"New user registered: {user.email}")
            
            return Response(
                {
                    "message": "Registration successful. Please check your email for OTP verification.",
                    "user": {
                        "email": user.email,
                        "role": user.role
                    }
                },
                status=status.HTTP_201_CREATED
            )
        
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return Response(
                {"error": "Registration failed. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

          
            