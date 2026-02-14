# accounts/urls.py

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    VerifyOTPView,
    ResendOTPView,
    LoginView,
    LogoutView,
    CurrentUserView,
    UpdateUserView,
    UpdateUserProfileView,
    UpdatePatientProfileView,
    UpdateDoctorProfileView,
    UpdateLabTechnicianProfileView,
    UpdateAdminProfileView,
    ChangePasswordView,
)

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # User Profile - Basic
    path('me/', CurrentUserView.as_view(), name='current-user'),
    path('update/', UpdateUserView.as_view(), name='update-user'),
    path('profile/update/', UpdateUserProfileView.as_view(), name='update-general-profile'),
    
    # User Profile - Role-specific
    path('profile/patient/update/', UpdatePatientProfileView.as_view(), name='update-patient-profile'),
    path('profile/doctor/update/', UpdateDoctorProfileView.as_view(), name='update-doctor-profile'),
    path('profile/lab-technician/update/', UpdateLabTechnicianProfileView.as_view(), name='update-lab-tech-profile'),
    path('profile/admin/update/', UpdateAdminProfileView.as_view(), name='update-admin-profile'),
    
    # Password Management
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    
     #  tokens 
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]