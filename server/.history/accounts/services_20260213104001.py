from .models import OTP
from django.utils import timezone

def generate_otp(user, otp_type):
    """
   here we will generate a new otp
    """