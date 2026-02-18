from django.db import models
from django.conf import settings

class LabResults(models.Model):
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lab_results"
    )
    
    results_photo = models.ImageField(upload_to='lab_results/%Y/%m/%d/')
    
    # Meta data for the lap test 
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    
    # status tracker 
    is_reviewed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    
    