import random
from rest_framework.views import APIView
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status, generics, permissions, filters as drf_filters, viewsets
from django.db.models import Avg
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User, Profile, DoctorProfile
from .filters import DoctorFilter
from .notifications import AuthNotifications
from .serializers import UserRegistrationSerializer, OTPVerificationSerializer, CustomTokenObtainPairSerializer, ProfileSerializer, DoctorProfileSerializer, AdminUserManagementSerializer


"""
this section covers the user authentification section
this takes user registration, login, otp verification
more over we use jwt authentification
"""
class RegisterView(APIView):
    @extend_schema(
        request=UserRegistrationSerializer,
        responses={
            201: OpenApiResponse(description="User created successfully. OTP sent to email."),
            400: OpenApiResponse(description="Validation error — invalid or missing fields."),
        },
        description="Register a new user account. On success, a 6-digit OTP is generated and sent to the provided email address for account activation.",
        summary="Register a new user",
        tags=["Authentication"],
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # OTP Generation 
            otp_code = user.generate_otp()
            success = AuthNotifications.send_otp_email(user, otp_code)
            
            
            
            if success:
                    return Response({
                        "message": "Registration successful. Check your email for the OTP."
                    }, status=status.HTTP_201_CREATED)
            else:
                    return Response({
                        "message": "User created but failed to send email. Please try resending OTP."
                    }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    @extend_schema(
        request=OTPVerificationSerializer,
        responses={
            200: OpenApiResponse(description="Account activated successfully."),
            400: OpenApiResponse(description="Invalid OTP or email, or validation error."),
        },
        description="Verify the OTP sent to the user's email after registration. On success, the account is activated and marked as verified.",
        summary="Verify OTP and activate account",
        tags=["Authentication"],
    )
    def post(self, request):  # sourcery skip: extract-method
        serializer = OTPVerificationSerializer(data=request.data)
        
        if serializer.is_valid():
             email = serializer.validated_data['email']
             otp_received = serializer.validated_data['otp']
            
             try:
                user = User.objects.get(email=email)
                if user.verify_otp(otp_received): # Your logic to check if OTP matches and isn't expired
                    user.is_active = True
                    user.save()
                    return Response({"message": "Account activated successfully!"}, status=200)
                else:
                    return Response({"error": "Invalid or expired OTP."}, status=400)
             except User.DoesNotExist:
                return Response({"error": "User not found."}, status=404)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

class ResendOTPView(APIView):
    """
    Allows users to request a new OTP if the previous one expired 
    or was lost in the spam folder.
    """
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            
            if user.is_active:
                return Response({"message": "This account is already active."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Generate a fresh code and update the timestamp
            otp_code = user.generate_otp()
            
            # Send the email again
            success = AuthNotifications.send_otp_email(user, otp_code)
            
            if success:
                return Response({"message": "A new OTP has been sent to your email."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Failed to send email. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except User.DoesNotExist:
            return Response({"message": "If this email is registered, a new OTP has been sent."}, status=status.HTTP_200_OK)

@extend_schema(
    request=CustomTokenObtainPairSerializer,
    responses={
        200: OpenApiResponse(description="Login successful. Returns access and refresh JWT tokens."),
        401: OpenApiResponse(description="Invalid credentials or unverified/inactive account."),
    },
    description="Authenticate with email and password. Returns a JWT access token and refresh token on success. The account must be verified and active before login is permitted.",
    summary="Login and obtain JWT tokens",
    tags=["Authentication"],
)
class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    
"""
this section of the application now will cover the user profiles with crude operations
"""

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        responses={200: ProfileSerializer},
        description="Retrieve the profile of the currently authenticated user. A profile is created automatically if one does not already exist.",
        summary="Get current user profile",
        tags=["Profile"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        request=ProfileSerializer,
        responses={
            200: ProfileSerializer,
            400: OpenApiResponse(description="Validation error."),
        },
        description="Fully update the profile of the currently authenticated user.",
        summary="Update current user profile",
        tags=["Profile"],
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        request=ProfileSerializer,
        responses={
            200: ProfileSerializer,
            400: OpenApiResponse(description="Validation error."),
        },
        description="Partially update the profile of the currently authenticated user.",
        summary="Partially update current user profile",
        tags=["Profile"],
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile


@extend_schema(
    responses={200: DoctorProfileSerializer(many=True)},
    parameters=[
        OpenApiParameter(
            name="specialization",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter doctors by their medical specialization (e.g. 'Cardiology', 'Dermatology').",
            required=False,
        ),
    ],
    description="Returns a list of all verified doctor profiles. Requires authentication. Results can be filtered by specialization.",
    summary="List verified doctors",
    tags=["Doctors"],
)

class DoctorListView(generics.ListAPIView):
    queryset = DoctorProfile.objects.filter(is_verified=True)
    serializer_class = DoctorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['specialization']


class DoctorProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Publicly accessible list of doctors for patients to search.
    """
    queryset = DoctorProfile.objects.filter(is_verified=True).annotate(
        avg_rating=Avg('reviews__rating')
    ).order_by('-avg_rating', 'specialization')

    serializer_class = DoctorProfileSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter]
    filterset_class = DoctorFilter
    search_fields = ['profile__first_name', 'profile__last_name', 'specialization']


@extend_schema(
    responses={200: AdminUserManagementSerializer(many=True)},
    parameters=[
        OpenApiParameter(
            name="role",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter users by their assigned role.",
            required=False,
        ),
        OpenApiParameter(
            name="is_active",
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description="Filter users by their active status.",
            required=False,
        ),
        OpenApiParameter(
            name="is_verified",
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description="Filter users by their email verification status.",
            required=False,
        ),
        OpenApiParameter(
            name="search",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Search users by email, first name, or last name.",
            required=False,
        ),
    ],
    description="Admin-only endpoint. Returns a paginated list of all users with filtering by role, active status, and verification status, as well as search by email or name.",
    summary="Admin — list and search all users",
    tags=["Admin"],
)
class UserManagementListView(generics.ListAPIView):
    # Only staff/admins should ever see this
    permission_classes = [permissions.IsAdminUser] 
    serializer_class = AdminUserManagementSerializer
    queryset = User.objects.all().order_by('-id')
    
    # Adding Search and Filter capabilities
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter]
    filterset_fields = ['role', 'is_active', 'is_verified']
    search_fields = ['email', 'profile__first_name', 'profile__last_name']
