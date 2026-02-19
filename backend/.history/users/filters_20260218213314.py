import django_filters
from .models import DoctorProfile
from django.db.models import Avg

class DoctorFilter(django_filters.FilterSet):
    specialization = django_filters.CharFilter(lookup_expr='icontains')
    