from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.db import transaction
from .serializers import (
    RegistrationSerializer, 
    OTPVerificationSerializer,
    ResendOTPSerializer
)
from .services import verify_otp, generate_otp, send_otp_email
from rest_framework.generics import CreateAPIView
from rest_framework_simplejwt.tokens import RefreshToken

import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class RegisterView(CreateAPIView):
    """
    API endpoint for user registration.
    """
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            with transaction.atomic():
                # Create user
                user = serializer.save()
                
                # Generate OTP
                otp = generate_otp(user.email, purpose='registration')
                
                # Send OTP email
                email_sent = send_otp_email(user.email, otp.otp_code, purpose='registration')
                
                if not email_sent:
                    logger.warning(f"Failed to send OTP email to {user.email}")
                
                logger.info(f"New user registered: {user.email}")
            
            return Response(
                {
                    "message": "Registration successful. Please check your email for OTP verification.",
                    "user": {
                        "email": user.email,
                        "user_type": user.user_type
                    }
                },
                status=status.HTTP_201_CREATED
            )
        
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return Response(
                {"error": f"Registration failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VerifyOTPView(APIView):
    """
    API endpoint for OTP verification.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data["email"]
        otp_code = serializer.validated_data["otp_code"]
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verify OTP
        if not verify_otp(email, otp_code, purpose='registration'):
            return Response(
                {"error": "Invalid or expired OTP."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mark user as verified
        user.is_verified = True
        user.save(update_fields=['is_verified'])
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "message": "Email verified successfully.",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "email": user.email,
                "user_type": user.user_type,
                "is_verified": user.is_verified
            }
        }, status=status.HTTP_200_OK)


class ResendOTPView(APIView):
    """
    API endpoint for resending OTP.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data["email"]
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user is already verified
        if user.is_verified:
            return Response(
                {"message": "User is already verified."},
                status=status.HTTP_200_OK
            )
        
        try:
            # Generate new OTP
            otp = generate_otp(email, purpose='registration')
            
            # Send OTP email
            email_sent = send_otp_email(email, otp.otp_code, purpose='registration')
            
            if not email_sent:
                return Response(
                    {"error": "Failed to send OTP email. Please try again."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            logger.info(f"OTP resent to {email}")
            
            return Response(
                {"message": "OTP sent successfully. Please check your email."},
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            logger.error(f"Error resending OTP: {str(e)}")
            return Response(
                {"error": "Failed to resend OTP. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )