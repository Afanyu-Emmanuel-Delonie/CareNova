from .models import OTP
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


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
    subject = f"{otp.code} is your CareNova verification code"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = user.email
    
    # content for the html template 
    context = {
        'otp_code': otp.code,
        'user_email': user.email
    }
    
    html_content = render_to_string('otp_email.html', context)
    text_content = strip_
