from django.urls import path
from .views import OrderCreateView

urlpatterns = [
    path('checkout/', OrderCreateView.as_view(), name='checkout'),
]
