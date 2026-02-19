from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, VerifyOTPView, LoginView, UserProfileView, DoctorListView, UserManagementListView, DoctorProfileViewSet

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', UserProfileView.as_view(), name='user-profile'),
    path('doctors/', DoctorProfileViewSet.as_view({'get': 'list'}), name='doctor-list'),
    path('doctors/<int:pk>/', DoctorProfileViewSet.as_view({'get': 'retrieve'}), name='doctor-detail'),
    path('members/', UserManagementListView.as_view(), name='users-list' ),
    
    
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
