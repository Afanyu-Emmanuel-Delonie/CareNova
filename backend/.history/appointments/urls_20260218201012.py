from django.urls import path
from .views import AppointmentViewSet

urlpatterns = [
    path('register/', AppointmentViewSet.as_view(), name='register'),
   
]
