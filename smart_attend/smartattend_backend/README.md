# SmartAttend Backend

This is the Django backend for the SmartAttend attendance monitoring system.

## Features

- User authentication (Admin, Teacher, Student)
- Class management
- Attendance tracking with multiple methods (manual, QR code, facial recognition)
- Geolocation verification
- Facial recognition integration
- RESTful API

## Technologies Used

- Django 5.2
- Django REST Framework
- PostgreSQL (production) / SQLite (development)
- Docker & Docker Compose
- Python-Decouple for environment management

## Setup Instructions

### Development Setup

1. Clone the repository
2. Navigate to the backend directory:
   ```
   cd smartattend_backend
   ```
3. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Run migrations:
   ```
   python manage.py migrate
   ```
6. Create a superuser:
   ```
   python manage.py createsuperuser
   ```
7. Start the development server:
   ```
   python manage.py runserver
   ```

### Docker Setup

1. Make sure Docker is installed
2. Run with Docker Compose:
   ```
   docker-compose up --build
   ```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register a new user
- `POST /api/auth/login/` - Login user
- `POST /api/auth/logout/` - Logout user
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/update/` - Update user profile

### User Management (Admin only)
- `GET /api/users/students/` - Get all students
- `GET /api/users/teachers/` - Get all teachers

### Class Management
- `GET /api/classes/` - Get classes (based on user role)
- `POST /api/classes/create/` - Create a new class (Admin only)
- `GET /api/classes/<id>/` - Get class details
- `PUT /api/classes/<id>/update/` - Update class (Admin only)
- `DELETE /api/classes/<id>/delete/` - Delete class (Admin only)
- `POST /api/classes/<id>/enroll/` - Enroll students (Admin only)
- `GET /api/classes/teacher/<id>/` - Get classes for a teacher
- `GET /api/classes/student/<id>/` - Get classes for a student

### Attendance Management
- `GET /api/attendance/sessions/` - Get attendance sessions
- `POST /api/attendance/sessions/create/` - Create attendance session (Teacher only)
- `GET /api/attendance/sessions/<id>/` - Get session details
- `POST /api/attendance/sessions/<id>/mark/` - Mark attendance
- `POST /api/attendance/sessions/<id>/qr/generate/` - Generate QR code (Teacher only)
- `POST /api/attendance/qr/scan/` - Scan QR code (Student only)
- `GET /api/attendance/classes/<id>/summary/` - Get class attendance summary
- `GET /api/attendance/student/<id>/` - Get student attendance
- `GET /api/attendance/student/` - Get current user's attendance

### Core Features
- `POST /api/location/verify/` - Verify student location
- `POST /api/facial/save/` - Save facial data
- `POST /api/facial/verify/` - Verify facial data
- `GET /api/notifications/` - Get user notifications
- `POST /api/notifications/<id>/read/` - Mark notification as read
- `GET /api/analytics/class/<id>/` - Get class analytics
- `POST /api/analytics/class/<id>/update/` - Update class analytics

## Environment Variables

Create a `.env` file with the following variables:

```
DEBUG=True
SECRET_KEY=your-secret-key
DB_NAME=smartattend_db
DB_USER=smartattend_user
DB_PASSWORD=smartattend_password
DB_HOST=localhost
DB_PORT=5432
```

## Database Schema

The application uses the following models:

1. **User** - Custom user model with roles (admin, teacher, student)
2. **Class** - Represents a course with schedule and location
3. **ClassSchedule** - Weekly schedule for classes
4. **AttendanceSession** - Attendance session for a class on a specific date
5. **AttendanceRecord** - Individual student attendance record
6. **QRCode** - QR codes for attendance marking
7. **LocationVerification** - Geolocation verification records
8. **FacialRecognitionData** - Facial encoding data for students
9. **AttendanceAnalytics** - Class attendance analytics
10. **Notification** - User notifications

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

This project is licensed under the MIT License.