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
        
    )
