# config/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Your API endpoints
    
    # auth routes
    path("api/auth/", include("accounts.urls")),
    
    # lab result 
    path("api/lab/", include())
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # Swagger UI (Interactive Documentation)
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # ReDoc (Alternative Documentation UI)
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)