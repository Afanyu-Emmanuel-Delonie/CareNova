from django import views
from django.shortcuts import render
from rest_framework.response import Response
from .models import User 
from .serializers import UserRegistrationSerializer, OTPVerificationSerializer

class RegisterView(views.APIView):
    def post(self, request)
