from .models import OTP
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import st


def generate_otp(user, otp_type):
    """
    Generate a new OTP.
    Delete old unused OTPs of the same type.
    """

    OTP.objects.filter(
        user=user,
        is_used=False,
        otp_type=otp_type
    ).delete()

    return OTP.objects.create(user=user, otp_type=otp_type)


def verify_otp(user, otp_type, code):
    try:
        otp = OTP.objects.get(
            user=user,
            otp_type=otp_type,
            code=code,
            is_used=False
        )
    except OTP.DoesNotExist:
        return False

    if otp.is_expired():
        return False

    otp.mark_as_used()
    return True


def send_otp_email(user, otp):
    print(f"Sending OTP {otp.code} to {user.email}")
