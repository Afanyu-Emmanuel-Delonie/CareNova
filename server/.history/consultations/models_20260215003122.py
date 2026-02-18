from django.db import models
from django.conf import settings
from labs.models import LabResult

class Diagnosis(models.Model):
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='diagnosis' 
    )
