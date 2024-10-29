# your_project/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from your_app.views import upload_image

urlpatterns = [
    path('upload-image/', upload_image, name='upload-image'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
