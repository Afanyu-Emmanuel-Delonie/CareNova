from django.contrib import admin
from .models import Diagnosis

@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    list_display = ('id', 'doctor', 'patient', 'lab_result', 'created_at')
    search_fields = ('doctor__username', 'patient__email', 'medical_opinion')
    list_filter = ('created_at',)
    
    # We make these readonly to prevent admin tampering with medical records
    readonly_fields = ('created_at',)