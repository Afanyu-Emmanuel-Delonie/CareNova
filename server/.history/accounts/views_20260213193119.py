from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.db import transaction
from .serializers import RegistrationSerializer, OTPVerificationSerializer
from .services import verify_otp, generate_otp, send_otp_email
from rest_framework.generics import CreateAPIView

import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class VerifyOTPView(APIView):
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Use a serializer for validation instead of manual checks
        serializer = OTPVerificationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        otp_type = serializer.validated_data['otp_type']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            logger.warning(f"OTP verification attempted for non-existent user: {email}")
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        is_valid = verify_otp(user, otp_type, code)
        
        if not is_valid:
            logger.warning(f"Invalid OTP attempt for user: {email}")
            return Response(
                {"error": "Invalid or expired OTP."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update user based on OTP type
        if otp_type == "EMAIL_VERIFICATION":
            user.is_verified = True
            user.save(update_fields=['is_verified'])
            logger.info(f"User verified successfully: {email}")
        
        return Response(
            {
                "message": "OTP verified successfully.",
                "user": {
                    "email": user.email,
                    "is_verified": user.is_verified
                }
            },
            status=status.HTTP_200_OK
        )
        
class RegisterView(CreateAPIView):
    """
    Alternative implementation using DRF's generic views.
    This is more concise and follows DRF conventions.
    """
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            with transaction.atomic():
                user = serializer.save()
                otp = generate_otp(user, "EMAIL_VERIFICATION")
                send_otp_email(user, otp)
                
                logger.info(f"New user registered: {user.email}")
            
            return Response(
                {
                    "message": "Registration successful. Please check your email for OTP verification.",
                    "user": {
                        "email": user.email,
                        "role": user.role
                    }
                },
                status=status.HTTP_201_CREATED
            )
        
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return Response(
                {"error": "Registration failed. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RequestAccountDeletionView(APIView):
    """
    Step 1: Request account deletion - sends confirmation email/OTP
    
    POST /api/auth/request-delete-account/
    Headers: Authorization: Bearer <token>
    Body: {
        "password": "user_password"  # Verify it's really them
    }
    """
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer]
    
    def post(self, request):
        user = request.user
        serializer = PasswordVerificationSerializer(
            data=request.data,
            context={'user': user}
        )
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate OTP for account deletion confirmation
        from .services import generate_otp, send_otp_email
        otp = generate_otp(user, "ACCOUNT_DELETION")
        send_otp_email(user, otp)
        
        logger.warning(f"Account deletion requested for: {user.email}")
        
        return Response(
            {
                "message": "Account deletion requested. Please check your email for confirmation code.",
                "email": user.email
            },
            status=status.HTTP_200_OK
        )


class ConfirmAccountDeletionView(APIView):
    """
    Step 2: Confirm account deletion with OTP
    
    DELETE /api/auth/delete-account/
    Headers: Authorization: Bearer <token>
    Body: {
        "code": "123456",
        "password": "user_password"
    }
    """
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer]
    
    def delete(self, request):
        user = request.user
        serializer = AccountDeletionSerializer(
            data=request.data,
            context={'user': user}
        )
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # Store user email before deletion for logging
                user_email = user.email
                user_id = user.id
                
                # Delete the user (this will cascade to related profiles)
                user.delete()
                
                logger.critical(f"Account deleted: {user_email} (ID: {user_id})")
                
                # Send final confirmation email
                send_account_deletion_email(user_email)
            
            return Response(
                {
                    "message": "Your account has been permanently deleted.",
                },
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            logger.error(f"Account deletion failed for {user.email}: {str(e)}")
            return Response(
                {"error": "Account deletion failed. Please try again or contact support."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DeactivateAccountView(APIView):
    """
    Alternative: Deactivate account instead of deleting (soft delete)
    
    POST /api/auth/deactivate-account/
    Headers: Authorization: Bearer <token>
    Body: {
        "password": "user_password"
    }
    """
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer]
    
    def post(self, request):
        user = request.user
        serializer = PasswordVerificationSerializer(
            data=request.data,
            context={'user': user}
        )
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Deactivate instead of delete
        user.is_active = False
        user.save(update_fields=['is_active'])
        
        logger.warning(f"Account deactivated: {user.email}")
        
        return Response(
            {
                "message": "Your account has been deactivated. Contact support to reactivate.",
            },
            status=status.HTTP_200_OK
        )


class ReactivateAccountView(APIView):
    """
    Reactivate a deactivated account
    
    POST /api/auth/reactivate-account/
    Body: {
        "email": "user@example.com",
        "code": "123456"  # OTP sent to email
    }
    """
    permission_classes = []  # No auth needed (account is deactivated)
    renderer_classes = [JSONRenderer]
    
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        
        if not email or not code:
            return Response(
                {"error": "Email and code are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email, is_active=False)
        except User.DoesNotExist:
            return Response(
                {"error": "Account not found or already active."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verify OTP
        from .services import verify_otp
        is_valid = verify_otp(user, "ACCOUNT_REACTIVATION", code)
        
        if not is_valid:
            return Response(
                {"error": "Invalid or expired code."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.is_active = True
        user.save(update_fields=['is_active'])
        
        logger.info(f"Account reactivated: {user.email}")
        
        return Response(
            {
                "message": "Your account has been reactivated. You can now log in.",
            },
            status=status.HTTP_200_OK
        )


# ============================================================
# ADMIN VIEWS - For admins to manage user accounts
# ============================================================

class AdminDeleteUserView(APIView):
    """
    Admin endpoint to delete any user account
    
    DELETE /api/admin/users/<user_id>/
    Headers: Authorization: Bearer <admin_token>
    """
    permission_classes = [IsAuthenticated]  # Add IsAdminUser permission
    renderer_classes = [JSONRenderer]
    
    def delete(self, request, user_id):
        # Check if requester is admin
        if request.user.role != 'ADMIN':
            return Response(
                {"error": "Admin access required."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            user_to_delete = User.objects.get(id=user_id)
            
            # Prevent deleting other admins
            if user_to_delete.role == 'ADMIN':
                return Response(
                    {"error": "Cannot delete admin accounts."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            user_email = user_to_delete.email
            user_to_delete.delete()
            
            logger.critical(
                f"Admin {request.user.email} deleted user account: {user_email}"
            )
            
            return Response(
                {"message": f"User {user_email} has been deleted."},
                status=status.HTTP_200_OK
            )
        
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )          
            