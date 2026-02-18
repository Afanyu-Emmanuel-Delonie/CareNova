from rest_framework import serializers
from .models import LabResults

class LabResultsSerializer(serializers.ModelSerializer):
    class Meta:
      model = 