# SmartCollege - College Management System

A comprehensive Django-based college management system with five integrated applications.

## Features

### 1. College App (Authentication & Dashboard)
- User authentication (login/signup)
- Role-based access control (Admin, Student, Teacher, Doctor)
- Profile management with user roles
- Role-specific dashboards

### 2. Library App (E-Library System)
- Document upload functionality
- Document listing and browsing
- File download capability
- Access control based on user roles

### 3. Chat App (Real-time Communication)
- WebSocket-based real-time chat
- One-to-one messaging between Students and Teachers
- Live message delivery using Django Channels

### 4. Healthcare App (Medical Management)
- Health record management
- Doctor-patient interaction
- Appointment booking system
- Medical history tracking

### 5. Attendance App (Face Recognition)
- Face recognition-based attendance marking
- Training script for face encodings
- Automated attendance tracking
- Attendance reports and analytics

## Technology Stack

- **Backend**: Django 5.2.7
- **Real-time**: Django Channels with WebSockets
- **API**: Django REST Framework
- **Face Recognition**: OpenCV
- **Database**: SQLite (default, can be changed to PostgreSQL)
- **ASGI Server**: Daphne

## Installation & Setup

### Prerequisites
- Python 3.11 or higher
- Webcam (for face recognition attendance)

### Step 1: Install Dependencies
```bash
pip install django djangorestframework channels channels-redis daphne opencv-python-headless Pillow numpy
```

Or using the provided requirements:
```bash
pip install -r pyproject.toml
```

### Step 2: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 3: Create Superuser
```bash
python manage.py createsuperuser
```

### Step 4: Create Static and Media Directories
```bash
python manage.py collectstatic --noinput
```

### Step 5: Run the Development Server
```bash
python manage.py runserver 0.0.0.0:5000
```

The application will be available at `http://localhost:5000`

## Face Recognition Setup

### Training Face Encodings
1. Create a directory called `student_images/` in the project root
2. Add student images with naming format: `username.jpg`
3. Run the training script:
```bash
python attendance_app/train_faces.py
```

### Running Face Recognition Attendance
```bash
python attendance_app/recognize_attendance.py
```
Press 'q' to quit the webcam view.

## User Roles

- **Admin**: Full access to all features
- **Student**: Access to library, chat with teachers, view health records, book appointments, view attendance
- **Teacher**: Upload documents, chat with students, view attendance reports
- **Doctor**: Manage health records, view appointments

## Application Structure

```
SmartCollege/
├── college_app/          # Authentication and dashboards
├── library_app/          # E-library system
├── chat_app/             # Real-time chat with WebSockets
├── healthcare_app/       # Healthcare management
├── attendance_app/       # Face recognition attendance
├── templates/            # HTML templates
├── static/              # Static files (CSS, JS)
├── media/               # Uploaded files
└── SmartCollege/        # Project settings
```

## URLs

- `/` - Home (redirects to login)
- `/login/` - User login
- `/signup/` - User registration
- `/dashboard/` - Role-based dashboard
- `/library/` - E-library
- `/chat/` - Chat system
- `/healthcare/` - Healthcare management
- `/attendance/` - Attendance system
- `/admin/` - Django admin panel

## Notes

- Chat uses an in-memory channel layer for development (no Redis required)
- For production chat with multiple server instances, consider using Redis channel layer
- For face recognition, ensure you have proper webcam access
- Face encodings are stored in the database (FaceEncoding model)
- Default database is SQLite; change in settings.py for production use
- Configure ALLOWED_HOSTS in settings.py for deployment

## Development

To run in development mode:
```bash
python manage.py runserver 0.0.0.0:5000
```

For production deployment, use a proper ASGI server like Daphne:
```bash
daphne -b 0.0.0.0 -p 5000 SmartCollege.asgi:application
```
