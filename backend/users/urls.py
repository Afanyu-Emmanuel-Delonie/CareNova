from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, VerifyOTPView, ResendOTPView, LoginView,
    LogoutView, DeactivateAccountView, DeleteAccountView,
    UserProfileView, DoctorListView, DoctorProfileViewSet, CategoryListView,
    UserManagementListView,
)

urlpatterns = [

    # ── Authentication ───────────────────────────────────────────────────────
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # ── Account Management ───────────────────────────────────────────────────
    path('me/', UserProfileView.as_view(), name='user-profile'),
    path('me/deactivate/', DeactivateAccountView.as_view(), name='account-deactivate'),
    path('me/delete/', DeleteAccountView.as_view(), name='account-delete'),

    # ── Doctors ──────────────────────────────────────────────────────────────
    path('doctors/', DoctorProfileViewSet.as_view({'get': 'list'}), name='doctor-list'),
    path('doctors/<int:pk>/', DoctorProfileViewSet.as_view({'get': 'retrieve'}), name='doctor-detail'),
    path('categories/', CategoryListView.as_view(), name='category-list'),

    # ── Admin ────────────────────────────────────────────────────────────────
    path('members/', UserManagementListView.as_view(), name='users-list'),
]
