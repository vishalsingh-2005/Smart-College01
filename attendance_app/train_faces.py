import os
import pickle
import cv2
import numpy as np
from pathlib import Path

def train_faces():
    """
    Train face encodings from student images.
    Place student images in 'student_images/' folder with naming convention: username.jpg
    This script will generate face encodings and save them to 'face_encodings.pkl'
    """
    
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    student_images_dir = Path('student_images')
    if not student_images_dir.exists():
        print(f"Creating {student_images_dir} directory...")
        student_images_dir.mkdir()
        print(f"Please add student images to {student_images_dir}/ with format: username.jpg")
        return
    
    encodings_data = {}
    
    for image_file in student_images_dir.glob('*.jpg'):
        username = image_file.stem
        print(f"Processing {username}...")
        
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
            
            encoding = face_resized.flatten()
            encodings_data[username] = encoding
            print(f"Encoded face for {username}")
            break
    
    if encodings_data:
        with open('face_encodings.pkl', 'wb') as f:
            pickle.dump(encodings_data, f)
        print(f"\nSuccessfully trained {len(encodings_data)} faces!")
        print("Encodings saved to face_encodings.pkl")
    else:
        print("No faces were encoded. Please check your images.")

if __name__ == '__main__':
    train_faces()
