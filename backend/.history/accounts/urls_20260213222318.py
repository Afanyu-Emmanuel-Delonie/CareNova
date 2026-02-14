from django.urls import path
from .views import VerifyOTPView, RegisterView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
     path("register/", RegisterView.as_view(), name="register"),
     
     
]
