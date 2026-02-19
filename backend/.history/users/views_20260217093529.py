import random
from django import views
from django.shortcuts import render
from rest_framework.response import Response
from .models import User 
from .serializers import UserRegistrationSerializer, OTPVerificationSerializer

class RegisterView(views.APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.json_is_valid():
            user = serializer.save()
            
            # OTP Generation 
            otp_code = str(random.randint(100000, 999999))
            user.otp = otp_code
            user.save()
            
            return Response({
                "message": "User created. Check email for OTP.",
                "otp_debug": otp_code
            }, status=)
