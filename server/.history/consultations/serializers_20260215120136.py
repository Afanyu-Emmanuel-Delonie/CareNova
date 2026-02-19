from rest_framework import serializers
from .models import Diagnosis, Prescription
from labs.models import LabResult


class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = ['id', 'medicine_name', 'dosage', 'frequency', 'duration', 'instructions']
class DiagnosisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diagnosis
        fields = ['id', 'lab_result', 'medical_opinion', 'recommendation', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_lab_result(self, value):
        if value.is_reviewed:
            raise serializers.ValidationError("This lab result has already been diagnosed.")
        return value