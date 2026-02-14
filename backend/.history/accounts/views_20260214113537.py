# accounts/views.py

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    RegistrationSerializer, 
    OTPVerificationSerializer,
    ResendOTPSerializer,
    LoginSerializer,
    UserSerializer,
    UserUpdateSerializer,
    CompleteUserProfileSerializer,
    PatientProfileSerializer,
    DoctorProfileSerializer,
    LabTechnicianProfileSerializer,
    AdminProfileSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer
)
from .services import verify_otp, generate_otp, send_otp_email
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration using CreateAPIView
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
            
            headers = self.get_success_headers(serializer.data)
            return Response(
                {
                    "message": "Registration successful. Please check your email for OTP verification.",
                    "user": {
                        "email": user.email,
                        "user_type": user.user_type
                    }
                },
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return Response(
                {"error": f"Registration failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VerifyOTPView(generics.GenericAPIView):
    """
    API endpoint for OTP verification using GenericAPIView
    """
    serializer_class = OTPVerificationSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
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
        
        logger.info(f"User verified email: {user.email}")
        
        return Response({
            "message": "Email verified successfully.",
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            "user": {
                "email": user.email,
                "user_type": user.user_type,
                "is_verified": user.is_verified
            }
        }, status=status.HTTP_200_OK)


class ResendOTPView(generics.GenericAPIView):
    """
    API endpoint for resending OTP using GenericAPIView
    """
    serializer_class = ResendOTPSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
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


class LoginView(generics.GenericAPIView):
    """
    API endpoint for user login with JWT tokens using GenericAPIView
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Update last login
        from django.utils import timezone
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        logger.info(f"User logged in: {user.email}")
        
        return Response({
            'message': 'Login successful',
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'user_type': user.user_type,
                'is_verified': user.is_verified
            }
        }, status=status.HTTP_200_OK)


class LogoutView(generics.GenericAPIView):
    """
    API endpoint for user logout (blacklist refresh token) using GenericAPIView
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            logger.info(f"User logged out: {request.user.email}")
            
            return Response(
                {'message': 'Logout successful'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )


class CurrentUserView(generics.RetrieveAPIView):
    """
    Get current authenticated user's complete profile using RetrieveAPIView
    """
    serializer_class = CompleteUserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UpdateUserView(generics.UpdateAPIView):
    """
    Update basic user information using UpdateAPIView
    """
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch', 'put']
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        logger.info(f"User updated profile: {request.user.email}")
        
        return Response({
            'message': 'Profile updated successfully',
            'user': UserSerializer(instance).data
        }, status=status.HTTP_200_OK)


class UpdateUserProfileView(generics.UpdateAPIView):
    """
    Update UserProfile (general profile information) using UpdateAPIView
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch', 'put']
    
    def get_object(self):
        user = self.request.user
        if not hasattr(user, 'profile'):
            from .models import UserProfile
            UserProfile.objects.create(user=user)
        return user.profile
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        logger.info(f"User updated general profile: {request.user.email}")
        
        return Response({
            'message': 'Profile updated successfully',
            'profile': serializer.data
        }, status=status.HTTP_200_OK)


class UpdatePatientProfileView(generics.UpdateAPIView):
    """
    Update Patient Profile using UpdateAPIView
    """
    serializer_class = PatientProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch', 'put']
    
    def get_object(self):
        user = self.request.user
        if user.user_type != 'patient':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only patients can update patient profile")
        
        if not hasattr(user, 'patient_profile'):
            from .models import PatientProfile
            PatientProfile.objects.create(user=user)
        
        return user.patient_profile
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        logger.info(f"Patient updated profile: {request.user.email}")
        
        return Response({
            'message': 'Patient profile updated successfully',
            'profile': serializer.data
        }, status=status.HTTP_200_OK)


class UpdateDoctorProfileView(generics.UpdateAPIView):
    """
    Update Doctor Profile using UpdateAPIView
    """
    serializer_class = DoctorProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch', 'put']
    
    def get_object(self):
        user = self.request.user
        if user.user_type != 'doctor':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only doctors can update doctor profile")
        
        if not hasattr(user, 'doctor_profile'):
            from .models import DoctorProfile
            DoctorProfile.objects.create(user=user)
        
        return user.doctor_profile
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        logger.info(f"Doctor updated profile: {request.user.email}")
        
        return Response({
            'message': 'Doctor profile updated successfully',
            'profile': serializer.data
        }, status=status.HTTP_200_OK)


class UpdateLabTechnicianProfileView(generics.UpdateAPIView):
    """
    Update Lab Technician Profile using UpdateAPIView
    """
    serializer_class = LabTechnicianProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch', 'put']
    
    def get_object(self):
        user = self.request.user
        if user.user_type != 'staff':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only lab technicians can update lab technician profile")
        
        if not hasattr(user, 'lab_technician_profile'):
            from .models import LabTechnicianProfile
            LabTechnicianProfile.objects.create(user=user)
        
        return user.lab_technician_profile
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        logger.info(f"Lab Technician updated profile: {request.user.email}")
        
        return Response({
            'message': 'Lab technician profile updated successfully',
            'profile': serializer.data
        }, status=status.HTTP_200_OK)


class UpdateAdminProfileView(generics.UpdateAPIView):
    """
    Update Admin Profile using UpdateAPIView
    """
    serializer_class = AdminProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch', 'put']
    
    def get_object(self):
        user = self.request.user
        if user.user_type != 'admin':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only admins can update admin profile")
        
        if not hasattr(user, 'admin_profile'):
            from .models import AdminProfile
            AdminProfile.objects.create(user=user)
        
        return user.admin_profile
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        logger.info(f"Admin updated profile: {request.user.email}")
        
        return Response({
            'message': 'Admin profile updated successfully',
            'profile': serializer.data
        }, status=status.HTTP_200_OK)


class ChangePasswordView(generics.GenericAPIView):
    """
    Change password for authenticated user using GenericAPIView
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        logger.info(f"User changed password: {request.user.email}")
        
        return Response({
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)