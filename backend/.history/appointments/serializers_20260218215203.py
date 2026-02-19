from rest_framework import serializers
from .models import Appointment, Review, AvailabilitySlot
from users.models import DoctorProfile
from django.utils import timezone


class AppointmentSerializer(serializers.ModelSerializer):
    doctor = serializers.UUIDField(write_only=True)
    doctor_id = serializers.UUIDField(source='doctor.profile.user.id', read_only=True)
    patient_name = serializers.SerializerMethodField()
    patient_blood_group = serializers.ReadOnlyField(source='patient.blood_group')
    patient_phone = serializers.ReadOnlyField(source='patient.profile.phone_number')
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'doctor', 'doctor_id', 'patient_name', 'patient_blood_group', 'patient_phone',
            'appointment_date', 'appointment_time', 'is_emergency', 'reason', 'status'
        ]
        read_only_fields = ['status', 'patient']

    def get_patient_name(self, obj):
        profile = getattr(obj.patient, 'profile', None)
        if profile:
            return f"{profile.first_name} {profile.last_name}".strip()
        return None

    def validate_doctor(self, value):
        try:
            return DoctorProfile.objects.get(profile__user__id=value)
        except DoctorProfile.DoesNotExist:
            raise serializers.ValidationError("Invalid doctor id.")
        
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


class ReviewSerializer(serializers.ModelSerializer):
    doctor_name = serializers.SerializerMethodField(read_only=True)
    patient_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'appointment', 'doctor', 'doctor_name', 'patient', 'patient_name',
            'rating', 'comment', 'created_at'
        ]
        read_only_fields = ['doctor', 'patient', 'created_at']

    def get_doctor_name(self, obj):
        profile = getattr(obj.doctor, 'profile', None)
        if profile:
            return f"{profile.first_name} {profile.last_name}".strip()
        return None

    def get_patient_name(self, obj):
        profile = getattr(obj.patient, 'profile', None)
        if profile:
            return f"{profile.first_name} {profile.last_name}".strip()
        return None

    def validate(self, data):
        appointment = data.get('appointment')
        if appointment.status != Appointment.Status.COMPLETED:
            raise serializers.ValidationError(
                "You can only review an appointment after it has been completed."
            )
        return data

    def create(self, validated_data):
        appointment = validated_data['appointment']
        validated_data['doctor'] = appointment.doctor
        validated_data['patient'] = appointment.patient
        return super().create(validated_data)


class AvailabilitySlotSerializer(serializers.ModelSerializer):
    doctor_id = serializers.UUIDField(source='doctor.profile.user.id', read_only=True)
    doctor_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AvailabilitySlot
        fields = ['id', 'doctor', 'doctor_id', 'doctor_name', 'date', 'start_time', 'end_time', 'is_booked']
        read_only_fields = ['doctor', 'is_booked']

    def get_doctor_name(self, obj):
        profile = getattr(obj.doctor, 'profile', None)
        if profile:
            return f"{profile.first_name} {profile.last_name}".strip()
        return None

    def validate(self, data):
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError("end_time must be later than start_time.")
        return data


