import os
import cv2
import numpy as np
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartCollege.settings')
django.setup()

from django.contrib.auth.models import User
from attendance_app.models import FaceEncoding

def train_faces():
    """
    Train face encodings from student images and save to database.
    Place student images in 'student_images/' folder with naming convention: username.jpg
    This script will generate face encodings and save them to the FaceEncoding model
    """
    
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    student_images_dir = Path('student_images')
    if not student_images_dir.exists():
        print(f"Creating {student_images_dir} directory...")
        student_images_dir.mkdir()
        print(f"Please add student images to {student_images_dir}/ with format: username.jpg")
        return
    
    encoded_count = 0
    
    for image_file in student_images_dir.glob('*.jpg'):
        username = image_file.stem
        print(f"Processing {username}...")
        
        try:
            user = User.objects.get(username=username, profile__role='student')
        except User.DoesNotExist:
            print(f"Student user {username} not found in database. Skipping...")
            continue
        
        img = cv2.imread(str(image_file))
        if img is None:
            print(f"Could not read image: {image_file}")
            continue
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            print(f"No face detected in {image_file}")
            continue
        
        for (x, y, w, h) in faces:
            face_roi = gray[y:y+h, x:x+w]
            face_resized = cv2.resize(face_roi, (100, 100))
            
            encoding = face_resized.flatten().astype(np.float32)
            encoding_bytes = encoding.tobytes()
            
            face_encoding, created = FaceEncoding.objects.update_or_create(
                student=user,
                defaults={'encoding': encoding_bytes}
            )
            
            if created:
                print(f"Created face encoding for {username}")
            else:
                print(f"Updated face encoding for {username}")
            
            encoded_count += 1
            break
    
    if encoded_count > 0:
        print(f"\nSuccessfully trained {encoded_count} faces!")
        print("Encodings saved to database (FaceEncoding model)")
    else:
        print("No faces were encoded. Please check your images and ensure student users exist in the database.")

if __name__ == '__main__':
    train_faces()
