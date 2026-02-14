from django.urls import path
from .views import VerifyOTPView

urlpatterns = [
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
     path("register/", RegisterView.as_view(), name="register"),
]
