# SmartAttend - Intelligent Attendance Management System

SmartAttend is a comprehensive attendance management system built with Flutter (frontend) and Django (backend) that provides automated attendance tracking through multiple methods including QR codes, facial recognition, and geolocation verification.

## Features

### User Roles
- **Admin**: Manage classes, teachers, and students
- **Teacher**: Create attendance sessions, generate QR codes, view attendance records
- **Student**: Mark attendance via QR scanning, view personal attendance records

### Core Functionalities
- **Multi-method Attendance**: Manual entry, QR code scanning, facial recognition
- **Geolocation Verification**: Location-based attendance validation
- **Class Management**: Schedule classes with room assignments and timing
- **Attendance Analytics**: Detailed reports and statistics
- **Real-time Notifications**: Attendance updates and reminders

## Tech Stack

### Frontend (Flutter)
- Flutter 3.10+
- Provider for state management
- HTTP client for API communication
- QR code generation and scanning
- Geolocation services

### Backend (Django)
- Django 5.2
- Django REST Framework
- PostgreSQL database
- Token-based authentication
- Docker containerization

## Project Structure

```
smart_attend/
├── lib/
│   ├── models/          # Data models
│   ├── views/           # UI screens
│   ├── services/        # API services
│   ├── controllers/     # Business logic
│   ├── utils/           # Utilities and constants
│   └── main.dart        # Entry point
├── smartattend_backend/
│   ├── accounts/        # User management
│   ├── classes/         # Class management
│   ├── attendance/      # Attendance tracking
│   ├── core/            # Core features
│   ├── smartattend/     # Main Django app
│   ├── requirements.txt # Python dependencies
│   ├── Dockerfile       # Container configuration
│   └── manage.py        # Django CLI
└── DEPLOYMENT_GUIDE.md  # Deployment instructions
```

## Getting Started

### Prerequisites
- Flutter SDK 3.10+
- Python 3.11+
- PostgreSQL (optional, SQLite for development)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-github-username/smartattend.git
   cd smartattend
   ```

2. **Backend Setup**:
   ```bash
   cd smartattend_backend
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

3. **Frontend Setup**:
   ```bash
   cd ../smart_attend
   flutter pub get
   flutter run
   ```

## API Documentation

The backend provides a comprehensive RESTful API with endpoints for:
- User authentication and management
- Class creation and enrollment
- Attendance tracking and reporting
- Geolocation verification
- QR code generation and scanning

## Deployment

See `DEPLOYMENT_GUIDE.md` for detailed deployment instructions including:
- Docker deployment
- Production server setup
- SSL configuration
- Scaling considerations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built for educational purposes
- Inspired by modern attendance tracking needs
- Designed with scalability and security in mind