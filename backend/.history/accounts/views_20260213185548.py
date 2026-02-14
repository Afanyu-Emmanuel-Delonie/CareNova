from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .serializers import RegistrationSerializer
from .services import verify_otp, generate_otp, send_otp_email

User = get_user_model()


class VerifyOTPView(APIView):

    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")
        otp_type = request.data.get("otp_type")

        if not email or not code or not otp_type:
            return Response(
                {"error": "Email, code, and otp_type are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        is_valid = verify_otp(user, otp_type, code)

        if not is_valid:
            return Response(
                {"error": "Invalid or expired OTP."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Example: activate account
        if otp_type == "EMAIL_VERIFICATION":
            user.is_verified = True
            user.save()

        return Response(
            {"message": "OTP verified successfully."},
            status=status.HTTP_200_OK
        )


class RegisterView(APIView):
    
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # generate OTP 
            otp = generate_otp(user, "EMAIL_VERIFICATION")
            
            # send the otp 
            send_otp_email(user, otp)
            
            return Response(
                {
                    "message": "User registered successfully. Check your email for OTP.",
                    "name": user.use
                    "email": user.email,
                },
                status=status.HTTP_201_CREATED
            )
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        # Return helpful error message for GET requests
        return Response(
            {
                "error": "GET method not allowed. Please use POST to register.",
                "required_fields": ["email", "password", "role"]
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )