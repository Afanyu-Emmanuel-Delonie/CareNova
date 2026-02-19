from django.urls import path
from .views import CreateDiagnosisView, PatientMedicalHistoryView, AddPrescriptionView

urlpatterns = [
    path('diagnose/', CreateDiagnosisView.as_view(), name='create-diagnosis'),
    path('diagnose/<int:diagnosis_id>/prescribe/', AddPrescriptionView.as_view(), name='add-prescription'),
    path('history/', PatientMedicalHistoryView.as_view(), name='medical-history'),
]