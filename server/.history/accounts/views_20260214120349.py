# accounts/views.py

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
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
    ChangePasswordSerializer,
    LogoutSerializer
)
from .services import verify_otp, generate_otp, send_otp_email
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class RegisterView(generics.CreateAPIView):
    """
    Register a new user account.
    
    Creates a new user and sends an OTP verification code to their email.
    The user must verify their email before they can log in.
    """
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Register new user",
        description="Create a new user account and send OTP verification email. "
                    "Supports multiple user types: patient, doctor, nurse, admin, staff.",
        request=RegistrationSerializer,
        responses={
            201: OpenApiResponse(
                description="User created successfully",
                response={
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "example": "Registration successful. Please check your email for OTP verification."},
                        "user": {
                            "type": "object",
                            "properties": {
                                "email": {"type": "string", "example": "john.doe@example.com"},
                                "user_type": {"type": "string", "example": "patient"}
                            }
                        }
                    }
                }
            ),
            400: OpenApiResponse(description="Validation error - invalid input data"),
            500: OpenApiResponse(description="Server error - registration failed")
        },
        tags=['Authentication'],
        examples=[
            OpenApiExample(
                'Patient Registration',
                value={
                    "email": "patient@example.com",
                    "password": "SecurePass123!",
                    "password_confirm": "SecurePass123!",
                    "first_name": "John",
                    "last_name": "Doe",
                    "phone_number": "+1234567890",
                    "user_type": "patient",
                    "date_of_birth": "1990-05-15",
                    "address": "123 Main Street, City, State"
                },
                request_only=True,
            ),
            OpenApiExample(
                'Doctor Registration',
                value={
                    "email": "doctor@example.com",
                    "password": "SecurePass123!",
                    "password_confirm": "SecurePass123!",
                    "first_name": "Jane",
                    "last_name": "Smith",
                    "user_type": "doctor"
                },
                request_only=True,
            ),
        ]
    )
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
    Verify email address using OTP code.
    
    After successful verification, returns JWT tokens for authentication.
    """
    serializer_class = OTPVerificationSerializer
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Verify OTP code",
        description="Verify email address using the 6-digit OTP code sent during registration. "
                    "Returns JWT access and refresh tokens upon successful verification.",
        request=OTPVerificationSerializer,
        responses={
            200: OpenApiResponse(
                description="Email verified successfully",
                response={
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "example": "Email verified successfully."},
                        "tokens": {
                            "type": "object",
                            "properties": {
                                "refresh": {"type": "string", "example": "eyJ0eXAiOiJKV1QiLCJhbGc..."},
                                "access": {"type": "string", "example": "eyJ0eXAiOiJKV1QiLCJhbGc..."}
                            }
                        },
                        "user": {
                            "type": "object",
                            "properties": {
                                "email": {"type": "string"},
                                "user_type": {"type": "string"},
                                "is_verified": {"type": "boolean"}
                            }
                        }
                    }
                }
            ),
            400: OpenApiResponse(description="Invalid or expired OTP"),
            404: OpenApiResponse(description="User not found")
        },
        tags=['Authentication'],
        examples=[
            OpenApiExample(
                'Verify OTP',
                value={
                    "email": "john.doe@example.com",
                    "otp_code": "123456"
                },
                request_only=True,
            ),
        ]
    )
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
    Resend OTP verification code.
    """
    serializer_class = ResendOTPSerializer
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Resend OTP code",
        description="Request a new OTP verification code if the previous one expired or was not received.",
        request=ResendOTPSerializer,
        responses={
            200: OpenApiResponse(description="OTP sent successfully"),
            404: OpenApiResponse(description="User not found"),
            500: OpenApiResponse(description="Failed to send OTP email")
        },
        tags=['Authentication']
    )
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
    Authenticate user and receive JWT tokens.
    
    Requires verified email address.
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="User login",
        description="Authenticate with email and password to receive JWT access and refresh tokens. "
                    "Email must be verified before login is allowed.",
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                description="Login successful",
                response={
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "example": "Login successful"},
                        "tokens": {
                            "type": "object",
                            "properties": {
                                "refresh": {"type": "string"},
                                "access": {"type": "string"}
                            }
                        },
                        "user": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "email": {"type": "string"},
                                "first_name": {"type": "string"},
                                "last_name": {"type": "string"},
                                "user_type": {"type": "string"},
                                "is_verified": {"type": "boolean"}
                            }
                        }
                    }
                }
            ),
            400: OpenApiResponse(description="Invalid credentials or email not verified")
        },
        tags=['Authentication'],
        examples=[
            OpenApiExample(
                'Login',
                value={
                    "email": "john.doe@example.com",
                    "password": "SecurePass123!"
                },
                request_only=True,
            ),
        ]
    )
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
    Logout user by blacklisting refresh token.
    """
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="User logout",
        description="Logout by blacklisting the refresh token. The access token will remain valid until it expires.",
        request=LogoutSerializer,
        responses={
            200: OpenApiResponse(description="Logout successful"),
            400: OpenApiResponse(description="Invalid or missing refresh token")
        },
        tags=['Authentication']
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            refresh_token = serializer.validated_data['refresh']
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
                {'error': 'Invalid token or token already blacklisted'},
                status=status.HTTP_400_BAD_REQUEST
            )


class CurrentUserView(generics.RetrieveAPIView):
    """
    Get complete profile for authenticated user.
    
    Includes all profile data and role-specific information.
    """
    serializer_class = CompleteUserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get current user profile",
        description="Retrieve complete profile information for the authenticated user, "
                    "including basic info, general profile, and role-specific profile data.",
        responses={
            200: CompleteUserProfileSerializer,
            401: OpenApiResponse(description="Authentication required")
        },
        tags=['User Profile']
    )
    def get_object(self):
        return self.request.user


class UpdateUserView(generics.UpdateAPIView):
    """
    Update basic user information.
    """
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch', 'put']
    
    @extend_schema(
        summary="Update basic user information",
        description="Update name, phone number, address, date of birth, and profile picture.",
        request=UserUpdateSerializer,
        responses={
            200: OpenApiResponse(
                description="Profile updated successfully",
                response={
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "example": "Profile updated successfully"},
                        "user": {"$ref": "#/components/schemas/User"}
                    }
                }
            ),
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Authentication required")
        },
        tags=['User Profile']
    )
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
    Update general user profile settings.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch', 'put']
    
    @extend_schema(
        summary="Update general profile settings",
        description="Update bio, notification preferences, and other general profile settings.",
        request=UserProfileSerializer,
        responses={
            200: OpenApiResponse(description="Profile updated successfully"),
            401: OpenApiResponse(description="Authentication required")
        },
        tags=['User Profile']
    )
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
    Update patient-specific profile information.
    
    Only accessible to users with user_type='patient'.
    """
    serializer_class = PatientProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch', 'put']
    
    @extend_schema(
        summary="Update patient profile",
        description="Update medical history, allergies, chronic conditions, medications, "
                    "emergency contacts, and insurance information. Only accessible to patients.",
        request=PatientProfileSerializer,
        responses={
            200: OpenApiResponse(description="Patient profile updated successfully"),
            403: OpenApiResponse(description="Only patients can update patient profile"),
            401: OpenApiResponse(description="Authentication required")
        },
        tags=['Patient Profile']
    )
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
    Update doctor-specific profile information.
    
    Only accessible to users with user_type='doctor'.
    """
    serializer_class = DoctorProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch', 'put']
    
    @extend_schema(
        summary="Update doctor profile",
        description="Update medical license, specialization, education, certifications, "
                    "consultation fees, and availability. Only accessible to doctors.",
        request=DoctorProfileSerializer,
        responses={
            200: OpenApiResponse(description="Doctor profile updated successfully"),
            403: OpenApiResponse(description="Only doctors can update doctor profile"),
            401: OpenApiResponse(description="Authentication required")
        },
        tags=['Doctor Profile']
    )
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
    Update lab technician profile information.
    
    Only accessible to users with user_type='staff'.
    """
    serializer_class = LabTechnicianProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch', 'put']
    
    @extend_schema(
        summary="Update lab technician profile",
        description="Update certifications, specialization, department, and shift information. "
                    "Only accessible to lab technicians.",
        request=LabTechnicianProfileSerializer,
        responses={
            200: OpenApiResponse(description="Lab technician profile updated successfully"),
            403: OpenApiResponse(description="Only lab technicians can update this profile"),
            401: OpenApiResponse(description="Authentication required")
        },
        tags=['Lab Technician Profile']
    )
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
    Update admin profile information.
    
    Only accessible to users with user_type='admin'.
    """
    serializer_class = AdminProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch', 'put']
    
    @extend_schema(
        summary="Update admin profile",
        description="Update employee ID, department, designation, and administrative permissions. "
                    "Only accessible to administrators.",
        request=AdminProfileSerializer,
        responses={
            200: OpenApiResponse(description="Admin profile updated successfully"),
            403: OpenApiResponse(description="Only admins can update admin profile"),
            401: OpenApiResponse(description="Authentication required")
        },
        tags=['Admin Profile']
    )
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
    Change password for authenticated user.
    
    Requires current password for verification.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Change password",
        description="Change user password. Requires the current password for security verification.",
        request=ChangePasswordSerializer,
        responses={
            200: OpenApiResponse(description="Password changed successfully"),
            400: OpenApiResponse(description="Validation error - old password incorrect or new passwords don't match"),
            401: OpenApiResponse(description="Authentication required")
        },
        tags=['Password Management'],
        examples=[
            OpenApiExample(
                'Change Password',
                value={
                    "old_password": "OldSecurePass123!",
                    "new_password": "NewSecurePass456!",
                    "new_password_confirm": "NewSecurePass456!"
                },
                request_only=True,
            ),
        ]
    )
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        logger.info(f"User changed password: {request.user.email}")
        
        return Response({
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)