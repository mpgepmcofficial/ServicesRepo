# mpgepmc/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Include your app URLs
    path('', include('mpgepmcservs.urls')),

    # Optional: add a health check endpoint for production monitoring
    path('health/', TemplateView.as_view(template_name='health.html'), name='health'),
]

# Serve static & media files in development (not for production!)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
