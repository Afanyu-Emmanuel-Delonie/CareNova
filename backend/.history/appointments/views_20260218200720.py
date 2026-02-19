from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Appointment
from .serializers import AppointmentSerializer
from appointments import serializers

class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == 'ADMIN':
            return Appointment.objects.all()
        
        # Doctors see appointments booked with them
        if user.role == 'DOCTOR':
            return Appointment.objects.filter(doctor__profile__user=user)
        
        # Patients see their own appointments
        return Appointment.objects.filter(patient__profile__user=user)

    def perform_create(self, serializer):
        # Automatically link the appointment to the logged-in patient's profile
        if self.request.user.role != 'PATIENT':
            raise serializers.ValidationError("Only patients can book appointments.")
        
        # We assume the signal created the profile as we set up earlier
        patient_profile = self.request.user.profile.patient_data
        serializer.save(patient=patient_profile)