from django.urls import path
from .views import (
    AppointmentViewSet, ReviewViewSet, AvailabilitySlotViewSet, 
    AvailabilityViewSet, DoctorAgendaViewSet, PatientHistoryViewSet
)

urlpatterns = [
    # --- Appointment Management ---
    path('appointment/', AppointmentViewSet.as_view({'get': 'list', 'post': 'create'}), name='appointments-list-create'),
    path('appointment/<int:pk>/', AppointmentViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'put': 'update', 'delete': 'destroy'}), name='appointments-detail'),
    path('appointment/<int:pk>/change-status/', AppointmentViewSet.as_view({'post': 'change_status'}), name='appointments-change-status'),
    path('appointment/<int:pk>/reschedule/', AppointmentViewSet.as_view({'patch': 'reschedule'}), name='appointments-reschedule'),
    path('appointment/<int:pk>/patient-cancel/', AppointmentViewSet.as_view({'post': 'patient_cancel'}), name='appointments-patient-cancel'),
    path('appointment/<int:pk>/complete/', AppointmentViewSet.as_view({'post': 'complete_appointment'}), name='appointments-complete'),
    path('appointment/admin-traffic-monitor/', AppointmentViewSet.as_view({'get': 'admin_traffic_monitor'}), name='appointments-admin-traffic-monitor'),
    
    # --- Patient Medical Records ---
    path('history/', PatientHistoryViewSet.as_view({'get': 'list'}), name='patient-history'),

    # --- Reviews ---
    path('reviews/', ReviewViewSet.as_view({'get': 'list', 'post': 'create'}), name='reviews-list-create'),
    path('reviews/<int:pk>/', ReviewViewSet.as_view({'get': 'retrieve'}), name='reviews-detail'),
    
    # --- Availability & Slots ---
    path('availability/', AvailabilitySlotViewSet.as_view({'get': 'list', 'post': 'create'}), name='availability-list-create'),
    path('availability/<int:pk>/', AvailabilitySlotViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'put': 'update', 'delete': 'destroy'}), name='availability-detail'),
    path('availability/bulk-create/', AvailabilityViewSet.as_view({'post': 'bulk_create_slots'}), name='availability-bulk-create'),
    
    # --- Doctor Agenda ---
    path('agenda/', DoctorAgendaViewSet.as_view({'get': 'list'}), name='doctor-agenda-list'),
    path('agenda/today/', DoctorAgendaViewSet.as_view({'get': 'today'}), name='doctor-agenda-today'),
    path('agenda/<int:pk>/', DoctorAgendaViewSet.as_view({'get': 'retrieve'}), name='doctor-agenda-detail'),
]