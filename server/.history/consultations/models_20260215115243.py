from django.db import models
from django.conf import settings
from labs.models import LabResult

class Diagnosis(models.Model):
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='diagnosis' 
    )
    
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='received_diagnoses'
    )
    
    # we add the lab results that we use for the consultation 
    lab_result = models.OneToOneField(
        LabResult,
        on_delete=models.SET_NULL,
        null=True,
        related_name='dianosis'
    )
    
    medical_opinion = models.TextField()
    recommendation = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Diagnosis for {self.patient.email} by Dr. {self.doctor.username}"

class Prescription(models.Model):
    diagnosis = models.ForeignKey(
        Diagnosis,
        on_delete=models.CASCADE,
        related_name='prescriptions'
    )
    
    medicine_name = models.CharField(max_length=255)
    dosage = models

