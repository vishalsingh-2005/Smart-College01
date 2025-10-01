# SmartCollege - College Management System

## Overview

SmartCollege is a comprehensive Django-based college management system that integrates five core functional modules: authentication & user management, digital library, real-time chat, healthcare management, and face recognition-based attendance tracking. The system supports role-based access control for four user types: Admin, Student, Teacher, and Doctor, with each role having specific permissions and accessible features.

The application is built using Django 5.2.7 as the primary web framework, with Django Channels enabling real-time WebSocket communication for the chat feature. Face recognition capabilities are implemented using OpenCV for automated attendance marking. The system uses Django's built-in ORM for database operations, currently configured with SQLite but designed to be database-agnostic.

## Recent Changes (October 1, 2025)

**Latest Updates:**
1. ✅ Fixed URL routing conflict - Changed admin management URLs from `/admin/` to `/manage/` to avoid conflicts with Django's built-in admin interface
2. ✅ Added comprehensive payment management system for admins (create fee structures, view all payments)
3. ✅ Added student fee payment interface with payment history
4. ✅ Added notice board and bulletin board features for all users
5. ✅ Added bus tracker for students to track school bus locations
6. ✅ Added complete assignment management for teachers (create, view submissions, grade)
7. ✅ Added assignment submission system for students
8. ✅ Implemented strict role-based access control with ownership checks for teacher assignments
9. ✅ Updated dashboard with all new features for each role

**Previous Fixes:**
1. ✅ Resolved 403 Forbidden error on POST requests by adding CSRF_TRUSTED_ORIGINS configuration
2. ✅ Added REST API endpoint at `/attendance/api/mark/` for programmatic attendance marking
3. ✅ Configured CSRF_TRUSTED_ORIGINS to dynamically read from REPLIT_DOMAINS environment variable

**Application Status:** Fully functional and ready for use

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Application Structure
The project follows a modular Django app architecture with five specialized apps, each handling distinct functional domains:

**College App (Core Authentication & Dashboard)**
- Manages user authentication flows (login/signup/logout)
- Implements Profile model extending Django's User model with role-based attributes (role, phone, address, date_of_birth)
- Provides role-specific dashboard views with conditional feature access
- Acts as the central routing hub for the entire application

**Library App (Document Management)**
- Provides digital library functionality with document upload, browsing, and download capabilities
- Implements file storage using Django's FileField with media file handling
- Access control restricts uploads to teachers and admins while allowing all authenticated users to view/download
- Document model tracks title, description, file, uploader, and timestamp

**Chat App (Real-time Messaging)**
- Implements WebSocket-based real-time communication using Django Channels
- Uses ASGI protocol routing configured in asgi.py with Daphne server
- ChatMessage model stores message history with sender/receiver relationships
- Restricts chat functionality to Student-Teacher interactions only
- Channel layers enable live message broadcasting within chat rooms

**Healthcare App (Medical Records)**
- Manages medical records and appointment scheduling
- HealthRecord model links students with doctors, storing diagnoses and prescriptions
- Appointment model implements status workflow (pending → confirmed → completed/cancelled)
- Role-based views: doctors create records, students book appointments, both can view their respective data

**Attendance App (Face Recognition)**
- Implements face recognition-based attendance tracking using OpenCV
- FaceEncoding model stores binary face encodings linked to student users
- Attendance model enforces unique daily attendance per student
- Includes standalone Python scripts (train_faces.py, recognize_attendance.py) for face training and recognition
- Uses Haar Cascade classifiers for face detection

### Authentication & Authorization
- Built on Django's authentication system with custom Profile extension
- Role-based access control implemented through Profile.role field with choices: admin, student, teacher, doctor
- View-level permissions enforced using decorators and role checks
- OneToOne relationship between User and Profile ensures single role per user

### Data Models & Relationships
**Core relationships:**
- User → Profile (OneToOne): Extends authentication with role and personal details
- User → Document (ForeignKey): Tracks document uploads
- User → ChatMessage (dual ForeignKey): Sender and receiver relationships
- User → HealthRecord (dual ForeignKey): Patient (student) and provider (doctor) relationships
- User → Appointment (dual ForeignKey): Student and doctor appointment scheduling
- User → FaceEncoding (OneToOne): Face recognition data per student
- User → Attendance (ForeignKey): Daily attendance records per student

### Real-time Communication Architecture
- ASGI application configured with ProtocolTypeRouter for HTTP and WebSocket protocols
- WebSocket routing uses AuthMiddlewareStack for authenticated connections
- Chat rooms use channel group names for message broadcasting
- ChatConsumer handles WebSocket lifecycle (connect, disconnect, receive)
- Messages persisted to database while simultaneously broadcast to active connections

### File Storage & Media Handling
- Django's FileField/ImageField for document and image uploads
- Media files organized in subdirectories: documents/, face_images/
- Static and media URL configuration in settings with DEBUG-conditional serving
- FileResponse used for controlled document downloads with authorization checks

### Face Recognition Pipeline
**Training Phase (train_faces.py):**
- Reads student images from student_images/ directory
- Uses OpenCV Haar Cascade for face detection
- Generates face encodings stored as binary data in FaceEncoding model
- Links encodings to student User objects

**Recognition Phase (recognize_attendance.py):**
- Loads face encodings from database
- Captures webcam feed for real-time face detection
- Compares detected faces against known encodings
- Automatically creates Attendance records with unique constraint on (student, date)

### Template Architecture
- Base template (base.html) provides consistent layout and navigation
- Role-aware navigation with conditional menu items
- Django template inheritance used across all apps
- Inline CSS styling for simplicity (no external CSS framework dependency)

### URL Routing Strategy
- Main urls.py delegates to app-specific URL configurations
- Namespace-free routing with unique view names
- Root path redirects to login view
- App prefixes: /library/, /chat/, /healthcare/, /attendance/

## External Dependencies

### Core Framework & Extensions
- **Django 5.2.7**: Primary web framework
- **Django Channels**: WebSocket support and async capabilities (version not specified)
- **Django REST Framework**: API functionality (installed but not actively used in current codebase)
- **Daphne**: ASGI server for handling HTTP and WebSocket protocols

### Computer Vision & Image Processing
- **OpenCV (cv2)**: Face detection using Haar Cascade classifiers and face recognition processing
- **NumPy**: Array operations for face encoding manipulation

### Database
- **SQLite**: Default database (development configuration)
- Database can be migrated to PostgreSQL or other Django-supported databases by updating settings.py

## Recent Changes

**October 2025 - Project Implementation**
- Created complete Django project with all 5 apps fully functional
- Implemented InMemoryChannelLayer for WebSocket chat (no Redis required for development)
- Integrated face recognition scripts with Django ORM (FaceEncoding model)
- Updated face encoding storage to use float32 dtype for accurate distance calculations
- All migrations run successfully, database initialized
- Server running on port 5000 with Daphne ASGI server
- README.md created with complete setup instructions

### Additional Notes
- No external authentication providers (OAuth, SAML) currently integrated
- No external API integrations or third-party services
- Channel layers use InMemoryChannelLayer for development (use Redis for production multi-server deployments)
- No email service configuration present
- File storage uses local filesystem (no cloud storage integration like S3)
- Face encodings stored in database as float32 binary format for reliable recognition