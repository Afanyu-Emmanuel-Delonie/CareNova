import django_filters
from .models import DoctorProfile
from django.db.models import Avg

class DoctorFilter(django_filters.FilterSet):
    specialization = django_filters.CharFilter(lookup_expr='icontains')
    
    # Filter by minimum rating (e.g., show me doctors with 4+ stars)
    min_rating = django_filters.NumberFilter(method='filter_by_rating')

    class Meta:
        model = DoctorProfile
        fields = ['specialization', 'is_verified']
        
    def filter_by_rating(self, queryset, name, value):
        return queryset.annotate(
            avg_rating=Avg('reviews__rating')
        ).filter(avg_rating__gte=value)