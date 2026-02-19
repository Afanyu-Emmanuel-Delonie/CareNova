
from core.emails import BaseEmailSender

class AppointmentNotifications:
    @staticmethod
    def send_confirmation(appointment):
        context = {
            'patient_name': appointment.patient.profile.get_full_name(),
            'doctor_name': appointment.doctor.profile.get_full_name(),
            'date': appointment.appointment_date,
        }
        BaseEmailSender.send(
            "Appointment Confirmed", 
            appointment.patient.profile.user.email, 
            context, 
            'appointment_confirmed'
        )
        
class AuthNotifications:
    @staticmethod
    def send_otp(user, otp_code):
        context = {'otp': otp_code, 'name': user.profile.first_name}
        BaseEmailSender.send(
            "Verify Your CareNova Account", 
            user.email, 
            context, 
            'otp_verification'
        )
        
