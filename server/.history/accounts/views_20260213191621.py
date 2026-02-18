from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.db import transaction
from .serializers import RegistrationSerializer, OTPVerificationSerializer
from .services import verify_otp, generate_otp, send_otp_email
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class VerifyOTPView(APIView):
    
    permission_classes = [AllowAny]