from django.urls import path
from .views import LabUploadView, PatientLabListView, DoctorLabListView

urlpatterns = [
    # For Patients
    path('upload/', LabUploadView.as_view(), name='lab-upload'),
    path('my-results/', PatientLabListView.as_view(), name='patient-lab-list'),
    
    # For Doctors
    path('doctor/pending/', DoctorLabListView.as_view(), name='doctor-lab-list'),
]
