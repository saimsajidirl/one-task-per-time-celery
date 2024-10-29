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
