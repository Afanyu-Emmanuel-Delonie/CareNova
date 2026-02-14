from .models import OTP
from django.utils import timezone

def generate_otp(user, otp_type):
    """_summary_

    Args:
        user (_type_): _description_
        otp_type (_type_): _description_
    """