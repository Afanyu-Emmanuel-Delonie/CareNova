from rest_framework import serializers
from .models import LabResults

class LabResultsSerializer(serializers.ModelSerializer):
    class Meta:
      model = LabResults
      fields = ['id', 'title', 'result_photo', 'description', 'is_reviewed', 'created_at']
      read_only_fields = ['']