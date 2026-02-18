from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, VerifyOTPView, LoginView, UserProfileView, DoctorListView, UserManagementListView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', UserProfileView.as_view(), name='user-profile'),
    path('doctors/', DoctorListView.as_view(), name='doctor-list'),
    path('members/', UserManagement )
    
    
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
