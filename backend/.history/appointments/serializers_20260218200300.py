from rest_framework import serializers
from .models import Appointment
from users.models import DoctorProfile
from django.utils import timezone


class AppointmentSerializer(serializers.ModelSerializer):
    doctor_name = serializers.ReadOnlyField(source='doctor.users.get_full_name')
    patient_name = serializers.ReadOnlyField(source='users.profile.get_full_name')
    
    

