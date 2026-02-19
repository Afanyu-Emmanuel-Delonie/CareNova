import logging
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Shared helper (not a task — just a function)
# ─────────────────────────────────────────────
def _build_and_send_email(subject, to_email, context, template):
    """Renders a template and sends the email. Raises on failure."""
    html_content = render_to_string(f'emails/{template}.html', context)
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)


# ─────────────────────────────────────────────
# Celery Tasks
# ─────────────────────────────────────────────
@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,   # seconds before first retry
    queue='emails',
)
def send_otp_email_task(self, user_email, first_name, otp_code):
    """
    Async task: send the 6-digit OTP verification email.

    Usage:
        send_otp_email_task.delay(user.email, user.profile.first_name, otp_code)
    """
    try:
        context = {'name': first_name, 'otp': otp_code}
        _build_and_send_email(
            subject="CareNova: Verify Your Account",
            to_email=user_email,
            context=context,
            template='otp_verification',
        )
        logger.info("OTP email sent to %s", user_email)
    except Exception as exc:
        logger.warning("OTP email failed for %s (attempt %d): %s", user_email, self.request.retries + 1, exc)
        # Exponential backoff: 30s, 60s, 120s
        raise self.retry(exc=exc, countdown=30 * (2 ** self.request.retries))


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    queue='emails',
)
def send_appointment_confirmation_task(self, patient_email, context):
    """
    Async task: notify the patient their appointment is confirmed.

    Usage:
        send_appointment_confirmation_task.delay(patient_email, context)
    """
    try:
        _build_and_send_email(
            subject="Appointment Confirmed - CareNova",
            to_email=patient_email,
            context=context,
            template='appointment_confirmed',
        )
        logger.info("Confirmation email sent to %s", patient_email)
    except Exception as exc:
        logger.warning("Confirmation email failed for %s: %s", patient_email, exc)
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task(
    bind=True,
    max_retries=5,            # more retries — this is urgent
    default_retry_delay=10,   # retry quickly
    queue='urgent',           # separate high-priority queue
)
def send_emergency_alert_task(self, doctor_email, context):
    """
    Async task: alert the doctor of an emergency appointment request.

    Usage:
        send_emergency_alert_task.delay(doctor_email, context)
    """
    try:
        _build_and_send_email(
            subject="URGENT: Emergency Request - CareNova",
            to_email=doctor_email,
            context=context,
            template='emergency_alert',
        )
        logger.info("Emergency alert sent to %s", doctor_email)
    except Exception as exc:
        logger.error("Emergency alert FAILED for %s: %s", doctor_email, exc)
        raise self.retry(exc=exc, countdown=10 * (2 ** self.request.retries))


# ─────────────────────────────────────────────
# Notification classes (thin dispatchers)
# ─────────────────────────────────────────────
class AuthNotifications:
    @staticmethod
    def send_otp_email(user, otp_code):
        first_name = user.profile.first_name if hasattr(user, 'profile') else "New User"
        send_otp_email_task.delay(user.email, first_name, otp_code)


class AppointmentNotifications:
    @classmethod
    def send_confirmation(cls, appointment):
        patient_profile = appointment.patient.profile
        doctor_profile = appointment.doctor.profile

        context = {
            'patient_name': f"{patient_profile.first_name} {patient_profile.last_name}",
            'doctor_name': f"Dr. {doctor_profile.last_name}",
            'date': appointment.appointment_date.strftime('%B %d, %Y'),
            'time': appointment.appointment_time.strftime('%I:%M %p'),
            'department': getattr(appointment.doctor, 'specialization', 'General'),
        }
        send_appointment_confirmation_task.delay(patient_profile.user.email, context)

    @classmethod
    def send_emergency_alert(cls, appointment):
        doctor_profile = appointment.doctor.profile
        patient_profile = appointment.patient.profile

        context = {
            'doctor_name': f"Dr. {doctor_profile.last_name}",
            'patient_name': f"{patient_profile.first_name} {patient_profile.last_name}",
            'reason': appointment.reason,
            'time': "ASAP",
        }
        send_emergency_alert_task.delay(doctor_profile.user.email, context)