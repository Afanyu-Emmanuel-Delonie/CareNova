from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Appointment
from .serializers import AppointmentSerializer
from rest_framework.exceptions import ValidationError

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
        if self.request.user.role != 'PATIENT':
            raise ValidationError("Only patients can book appointments.")
        
        
        patient_profile = self.request.user.profile.patient_data
        serializer.save(patient=patient_profile)

    @action(detail=True, methods=['post'], url_path='change-status')
    def change_status(self, request, pk=None):
        appointment = self.get_object()
        new_status = request.data.get('status')

        # Only the assigned doctor can change this appointment's status.
        if request.user.role == 'DOCTOR' and appointment.doctor.profile.user != request.user:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        valid_statuses = [choice.value for choice in Appointment.Status]
        if new_status in valid_statuses:
            if new_status == Appointment.Status.CANCELLED and appointment.is_emergency:
                doctor_user = appointment.doctor.profile.user
                doctor_user.is_flagged = True
                doctor_user.save(update_fields=['is_flagged'])
                # Hook: trigger admin alert/workflow to reassign emergency case immediately.

            appointment.status = new_status
            appointment.save(update_fields=['status', 'updated_at'])
            return Response(
                {"message": f"Appointment marked as {new_status}"},
                status=status.HTTP_200_OK,
            )

        return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='reschedule')
    def reschedule(self, request, pk=None):
        appointment = self.get_object()
        
        # Security: Ensure only the assigned doctor can reschedule
        if request.user.role != 'DOCTOR' or appointment.doctor.profile.user != request.user:
            return Response({"error": "Only the assigned doctor can reschedule this."}, status=403)

        new_date = request.data.get('appointment_date')
        new_time = request.data.get('appointment_time')

        if not new_date or not new_time:
            return Response({"error": "Both date and time are required to reschedule."}, status=400)

        # Apply the change
        appointment.appointment_date = new_date
        appointment.appointment_time = new_time
        appointment.status = 'PENDING'
        appointment.save()

        return Response({
            "message": "Appointment rescheduled. Waiting for patient confirmation.",
            "new_date": appointment.appointment_date,
            "new_time": appointment.appointment_time
        })


