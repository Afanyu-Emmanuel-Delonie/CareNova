from django.urls import path
from .views import AppointmentViewSet

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
   
]
