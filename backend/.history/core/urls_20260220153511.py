from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),

    # apps api endpoints
    path('api/v1/users/', include('users.urls')),
    path('api/v1/appointments/', include('appointments.urls')),
    path('api/v1/chats/', include('chat.urls')),
    path('api/v1/news/', include('news.urls')),

    # Schema Generation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # UI for the documentation
    path('api/v1/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# Serve media files in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)