from django.db import models
from django.conf import settings

class LabResults(models.Model):
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lab_results"
    )
    
    results_photo = models.ImageField(upload_to="")
    
    