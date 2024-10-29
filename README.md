# one-task-per-time-celery

Sure! Here is the full code setup for an image resizing task using Celery in Django. This includes all necessary configurations, models, views, and templates to get it running smoothly.
1. Celery Configuration (your_project/celery.py)

python

# your_project/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')

app = Celery('your_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

2. Django Settings (your_project/settings.py)

Add the Celery broker configuration in your Django settings.

python

# your_project/settings.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Update this if your Redis setup is different

# Ensure media files are accessible
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

3. Celery Task for Image Resizing (your_app/tasks.py)

python

# your_app/tasks.py
from celery import shared_task, current_app
import redis
from PIL import Image
import os

# Connect to Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

@shared_task(bind=True)
def resize_image(self, image_path, output_size=(300, 300)):
    """Resize the image to the specified output size."""
    print(f"Processing image: {image_path}")
    img = Image.open(image_path)
    img = img.resize(output_size)
    
    # Save the resized image
    base, ext = os.path.splitext(image_path)
    output_path = f"{base}_resized{ext}"
    img.save(output_path)
    print(f"Image saved to: {output_path}")

def add_resize_task(image_path):
    # Fetch the previous task ID if it exists
    previous_task_id = redis_client.get('latest_task_id')

    # Revoke the previous task if it's still active
    if previous_task_id:
        current_app.control.revoke(previous_task_id.decode(), terminate=True)

    # Launch a new resize task
    new_task = resize_image.apply_async(args=[image_path])

    # Store the new task ID in Redis
    redis_client.set('latest_task_id', new_task.id)
    return new_task

4. Image Upload Form (your_app/forms.py)

python

# your_app/forms.py
from django import forms

class ImageUploadForm(forms.Form):
    image = forms.ImageField()

5. Image Upload View (your_app/views.py)

This view will handle image upload and trigger the resizing task.

python

# your_app/views.py
from django.shortcuts import render
from django.http import JsonResponse
from .tasks import add_resize_task
from .forms import ImageUploadForm
import os

def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = request.FILES['image']
            image_path = os.path.join('media/uploaded_images/', image.name)

            # Save the uploaded image to the media directory
            with open(image_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)

            # Trigger the image resizing task
            add_resize_task(image_path)

            return JsonResponse({'status': 'Image uploaded and resizing task added!'})
    else:
        form = ImageUploadForm()
    return render(request, 'upload.html', {'form': form})

6. URL Configuration (your_project/urls.py)

Add a URL for the image upload view.

python

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

7. HTML Template for Image Upload (templates/upload.html)

Create the upload.html file to allow users to upload images.

html

<!-- templates/upload.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Upload</title>
</head>
<body>
    <h1>Upload an Image</h1>
    <form method="POST" enctype="multipart/form-data">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Upload</button>
    </form>
</body>
</html>

8. Create the Media Directory

Make sure the media/uploaded_images/ directory exists. This is where uploaded images will be saved, and the resized images will be outputted.

bash

mkdir -p media/uploaded_images/

9. Running the Application

    Start Redis Server:

    bash

redis-server

Start Celery Worker:

bash

celery -A your_project worker --loglevel=info

Run Django Development Server:

bash

    python manage.py runserver

10. Testing the Setup

    Open your browser and go to http://127.0.0.1:8000/upload-image/.
    Use the upload form to submit an image.
    The image will be saved in media/uploaded_images/, and a resizing task will be queued. If you upload a new image before the previous task completes, the previous task will be canceled, and only the latest task will run.

This setup should now allow you to use Celery in Django to handle image resizing tasks, ensuring that only the latest task is processed. Let me know if you have any further questions!





