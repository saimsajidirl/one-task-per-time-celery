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
