from django.urls import path
from .views import AppointmentViewSet

urlpatterns = [
    path('appointment/', AppointmentViewSet.as_view(), name='appoint'),
   
]
