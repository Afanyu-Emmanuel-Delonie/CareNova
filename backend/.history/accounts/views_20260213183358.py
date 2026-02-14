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
        if otp_type == "email_verification":
            user.is_active = True
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
            otp = generate_otp(user, "email")

