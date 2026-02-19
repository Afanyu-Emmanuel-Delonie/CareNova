from django.urls import path
from .views import AppointmentViewSet, ReviewViewSet, AvailabilitySlotViewSet

urlpatterns = [
    path('appointment/', AppointmentViewSet.as_view({'get': 'list', 'post': 'create'}), name='appointments-list-create'),
    path('appointment/<int:pk>/', AppointmentViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'put': 'update', 'delete': 'destroy'}), name='appointments-detail'),
    path('appointment/<int:pk>/change-status/', AppointmentViewSet.as_view({'post': 'change_status'}), name='appointments-change-status'),
    path('appointment/<int:pk>/reschedule/', AppointmentViewSet.as_view({'patch': 'reschedule'}), name='appointments-reschedule'),
    path('appointment/<int:pk>/patient-cancel/', AppointmentViewSet.as_view({'post': 'patient_cancel'}), name='appointments-patient-cancel'),
    path('appointment/admin-traffic-monitor/', AppointmentViewSet.as_view({'get': 'admin_traffic_monitor'}), name='appointments-admin-traffic-monitor'),
    
    path('reviews/', ReviewViewSet.as_view({'get': 'list', 'post': 'create'}), name='reviews-list-create'),
    path('reviews/<int:pk>/', ReviewViewSet.as_view({'get': 'retrieve'}), name='reviews-detail'),
    path('availability/', AvailabilitySlotViewSet.as_view({'get': 'list', 'post': 'create'}), name='availability-list-create'),
    path('availability/<int:pk>/', AvailabilitySlotViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'put': 'update', 'delete': 'destroy'}), name='availability-detail'),
]
