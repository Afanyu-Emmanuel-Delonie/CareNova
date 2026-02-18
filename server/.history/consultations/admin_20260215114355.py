from django.contrib import admin
from .models import Diagnosis

@admin.register(Diagnosis)
class 