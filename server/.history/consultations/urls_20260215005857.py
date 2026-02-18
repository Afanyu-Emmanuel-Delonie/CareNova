from django.urls import path
from .views import CreateDiagnosisView, PatientMedicalHistoryView

urlpatterns = [
    path('diagnose/', CreateDiagnosisView.as_view(), name='create-diagnosis'),
    path('history/', PatientMedicalHistoryView.as_view(), name='medical-history'),
]