from django.urls import path
from .views import (
    AppointmentViewSet, ReviewViewSet, AvailabilitySlotViewSet,
    AvailabilityViewSet, DoctorAgendaViewSet, PatientHistoryViewSet
)

urlpatterns = [

    # ── Appointments ────────────────────────────────────────────────────────
    # IMPORTANT: collection-level actions (no <pk>) must come BEFORE
    # the <int:pk> pattern, otherwise Django will try to cast e.g.
    # "admin-traffic-monitor" as an integer and return 404.

    path(
        'appointment/',
        AppointmentViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='appointments-list-create',
    ),
    path(
        'appointment/admin-traffic-monitor/',
        AppointmentViewSet.as_view({'get': 'admin_traffic_monitor'}),
        name='appointments-admin-traffic-monitor',
    ),
    path(
        'appointment/book-recurrent/',
        AppointmentViewSet.as_view({'post': 'book_recurrent'}),
        name='appointments-book-recurrent',
    ),
    path(
        'appointment/<int:pk>/',
        AppointmentViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy',
        }),
        name='appointments-detail',
    ),
    path(
        'appointment/<int:pk>/change-status/',
        AppointmentViewSet.as_view({'post': 'change_status'}),
        name='appointments-change-status',
    ),
    path(
        'appointment/<int:pk>/reschedule/',
        AppointmentViewSet.as_view({'patch': 'reschedule'}),
        name='appointments-reschedule',
    ),
    path(
        'appointment/<int:pk>/patient-cancel/',
        AppointmentViewSet.as_view({'post': 'patient_cancel'}),
        name='appointments-patient-cancel',
    ),
    path(
        'appointment/<int:pk>/complete/',
        AppointmentViewSet.as_view({'post': 'complete_appointment'}),
        name='appointments-complete',
    ),
    path(
        'appointment/<int:pk>/cancel-series/',
        AppointmentViewSet.as_view({'post': 'cancel_series'}),
        name='appointments-cancel-series',
    ),

    # ── Patient Medical History ─────────────────────────────────────────────
    path(
        'history/',
        PatientHistoryViewSet.as_view({'get': 'list'}),
        name='patient-history-list',
    ),
    path(
        'history/<int:pk>/',
        PatientHistoryViewSet.as_view({'get': 'retrieve'}),
        name='patient-history-detail',
    ),

    # ── Reviews ─────────────────────────────────────────────────────────────
    path(
        'reviews/',
        ReviewViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='reviews-list-create',
    ),
    path(
        'reviews/<int:pk>/',
        ReviewViewSet.as_view({'get': 'retrieve'}),
        name='reviews-detail',
    ),

    # ── Availability & Slots ────────────────────────────────────────────────
    # bulk-create must come before <int:pk> for the same ordering reason above.
    path(
        'availability/',
        AvailabilitySlotViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='availability-list-create',
    ),
    path(
        'availability/bulk-create/',
        AvailabilityViewSet.as_view({'post': 'bulk_create_slots'}),
        name='availability-bulk-create',
    ),
    path(
        'availability/<int:pk>/',
        AvailabilitySlotViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy',
        }),
        name='availability-detail',
    ),

    # ── Doctor Agenda ───────────────────────────────────────────────────────
    # today/ must come before <int:pk> for the same ordering reason above.
    path(
        'agenda/',
        DoctorAgendaViewSet.as_view({'get': 'list'}),
        name='doctor-agenda-list',
    ),
    path(
        'agenda/today/',
        DoctorAgendaViewSet.as_view({'get': 'today'}),
        name='doctor-agenda-today',
    ),
    path(
        'agenda/<int:pk>/',
        DoctorAgendaViewSet.as_view({'get': 'retrieve'}),
        name='doctor-agenda-detail',
    ),
]