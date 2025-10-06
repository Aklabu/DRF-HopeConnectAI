# Hope Connect AI

A comprehensive Django REST Framework backend for a Flutter mobile application that provides weather alerts, AI-powered chatbot assistance, and user management with push notifications for Nevada State of USA.

## Overview

Hope Connect AI is a robust backend system designed to serve a Flutter mobile application with real-time weather alerts, intelligent conversational AI, and comprehensive user authentication. The system integrates with the National Weather Service API, OpenAI, and Firebase Cloud Messaging to deliver a complete solution for weather-aware communication.

## Key Features

### 🔐 Authentication & User Management
- Email-based registration with OTP verification
- JWT token authentication (access & refresh tokens)
- Social authentication (Google & Apple Sign-In)
- Password reset with OTP verification
- User profile management with photo uploads
- Phone number validation with international format support

### 🌦️ Weather Alerts System
- Real-time weather alert ingestion from National Weather Service API
- Automated alert fetching via Celery background tasks
- Push notifications via Firebase Cloud Messaging
- Severity-based filtering (Minor, Moderate, Severe, Extreme)
- Geographic filtering for Nevada (NV) alerts
- Alert expiration and cleanup functionality
- User preference management for alert subscriptions

### 🤖 AI-Powered Chatbot
- OpenAI API integration for intelligent conversations
- Context-aware responses using CSV knowledge base
- Location-based query processing
- Session management for authenticated and anonymous users
- Chat history persistence
- Keyword extraction and response time tracking
- Multi-role messaging support (user, assistant, system)

## Technology Stack

### Backend Framework
- **Django 5.2.6** - Web framework
- **Django REST Framework** - API development
- **djangorestframework-simplejwt** - JWT authentication

### Database
- **SQLite** (Development) - Can be replaced with PostgreSQL/MySQL for production

### Task Queue
- **Celery** - Asynchronous task processing
- **Redis** - Message broker and cache backend

### External Services
- **Firebase Cloud Messaging** - Push notifications
- **OpenAI API** - AI chatbot capabilities
- **National Weather Service API** - Weather alerts data
- **Google OAuth 2.0** - Social authentication
- **Apple Sign In** - Social authentication

### Additional Libraries
- **drf-spectacular** - API documentation
- **python-decouple** - Environment configuration
- **pandas** - CSV data processing
- **firebase-admin** - Firebase integration

## Project Structure

```
hope-connect-ai/
├── accounts/           # User authentication and management
├── alerts/            # Weather alerts system
├── chatbot/           # AI chatbot functionality
├── config/            # Project settings and configuration
├── utils/             # Shared utilities and helpers
├── media/             # User uploaded files
├── logs/              # Application logs
└── manage.py          # Django management script
```

## Installation

### Prerequisites
- Python 3.10+
- Redis Server
- OpenAI API Key
- Firebase Project with Cloud Messaging enabled
- Email service credentials (SMTP)

### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/hope-connect-ai.git
cd hope-connect-ai
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment Configuration**

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key
DEBUG=True

# Database (Optional - defaults to SQLite)
# DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Firebase Configuration
FIREBASE_API_KEY=your-firebase-api-key
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CREDENTIALS_PATH=/path/to/firebase-service-account.json
FCM_SERVER_KEY=your-fcm-server-key

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Redis Configuration
REDIS_URL=redis://127.0.0.1:6379/1

# Weather Alerts Configuration
WEATHER_ALERTS_ENABLED=True
WEATHER_API_TIMEOUT=30
MAX_ALERTS_PER_BATCH=100
ALERT_RETENTION_DAYS=7

# FCM Configuration
FCM_BATCH_SIZE=500
FCM_ENABLED=True

# Optional Settings
REQUIRE_FIREBASE=False  # Set to True in production if Firebase is mandatory
```

5. **Firebase Setup**

Place your Firebase service account JSON file in one of these locations:
- Project root: `firebase-service-account.json`
- Config directory: `config/firebase-service-account.json`
- Credentials directory: `credentials/firebase-service-account.json`
- Or set custom path in `FIREBASE_CREDENTIALS_PATH` environment variable

6. **Database Setup**
```bash
python manage.py makemigrations
python manage.py migrate
```

7. **Create Superuser**
```bash
python manage.py createsuperuser
```

8. **Start Redis Server**
```bash
redis-server
```

9. **Start Celery Worker** (in a new terminal)
```bash
celery -A config worker -l info
```

10. **Start Celery Beat** (in a new terminal)
```bash
celery -A config beat -l info
```

11. **Run Development Server**
```bash
python manage.py runserver
```

## API Documentation

### Base URL
```
http://localhost:8000/api/
```

### API Schema
Access interactive API documentation:
- **Swagger UI**: `http://localhost:8000/api/schema/swagger-ui/`
- **ReDoc**: `http://localhost:8000/api/schema/redoc/`
- **OpenAPI Schema**: `http://localhost:8000/api/schema/`

### Main Endpoints

#### Accounts App
- `POST /accounts/signup/request-otp/` - Request registration OTP
- `POST /accounts/signup/verify-otp/` - Verify OTP
- `POST /accounts/signup/set-password/` - Complete registration
- `POST /accounts/login/` - User login
- `POST /accounts/logout/` - User logout
- `GET /accounts/profile/` - Get user profile
- `PATCH /accounts/profile/` - Update profile
- `POST /accounts/firebase-token/` - Register Firebase token
- `POST /accounts/google-signup/` - Google Sign-In
- `POST /accounts/apple-signup/` - Apple Sign-In

#### Alerts App
- `GET /alerts/` - List weather alerts (paginated)
- `GET /alerts/<alert_id>/` - Get specific alert

#### Chatbot App
- `POST /chatbot/chat/` - Send chat message
- `GET /chatbot/sessions/` - List chat sessions
- `GET /chatbot/sessions/<session_id>/` - Get session details
- `DELETE /chatbot/sessions/<session_id>/delete/` - Delete session

## Background Tasks

### Celery Beat Schedule

**Weather Alerts Fetching**
- Runs every 30 minutes
- Fetches latest alerts from National Weather Service API
- Automatically sends push notifications to subscribed users

**Alert Expiration Cleanup**
- Runs daily at 2:00 AM
- Removes alerts older than 7 days (configurable)

## Admin Panel

Access the admin panel at: `http://localhost:8000/admin/`

### Admin Features
- Custom branding: "Hope Connect AI Admin"
- User management with filtering and search
- Weather alert monitoring
- OTP tracking
- CSV file management for chatbot knowledge base
- Chat session and message viewing

## Security Features

- UUID primary keys for enhanced security
- JWT token authentication with blacklisting
- OTP-based email verification (10-minute expiration)
- Password hashing with Django's built-in system
- CSRF protection
- Secure session management
- Rate limiting support via Redis
- Token-based Firebase authentication

## Configuration

### Production Considerations

1. **Database**: Switch to PostgreSQL or MySQL
2. **Static Files**: Configure AWS S3 or similar for media storage
3. **Environment Variables**: Use proper secret management
4. **HTTPS**: Enable SSL certificates
5. **Security Headers**: Uncomment security settings in `settings.py`
6. **Debug Mode**: Set `DEBUG=False`
7. **Allowed Hosts**: Configure proper domain names
8. **Celery**: Use production-ready message broker
9. **Logging**: Configure centralized logging service

### Environment Variables Reference

See `.env` example above for required configuration variables.

## Testing

Run tests with:
```bash
python manage.py test
```

## Logging

Logs are stored in the `logs/` directory:
- `django.log` - General Django logs
- `alerts.log` - Weather alerts system logs
- `firebase.log` - Firebase and push notification logs

## Monitoring

The system includes response time tracking and performance monitoring:
- Chat response times
- Alert processing metrics
- Firebase notification success rates
- Context usage statistics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Support

For issues and questions:
- Create an issue on GitHub
- Contact: support@hopeconnectai.com

## Acknowledgments

- National Weather Service for weather alerts API
- OpenAI for conversational AI capabilities
- Firebase for push notification infrastructure
- Django and Django REST Framework communities
