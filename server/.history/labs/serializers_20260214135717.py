from rest_framework import serializers
from .models import LabResults

class LabResultSerializer(serializers.ModelSerializer):
    class Meta:
      model = LabResult
      fields = ['id', 'title', 'result_photo', 'description', 'is_reviewed', 'created_at']
      read_only_fields = ['is_reviewed', 'created_at']