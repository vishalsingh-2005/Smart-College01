import os
import sys
import pickle
import cv2
import numpy as np
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartCollege.settings')
django.setup()

from django.contrib.auth.models import User
from attendance_app.models import Attendance
from datetime import date

def recognize_and_mark_attendance():
    """
    Use webcam to recognize faces and mark attendance.
    Press 'q' to quit.
    """
    
    if not Path('face_encodings.pkl').exists():
        print("Error: face_encodings.pkl not found!")
        print("Please run train_faces.py first to generate face encodings.")
        return
    
    with open('face_encodings.pkl', 'rb') as f:
        known_encodings = pickle.load(f)
    
    print(f"Loaded {len(known_encodings)} known faces")
    
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    
    print("Webcam started. Press 'q' to quit.")
    marked_today = set()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame")
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in faces:
            face_roi = gray[y:y+h, x:x+w]
            face_resized = cv2.resize(face_roi, (100, 100))
            face_encoding = face_resized.flatten()
            
            min_distance = float('inf')
            recognized_user = None
            
            for username, known_encoding in known_encodings.items():
                distance = np.linalg.norm(face_encoding - known_encoding)
                if distance < min_distance:
                    min_distance = distance
                    recognized_user = username
            
            threshold = 3000
            if min_distance < threshold and recognized_user:
                label = f"{recognized_user}"
                color = (0, 255, 0)
                
                if recognized_user not in marked_today:
                    try:
                        user = User.objects.get(username=recognized_user)
                        attendance, created = Attendance.objects.get_or_create(
                            student=user,
                            date=date.today(),
                            defaults={'status': 'present'}
                        )
                        if created:
                            marked_today.add(recognized_user)
                            print(f"Attendance marked for {recognized_user}")
                    except User.DoesNotExist:
                        print(f"User {recognized_user} not found in database")
            else:
                label = "Unknown"
                color = (0, 0, 255)
            
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
        
        cv2.imshow('Face Recognition Attendance', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print(f"\nAttendance marked for {len(marked_today)} students today")

if __name__ == '__main__':
    recognize_and_mark_attendance()
