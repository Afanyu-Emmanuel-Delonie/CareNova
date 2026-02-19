from django.contrib import admin
from .models import LabResult

@admin.register(LabResult)
class LabResultsAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'title', 'is_reviewed', 'created_at')
    list_filter = ('is_reviewed', 'created_at')
    search_fields = ('patient__email', 'title')
    readonly_fields = ('created_at', 'updated_at')
    
    # This makes the admin list more readable
    list_editable = ('is_reviewed',)