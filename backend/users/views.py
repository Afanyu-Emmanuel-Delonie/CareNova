import random
from rest_framework.views import APIView
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status, generics, permissions, filters as drf_filters, viewsets
from django.db.models import Avg
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import User, Profile, DoctorProfile, Category
from .filters import DoctorFilter
from .notifications import AuthNotifications
from .serializers import UserRegistrationSerializer, OTPVerificationSerializer, CustomTokenObtainPairSerializer, ProfileSerializer, DoctorProfileSerializer, AdminUserManagementSerializer, CategorySerializer


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
            404: OpenApiResponse(description="User not found."),
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
                if user.verify_otp(otp_received):
                    user.is_verified = True
                    user.is_active = True
                    user.save(update_fields=["is_verified", "is_active"])
                    return Response({"message": "Account activated successfully!"}, status=200)
                else:
                    return Response({"error": "Invalid or expired OTP."}, status=400)
            except User.DoesNotExist:
                return Response({"error": "User not found."}, status=404)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendOTPView(APIView):
    @extend_schema(
        request=None,
        parameters=[
            OpenApiParameter(
                name="email",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Email address of the unverified account to resend the OTP to.",
                required=True,
            ),
        ],
        responses={
            200: OpenApiResponse(description="A new OTP has been sent, or the email is not registered (same response for security)."),
            400: OpenApiResponse(description="Email is required, or the account is already active."),
            429: OpenApiResponse(description="Rate limited — please wait 60 seconds before requesting a new code."),
            500: OpenApiResponse(description="Email delivery failed."),
        },
        description=(
            "Allows users to request a new OTP if the previous one expired or was lost. "
            "Requests are rate-limited to one per 60 seconds per account. "
            "If the email is not registered, a generic success response is returned to prevent user enumeration."
        ),
        summary="Resend OTP",
        tags=["Authentication"],
    )
    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)

            if user.is_active:
                return Response({"message": "This account is already active."}, status=status.HTTP_400_BAD_REQUEST)

            # Rate limit: enforce 60-second cooldown between OTP requests
            if user.otp_created_at and timezone.now() < user.otp_created_at + timedelta(seconds=60):
                return Response(
                    {"error": "Please wait 60 seconds before requesting a new code."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )

            otp_code = user.generate_otp()
            success = AuthNotifications.send_otp_email(user, otp_code)

            if success:
                return Response({"message": "A new OTP has been sent to your email."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Failed to send email. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except User.DoesNotExist:
            # Generic response to prevent revealing whether an email is registered
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


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=None,
        parameters=[
            OpenApiParameter(
                name="refresh",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="The refresh token to blacklist.",
                required=True,
            ),
        ],
        responses={
            205: OpenApiResponse(description="Logged out successfully. Refresh token blacklisted."),
            400: OpenApiResponse(description="refresh token is required, or the token is invalid/already blacklisted."),
        },
        description=(
            "Logs the user out by blacklisting their refresh token, making it unusable for future access token generation. "
            "The client is responsible for discarding the access token locally. "
            "Requires the refresh token in the request body."
        ),
        summary="Logout and blacklist refresh token",
        tags=["Authentication"],
    )
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully."}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DeactivateAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(description="Account deactivated. The user will no longer be able to log in."),
            400: OpenApiResponse(description="refresh token is required."),
        },
        description=(
            "Deactivates the authenticated user's account by setting is_active=False and blacklisting their refresh token. "
            "The account remains in the database and can be reactivated by an admin. "
            "The user will be unable to log in until reactivated."
        ),
        summary="Deactivate own account",
        tags=["Account Management"],
    )
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Blacklist the token before deactivating so the session ends immediately
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            pass  # Proceed with deactivation even if the token is already invalid

        user = request.user
        user.is_active = False
        user.save(update_fields=['is_active'])
        return Response({"message": "Your account has been deactivated."}, status=status.HTTP_200_OK)


class DeleteAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=None,
        parameters=[
            OpenApiParameter(
                name="refresh",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="The refresh token to blacklist before deletion.",
                required=True,
            ),
        ],
        responses={
            204: OpenApiResponse(description="Account permanently deleted."),
            400: OpenApiResponse(description="refresh token is required."),
        },
        description=(
            "Permanently and irreversibly deletes the authenticated user's account and all associated data. "
            "The refresh token is blacklisted first to terminate the session immediately. "
            "This action cannot be undone."
        ),
        summary="Permanently delete own account",
        tags=["Account Management"],
    )
    def delete(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            pass  # Proceed with deletion even if the token is already invalid

        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


"""
this section of the application now will cover the user profiles with crud operations
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
        OpenApiParameter(
            name="category",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter doctors by category name (e.g. 'Cardiology').",
            required=False,
        ),
        OpenApiParameter(
            name="min_rating",
            type=OpenApiTypes.NUMBER,
            location=OpenApiParameter.QUERY,
            description="Filter doctors with average rating greater than or equal to this value.",
            required=False,
        ),
    ],
    description="Returns a list of all verified doctor profiles. Requires authentication. Results can be filtered by specialization, category, and minimum rating.",
    summary="List verified doctors",
    tags=["Doctors"],
)
class DoctorListView(generics.ListAPIView):
    queryset = DoctorProfile.objects.filter(is_verified=True)
    serializer_class = DoctorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = DoctorFilter


@extend_schema(
    responses={200: CategorySerializer(many=True)},
    description="Public endpoint returning all available doctor categories for dropdown/filter use in clients.",
    summary="List doctor categories",
    tags=["Categories"],
)
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


@extend_schema_view(
    list=extend_schema(
        summary="List all verified doctors (public)",
        description=(
            "Publicly accessible endpoint. Returns a list of all verified doctor profiles, "
            "ordered by average rating (descending) then specialization. Supports full-text search "
            "by name or specialization, and advanced filtering via DoctorFilter."
        ),
        responses={200: DoctorProfileSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Search doctors by first name, last name, or specialization.",
                required=False,
            ),
            OpenApiParameter(
                name="specialization",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter doctors by specialization (applied via DoctorFilter).",
                required=False,
            ),
            OpenApiParameter(
                name="category",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter doctors by category name (applied via DoctorFilter).",
                required=False,
            ),
            OpenApiParameter(
                name="min_rating",
                type=OpenApiTypes.NUMBER,
                location=OpenApiParameter.QUERY,
                description="Return doctors with average rating >= this value (applied via DoctorFilter).",
                required=False,
            ),
        ],
        tags=["Doctors"],
    ),
    retrieve=extend_schema(
        summary="Retrieve a single doctor profile (public)",
        description=(
            "Publicly accessible endpoint. Returns the full profile of a single verified doctor "
            "by their ID, including their computed average rating from patient reviews."
        ),
        responses={
            200: DoctorProfileSerializer,
            404: OpenApiResponse(description="Doctor profile not found."),
        },
        tags=["Doctors"],
    ),
)
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
    permission_classes = [permissions.IsAdminUser]
    serializer_class = AdminUserManagementSerializer
    queryset = User.objects.all().order_by('-id')

    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter]
    filterset_fields = ['role', 'is_active', 'is_verified']
    search_fields = ['email', 'profile__first_name', 'profile__last_name']
    
    
