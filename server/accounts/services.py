# accounts/services.py

from .models import OTP
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def generate_otp(email, purpose='registration'):
    """
    Generate a new OTP.
    Delete old unused OTPs of the same purpose for this email.
    """
    # Delete old unverified OTPs
    OTP.objects.filter(
        email=email,
        is_verified=False,
        purpose=purpose
    ).delete()

    # Create new OTP
    return OTP.objects.create(email=email, purpose=purpose)


def verify_otp(email, otp_code, purpose='registration'):
    """
    Verify an OTP code.
    Returns True if valid, False otherwise.
    """
    try:
        otp = OTP.objects.get(
            email=email,
            purpose=purpose,
            otp_code=otp_code,
            is_verified=False
        )
    except OTP.DoesNotExist:
        logger.warning(f"OTP not found for {email}")
        return False

    # Check if expired
    if timezone.now() > otp.expires_at:
        logger.warning(f"OTP expired for {email}")
        return False

    # Mark as verified
    otp.is_verified = True
    otp.save(update_fields=['is_verified'])
    
    logger.info(f"OTP verified successfully for {email}")
    return True


def send_otp_email(email, otp_code, purpose='registration'):
    """
    Send OTP email to user.
    """
    if purpose == 'registration':
        subject = f"{otp_code} is your CareNova verification code"
    elif purpose == 'password_reset':
        subject = f"{otp_code} is your CareNova password reset code"
    else:
        subject = f"{otp_code} is your CareNova verification code"
    
    from_email = settings.DEFAULT_FROM_EMAIL
    to = email
    
    # Context for the html template 
    context = {
        'otp_code': otp_code,
        'user_email': email,
        'purpose': purpose
    }
    
    try:
        # Try to use HTML template if it exists
        html_content = render_to_string('emails/otp_email.html', context)
        text_content = strip_tags(html_content)
        
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
    except Exception:
        # Fallback to plain text email if template doesn't exist
        text_content = f"""
        Hello,
        
        Your verification code is: {otp_code}
        
        This code will expire in 10 minutes.
        
        If you didn't request this code, please ignore this email.
        
        Best regards,
        CareNova Team
        """
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    
    try:
        msg.send()
        logger.info(f"OTP email sent successfully to {email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send OTP email to {email}: {str(e)}")
        return False