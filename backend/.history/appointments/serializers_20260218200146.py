from rest_framework import serializers
from .models import Appointment
from users.models import DoctorProfile
from django.utils import timezone


class AppointmentSerializer(serializers.ModelSerializer):
    doctorName = serializers.ReadOnlyField(source=)

