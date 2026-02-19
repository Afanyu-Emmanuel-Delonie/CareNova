from django.urls import path
from .views import AppointmentViewSet

urlpatterns = [
    path('appointments/', AppointmentViewSet.as_view(), name='register'),
   
]
