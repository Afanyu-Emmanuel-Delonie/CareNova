from rest_framework import serializers
from .models import Appointment
from users.models import DoctorProfile
from django.utils import timezone


class AppointmentSerializer(serializers.ModelSerializer):
    doctor_name = serializers.ReadOnlyField(source='doctor.users.get_full_name')
    patient_name = serializers.ReadOnlyField(source='users.profile.get_full_name')
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'doctor', 'doctor_name', 'patient_name', 
            'appointment_date', 'appointment_time', 
            'is_emergency', 'reason', 'status', 'created_at'
        ]
        read_only_fields = ['status', 'patient']
        
    def validate_appointment_date(self, value):
        """Check that the date is not in the past."""
        if value < timezone.now().date():
            raise serializers.ValidationError("You cannot book an appointment in the past.")
        return value

    def validate(self, data):
        """Check for double booking."""
        doctor = data.get('doctor')
        date = data.get('appointment_date')
        time = data.get('appointment_time')

        if Appointment.objects.filter(
            doctor=doctor, 
                appointment_date=date, 
                appointment_time=time,
                status__in=['PENDING', 'CONFIRMED']
            ).exists():
            raise serializers.ValidationError(
                    "This doctor is already booked for this time slot. Please choose another."
                )
            return data

