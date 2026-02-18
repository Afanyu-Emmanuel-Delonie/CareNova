from rest_framework import serializers
from .models import LabResults

class LabResultsSerializer(serializers.ModelSerializer):
    class Meta:
        db_table = ''
        managed = True
        verbose_name = 'ModelName'
        verbose_name_plural = 'ModelNames'