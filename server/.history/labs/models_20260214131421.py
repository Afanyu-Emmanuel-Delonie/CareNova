from django.db import models
from django.conf import settings

class LabResults(models.Model):
    patient = models