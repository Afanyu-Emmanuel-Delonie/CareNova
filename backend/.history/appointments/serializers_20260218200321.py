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

