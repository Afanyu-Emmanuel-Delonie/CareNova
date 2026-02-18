from django.urls import path
from res
from .views import RegisterView, VerifyOTPView, LoginView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    
]
