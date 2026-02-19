from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

class AuthNotifications:
    @staticmethod
    def send_otp_email(user, otp_code):
        """
        Sends the 6-digit activation OTP to the user's email.
        """
        subject = "CareNova: Verify Your Account"
        context = {
            'name': user.profile.first_name if hasattr(user, 'profile') else "New User",
            'otp': otp_code
        }
        
        # Load the template we created in Step 1
        html_content = render_to_string('emails/otp_verification.html', context)
        text_content = strip_tags(html_content) 

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(html_content, "text/html")
        
        try:
            email.send(fail_silently=False)
            return True
        except Exception as e:
            # In a real app, you'd log this error to a file
            print(f"SMTP Error: {e}")
            return False
        
class AppointmentNotifications:
    @staticmethod
    def _send(subject, to_email, context, template):
        html_content = render_to_string(f'emails/{template}.html', context)
        text_content = strip_tags(html_content)
        email = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [to_email])
        email.attach_alternative(html_content, "text/html")
        return email.send(fail_silently=False)

    @classmethod
    def send_confirmation(cls, appointment):
       patient_email = appointment.patient.user.email 
    
       context = {
            'patient_name': f"{appointment.patient.first_name} {appointment.patient.last_name}",
            'doctor_name': appointment.doctor.last_name,
            'date': appointment.appointment_date.strftime('%B %d, %Y'),
            'time': appointment.appointment_time.strftime('%I:%M %p'),
            'department': getattr(appointment.doctor, 'specialization', 'General')
        }
    return cls._send("Appointment Confirmed - CareNova", patient_email, context, 'appointment_confirmed')

    @classmethod
    def send_emergency_alert(cls, appointment):
        context = {
            'doctor_name': appointment.doctor.profile.last_name,
            'patient_name': f"{appointment.patient.profile.first_name} {appointment.patient.profile.last_name}",
            'reason': appointment.reason,
            'time': "ASAP"
        }
        return cls._send("URGENT: Emergency Request", appointment.doctor.email, context, 'emergency_alert')

