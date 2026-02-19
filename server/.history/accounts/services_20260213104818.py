from .models import OTP
from django.utils import timezone

def generate_otp(user, otp_type):
    """
    here we will generate a new otp
    also we will delete the old otp that was created
    """
    # delete the old otp that was created of same type 
    OTP.objects.filter(
        user=user,
        is_used=False,
        otp_type=otp_type
    ).delete()
    
    # creating a new otp 
    OTP.objects.create(user=user, otp_type=otp_type)
    
    return OTP

def verify_otp(user, otp_type, code):
    try:
        otp = OTP.objects.get(
            user=user, otp_type=otp_type, code=code, is_used=False
        )
    except OTP.DoesNotExist:
        return False
    
    if OTP.is