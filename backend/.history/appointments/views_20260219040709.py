from datetime import date
from django.db import transaction
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from django.utils import timezone

from .models import Appointment, Review, AvailabilitySlot
from .serializers import AppointmentSerializer, ReviewSerializer, AvailabilitySlotSerializer, BulkSlotSerializer, DoctorAgendaSerializer, CompleteAppointmentSerializer, PatientHistorySerializer
from rest_framework.exceptions import ValidationError


# ──────────────────────────────────────────────────────────────
# Appointments
# ──────────────────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(
        summary="List appointments",
        description=(
            "Returns appointments scoped to the caller's role: "
            "admins see all, doctors see their own bookings, patients see their own."
        ),
        responses={200: AppointmentSerializer(many=True)},
        tags=["Appointments"],
    ),
    create=extend_schema(
        summary="Book an appointment",
        description=(
            "Creates a new appointment. Non-emergency bookings require an available "
            "AvailabilitySlot for the chosen doctor, date, and time. Emergency bookings "
            "may proceed even when no slot is available. Only patients can book."
        ),
        request=AppointmentSerializer,
        responses={
            201: AppointmentSerializer,
            400: OpenApiResponse(description="Validation error — slot unavailable or invalid payload."),
            403: OpenApiResponse(description="Only patients can book appointments."),
        },
        tags=["Appointments"],
    ),
    retrieve=extend_schema(
        summary="Retrieve an appointment",
        responses={
            200: AppointmentSerializer,
            404: OpenApiResponse(description="Appointment not found."),
        },
        tags=["Appointments"],
    ),
    update=extend_schema(
        summary="Update an appointment",
        request=AppointmentSerializer,
        responses={
            200: AppointmentSerializer,
            400: OpenApiResponse(description="Validation error."),
        },
        tags=["Appointments"],
    ),
    partial_update=extend_schema(
        summary="Partially update an appointment",
        request=AppointmentSerializer,
        responses={
            200: AppointmentSerializer,
            400: OpenApiResponse(description="Validation error."),
        },
        tags=["Appointments"],
    ),
    destroy=extend_schema(
        summary="Delete an appointment",
        responses={
            204: OpenApiResponse(description="Appointment deleted."),
            404: OpenApiResponse(description="Appointment not found."),
        },
        tags=["Appointments"],
    ),
)
class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == 'ADMIN':
            return Appointment.objects.all()
        if user.role == 'DOCTOR':
            return Appointment.objects.filter(doctor__profile__user=user)
        return Appointment.objects.filter(patient__profile__user=user)

    def perform_create(self, serializer):
        """
        Booking rules:
        - Non-emergency appointments must match an unbooked AvailabilitySlot.
        - Emergency appointments may proceed even when no slot is available.
        - When a matching slot exists, it is marked as booked.
        """
        if self.request.user.role != 'PATIENT':
            raise ValidationError("Only patients can book appointments.")

        with transaction.atomic():
            slot = AvailabilitySlot.objects.select_for_update().filter(
                doctor=serializer.validated_data['doctor'],
                date=serializer.validated_data['appointment_date'],
                start_time=serializer.validated_data['appointment_time'],
                is_booked=False,
            ).first()

            if not slot and not serializer.validated_data.get('is_emergency'):
                raise ValidationError("This time slot is no longer available.")

            if slot:
                slot.is_booked = True
                slot.save(update_fields=['is_booked'])

            patient_profile = self.request.user.profile.patient_data
            serializer.save(patient=patient_profile)

    @extend_schema(
        summary="Change appointment status",
        description=(
            "Allows the assigned doctor to update the status of an appointment. "
            "Cancelling an emergency appointment flags the doctor's account and "
            "triggers an admin alert for immediate reassignment."
        ),
        request=None,
        parameters=[
            OpenApiParameter(
                name="status",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="The new status value. Must be a valid Appointment.Status choice.",
                required=True,
            ),
        ],
        responses={
            200: OpenApiResponse(description="Status updated successfully."),
            400: OpenApiResponse(description="Invalid or missing status value."),
            403: OpenApiResponse(description="Doctor is not assigned to this appointment."),
        },
        tags=["Appointments"],
    )
    @action(detail=True, methods=['post'], url_path='change-status')
    def change_status(self, request, pk=None):
        appointment = self.get_object()
        new_status = request.data.get('status')

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

    @extend_schema(
        summary="Reschedule an appointment",
        description=(
            "Allows the assigned doctor to propose a new date and time for an appointment. "
            "On success the appointment status reverts to PENDING, awaiting patient confirmation."
        ),
        request=None,
        parameters=[
            OpenApiParameter(
                name="appointment_date",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="New appointment date (YYYY-MM-DD).",
                required=True,
            ),
            OpenApiParameter(
                name="appointment_time",
                type=OpenApiTypes.TIME,
                location=OpenApiParameter.QUERY,
                description="New appointment time (HH:MM).",
                required=True,
            ),
        ],
        responses={
            200: OpenApiResponse(description="Appointment rescheduled. Status reset to PENDING."),
            400: OpenApiResponse(description="Both date and time are required."),
            403: OpenApiResponse(description="Only the assigned doctor can reschedule."),
        },
        tags=["Appointments"],
    )
    @action(detail=True, methods=['patch'], url_path='reschedule')
    def reschedule(self, request, pk=None):
        appointment = self.get_object()

        if request.user.role != 'DOCTOR' or appointment.doctor.profile.user != request.user:
            return Response({"error": "Only the assigned doctor can reschedule this."}, status=403)

        new_date = request.data.get('appointment_date')
        new_time = request.data.get('appointment_time')

        if not new_date or not new_time:
            return Response({"error": "Both date and time are required to reschedule."}, status=400)

        appointment.appointment_date = new_date
        appointment.appointment_time = new_time
        appointment.status = 'PENDING'
        appointment.save()

        return Response({
            "message": "Appointment rescheduled. Waiting for patient confirmation.",
            "new_date": appointment.appointment_date,
            "new_time": appointment.appointment_time
        })

    @extend_schema(
        summary="Cancel appointment (patient)",
        description=(
            "Allows the patient who owns the appointment to cancel it. "
            "Cancelling a PENDING emergency appointment temporarily suspends the "
            "assigned doctor's verified status and triggers an admin alert for urgent reassignment."
        ),
        request=None,
        parameters=[
            OpenApiParameter(
                name="cancellation_reason",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Optional reason for cancellation.",
                required=False,
            ),
        ],
        responses={
            200: OpenApiResponse(description="Appointment cancelled successfully."),
            403: OpenApiResponse(description="Only the patient who owns this appointment can cancel it."),
        },
        tags=["Appointments"],
    )
    @action(detail=True, methods=['post'], url_path='patient-cancel')
    def patient_cancel(self, request, pk=None):
        appointment = self.get_object()

        if request.user.role != 'PATIENT' or appointment.patient.profile.user != request.user:
            return Response({"error": "Unauthorized"}, status=403)

        reason = request.data.get('cancellation_reason', 'Patient opted for a different provider')

        if appointment.status == Appointment.Status.PENDING and appointment.is_emergency:
            appointment.doctor.is_verified = False
            appointment.doctor.save(update_fields=['is_verified'])
            # Hook: alert admins for urgent doctor review and emergency reassignment.

        appointment.status = Appointment.Status.CANCELLED
        appointment.save(update_fields=['status', 'updated_at'])

        return Response({
            "message": "Appointment cancelled. You can now book with a different doctor.",
            "status": Appointment.Status.CANCELLED,
            "cancellation_reason": reason
        })

    @extend_schema(
        summary="Admin traffic monitor",
        description=(
            "Admin-only. Returns real-time monitoring data covering: "
            "(1) unattended emergency appointments still in PENDING status, and "
            "(2) appointments cancelled due to doctor delays that required patient rerouting."
        ),
        responses={
            200: OpenApiResponse(description="Monitoring payload with emergency and rerouting counts."),
            403: OpenApiResponse(description="Admin access only."),
        },
        tags=["Appointments"],
    )
    @action(detail=False, methods=['get'], url_path='admin-traffic-monitor')
    def admin_traffic_monitor(self, request):
        if not request.user.is_staff:
            return Response({"error": "Admin access only"}, status=403)

        unattended_emergencies = Appointment.objects.filter(
            is_emergency=True,
            status='PENDING'
        )
        rerouted_cases = Appointment.objects.filter(
            status='CANCELLED',
            reason__icontains="delay"
        )

        return Response({
            "critical_count": unattended_emergencies.count(),
            "unattended_emergencies": AppointmentSerializer(unattended_emergencies, many=True).data,
            "rerouted_cases": AppointmentSerializer(rerouted_cases, many=True).data,
        })


# ──────────────────────────────────────────────────────────────
# Reviews
# ──────────────────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(
        summary="List reviews",
        description=(
            "Returns reviews scoped to the caller's role: "
            "admins see all, doctors see reviews about them, patients see their own."
        ),
        responses={200: ReviewSerializer(many=True)},
        tags=["Reviews"],
    ),
    create=extend_schema(
        summary="Submit a review",
        description=(
            "Allows a patient to submit a review for one of their own completed appointments. "
            "Only patients can create reviews."
        ),
        request=ReviewSerializer,
        responses={
            201: ReviewSerializer,
            400: OpenApiResponse(description="Validation error — appointment doesn't belong to this patient or invalid payload."),
            403: OpenApiResponse(description="Only patients can submit reviews."),
        },
        tags=["Reviews"],
    ),
    retrieve=extend_schema(
        summary="Retrieve a review",
        responses={
            200: ReviewSerializer,
            404: OpenApiResponse(description="Review not found."),
        },
        tags=["Reviews"],
    ),
    update=extend_schema(
        summary="Update a review",
        request=ReviewSerializer,
        responses={
            200: ReviewSerializer,
            400: OpenApiResponse(description="Validation error."),
        },
        tags=["Reviews"],
    ),
    partial_update=extend_schema(
        summary="Partially update a review",
        request=ReviewSerializer,
        responses={
            200: ReviewSerializer,
            400: OpenApiResponse(description="Validation error."),
        },
        tags=["Reviews"],
    ),
    destroy=extend_schema(
        summary="Delete a review",
        responses={
            204: OpenApiResponse(description="Review deleted."),
            404: OpenApiResponse(description="Review not found."),
        },
        tags=["Reviews"],
    ),
)
class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == 'ADMIN':
            return Review.objects.all()
        if user.role == 'DOCTOR':
            return Review.objects.filter(doctor__profile__user=user)
        return Review.objects.filter(patient__profile__user=user)

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != 'PATIENT':
            raise ValidationError("Only patients can submit reviews.")

        appointment = serializer.validated_data['appointment']
        if appointment.patient.profile.user != user:
            raise ValidationError("You can only review your own appointments.")

        serializer.save()


# ──────────────────────────────────────────────────────────────
# Availability Slots
# ──────────────────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(
        summary="List availability slots",
        description=(
            "Returns availability slots scoped to the caller's role: "
            "admins see all slots, doctors see only their own, patients see only unbooked slots."
        ),
        responses={200: AvailabilitySlotSerializer(many=True)},
        tags=["Availability"],
    ),
    create=extend_schema(
        summary="Create an availability slot",
        description=(
            "Allows a doctor to publish a new availability slot for patient booking. "
            "Only doctors can create slots."
        ),
        request=AvailabilitySlotSerializer,
        responses={
            201: AvailabilitySlotSerializer,
            400: OpenApiResponse(description="Validation error."),
            403: OpenApiResponse(description="Only doctors can create availability slots."),
        },
        tags=["Availability"],
    ),
    retrieve=extend_schema(
        summary="Retrieve an availability slot",
        responses={
            200: AvailabilitySlotSerializer,
            404: OpenApiResponse(description="Slot not found."),
        },
        tags=["Availability"],
    ),
    update=extend_schema(
        summary="Update an availability slot",
        request=AvailabilitySlotSerializer,
        responses={
            200: AvailabilitySlotSerializer,
            400: OpenApiResponse(description="Validation error."),
        },
        tags=["Availability"],
    ),
    partial_update=extend_schema(
        summary="Partially update an availability slot",
        request=AvailabilitySlotSerializer,
        responses={
            200: AvailabilitySlotSerializer,
            400: OpenApiResponse(description="Validation error."),
        },
        tags=["Availability"],
    ),
    destroy=extend_schema(
        summary="Delete an availability slot",
        responses={
            204: OpenApiResponse(description="Slot deleted."),
            404: OpenApiResponse(description="Slot not found."),
        },
        tags=["Availability"],
    ),
)
class AvailabilitySlotViewSet(viewsets.ModelViewSet):
    serializer_class = AvailabilitySlotSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = AvailabilitySlot.objects.all()
        if user.is_staff or user.role == 'ADMIN':
            return queryset
        if user.role == 'DOCTOR':
            return queryset.filter(doctor__profile__user=user)
        return queryset.filter(is_booked=False)

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != 'DOCTOR':
            raise ValidationError("Only doctors can create availability slots.")
        serializer.save(doctor=user.profile.doctor_data)
  
# ──────────────────────────────────────────────────────────────
# Availability Slots
# ──────────────────────────────────────────────────────────────

class AvailabilityViewSet(viewsets.ModelViewSet):
    queryset = AvailabilitySlot.objects.all()
    serializer_class = BulkSlotSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Bulk create availability slots",
        description=(
            "Doctor-only endpoint to create multiple availability slots for a given date. "
            "Send `date`, `slots` (list of start times), and optional `duration_minutes` "
            "(default 30) to auto-calculate `end_time`."
        ),
        request=BulkSlotSerializer,
        responses={
            201: OpenApiResponse(description="Slots created successfully."),
            400: OpenApiResponse(description="Validation error."),
            403: OpenApiResponse(description="Only doctors can manage availability."),
        },
        tags=["Availability"],
    )
    @action(detail=False, methods=['post'], url_path='bulk-create')
    def bulk_create_slots(self, request):
        if request.user.role != 'DOCTOR':
            return Response({"error": "Only doctors can manage availability."}, status=403)
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            doctor_profile = request.user.profile.doctor_data
            created_slots = serializer.save(doctor=doctor_profile)
            return Response(
                {"message": f"Successfully created {len(created_slots)} slots."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)     


# ──────────────────────────────────────────────────────────────
# Daily Agenda
# ──────────────────────────────────────────────────────────────

class DoctorAgendaViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DoctorAgendaSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="List doctor's daily agenda",
        description=(
            "Doctor-only endpoint. Returns non-cancelled appointments for the authenticated doctor. "
            "Use optional `date` query parameter (YYYY-MM-DD). Defaults to today's date."
        ),
        parameters=[
            OpenApiParameter(
                name="date",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Target date for agenda filtering.",
            ),
        ],
        responses={200: DoctorAgendaSerializer(many=True)},
        tags=["Agenda"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve agenda appointment item",
        responses={
            200: DoctorAgendaSerializer,
            404: OpenApiResponse(description="Agenda item not found."),
        },
        tags=["Agenda"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Get today's agenda",
        description="Doctor-only shortcut endpoint that returns today's non-cancelled agenda items.",
        responses={200: DoctorAgendaSerializer(many=True)},
        tags=["Agenda"],
    )
    @action(detail=False, methods=['get'], url_path='today')
    def today(self, request):
        if request.user.role != 'DOCTOR':
            return Response([], status=status.HTTP_200_OK)

        doctor = request.user.profile.doctor_data
        qs = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=timezone.now().date(),
        ).exclude(status=Appointment.Status.CANCELLED).order_by('appointment_time')

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        if self.request.user.role != 'DOCTOR':
            return Appointment.objects.none()

        doctor = self.request.user.profile.doctor_data
        date_str = self.request.query_params.get('date')
        if date_str:
            try:
                target_date = date.fromisoformat(date_str)
            except ValueError:
                target_date = timezone.now().date()
        else:
            target_date = timezone.now().date()

        return Appointment.objects.filter(
                doctor=doctor,
                appointment_date=target_date
            ).exclude(status=Appointment.Status.CANCELLED).order_by('appointment_time')

# ──────────────────────────────────────────────────────────────
# Clinical Note
# ──────────────────────────────────────────────────────────────

@action(detail=True, methods=['post'], url_path='complete')
def complete_appointment(self, request, pk=None):
    appointment = self.get_object()
    
    # Security: Only the assigned doctor can complete it
    if request.user.role != 'DOCTOR' or appointment.doctor.profile.user != request.user:
        return Response({"error": "Unauthorized"}, status=403)

    if appointment.status != 'CONFIRMED':
        return Response({"error": "Only confirmed appointments can be completed."}, status=400)

    serializer = CompleteAppointmentSerializer(appointment, data=request.data)
    if serializer.is_valid():
        serializer.save(status='COMPLETED')
        return Response({"message": "Appointment marked as completed. Patient can now leave a review."})
    
    return Response(serializer.errors, status=400)

class PatientHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PatientHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        patient = self.request.user.users.patien

