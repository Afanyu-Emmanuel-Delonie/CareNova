from django.urls import path
from .views import VerifyOTPView, RegisterView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
     path("register/", RegisterView.as_view(), name="register"),
     
    #  tokens 
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
