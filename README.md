# Hope Connect AI Project with Django REST Framework Backend.

1. Accounts App:
The Accounts app provides comprehensive authentication and user management for the Hope Connect AI Flutter application, featuring secure registration, login, profile management, push notifications, and social authentication.
Features
Email-based registration with OTP verification
JWT token authentication with access/refresh tokens
Secure password management with reset functionality
Token blacklisting for secure logout
Social authentication (Google & Apple Sign-In)
Custom user model with UUID primary keys
Profile management with personal information and photos
Phone number validation with international format support
Firebase Cloud Messaging integration
Weather alert preferences management
Test notification functionality
Admin Features
Custom branding: "Hope Connect AI Admin"
Clean interface with unnecessary models hidden
User management with filtering and search capabilities
OTP monitoring and tracking
List view with email, name, and status
Filter by staff and active status
Search by email and full name
Organized field groups for better usability
Models
CustomUser(AbstractBaseUser)
Primary Key: UUID
Authentication: Email-based
Fields: full_name, birth_date, profile_picture, phone_number, email, firebase_token, receive_weather_alerts
Permissions: is_staff, is_active, is_superuser
Timestamps: date_joined, last_login
OTP (One-Time Password)
Fields: email, otp (4-digit), created_at, is_used
Purpose: Email verification for registration and password reset
Expiration: 10 minutes
Usage: Single-use only
API Endpoints
Registration Flow
Request OTP for Registration
http
POST /accounts/signup/request-otp/
{
    "email": "user@example.com"
}
Verify Registration OTP
http
POST /accounts/signup/verify-otp/
{
    "email": "user@example.com",
    "otp": "1234"
}
Complete Registration with Password
http
POST /accounts/signup/set-password/
{
    "email": "user@example.com",
    "password": "securepassword123",
    "confirm_password": "securepassword123"
}
Authentication
Login
http
POST /accounts/login/
{
    "email": "user@example.com",
    "password": "securepassword123"
}

Response:
{
    "success": true,
    "message": "Login successful",
    "data": {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "user": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "full_name": "John Doe",
            "email": "user@example.com"
        }
    }
}
Logout
http
POST /accounts/logout/
Authorization: Bearer <access_token>
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
Password Reset Flow
Request Password Reset OTP
http
POST /accounts/forgot-password/request-otp/
{
    "email": "user@example.com"
}
Verify Password Reset OTP
http
POST /accounts/forgot-password/verify-otp/
{
    "email": "user@example.com",
    "otp": "5678"
}
Reset Password
http
POST /accounts/forgot-password/reset/
{
    "email": "user@example.com",
    "password": "newsecurepassword123",
    "confirm_password": "newsecurepassword123"
}
Profile Management
Get Profile
http
GET /accounts/profile/
Authorization: Bearer <access_token>

Response:
{
    "success": true,
    "message": "Profile retrieved successfully",
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "full_name": "John Doe",
        "birth_date": "1990-01-01",
        "profile_picture": "/media/profile_pictures/image.jpg",
        "phone_number": "+1234567890",
        "email": "user@example.com"
    }
}
Update Profile
http
PATCH /accounts/profile/
Authorization: Bearer <access_token>
{
    "full_name": "John Smith",
    "birth_date": "1990-01-01",
    "phone_number": "+1987654321"
}
Push Notifications
Register Firebase Token
http
POST /accounts/firebase-token/
Authorization: Bearer <access_token>
{
    "firebase_token": "dGhpcyBpcyBhIGZha2UgZmlyZWJhc2UgdG9rZW4..."
}
Send Test Notification
http
POST /accounts/test-notification/
Authorization: Bearer <access_token>
{
    "title": "Test Title",
    "body": "This is a test notification message"
}
Social Authentication
Google Sign-In
http
POST /accounts/google-signup/
{
    "id_token": "ya29.a0AWY7CkkeB8X9..."
}

Response:
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "user@gmail.com",
        "full_name": "John Doe"
    }
}
Apple Sign-In
http
POST /accounts/apple-signup/
{
    "id_token": "eyJraWQiOiJZdXlYb1kiLCJhbGciOiJSUzI1NiJ9..."

2. Alerts App:
The Alerts app manages weather alerts for the Hope Connect AI Flutter application. It fetches real-time weather alerts from the National Weather Service API, stores them in the database, and sends push notifications to users who have opted in for weather alerts.
Features
Weather alert ingestion from National Weather Service API
Real-time push notifications via Firebase Cloud Messaging
Alert storage with unique source ID tracking
Severity-based filtering (Minor, Moderate, Severe, Extreme)
Automatic alert fetching via Celery background tasks
Alert expiration and cleanup functionality
User preference management for weather alert subscriptions
Paginated API responses for mobile app integration
Geographic area filtering for Nevada (NV) alerts
Admin Features
Alert management with comprehensive list view
Filtering by severity and creation date
Search functionality by event type, headline, and area
Organized fieldsets with content and metadata sections
Read-only fields for ID and creation timestamp
Ordered by most recent alerts first
Models
Alert
Primary Key: UUID
Unique Tracking: source_id from NWS API
Fields:
source_id - Unique identifier from National Weather Service
event - Type of weather event (max 200 chars)
headline - Alert headline (max 500 chars)
description - Detailed alert description (text field)
severity - Alert level (Minor, Moderate, Severe, Extreme)
area - Geographic area description (max 500 chars)
created_at - Timestamp for sorting and expiration
Indexes: On source_id, severity, and created_at for performance
Ordering: Most recent alerts first
API Endpoints
Get All Alerts (Paginated)
http
GET /alerts/
Authorization: Bearer <access_token>

Query Parameters:
- page: Page number (default: 1)
- page_size: Items per page (default: 20, max: 100)
- severity: Filter by severity level (Minor, Moderate, Severe, Extreme)

Response:
{
    "count": 45,
    "total_pages": 3,
    "current_page": 1,
    "page_size": 20,
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "source_id": "urn:oid:2.49.0.1.840.0.abc123",
            "event": "Winter Storm Warning",
            "headline": "Winter Storm Warning issued for Sierra Nevada",
            "description": "Heavy snow expected with accumulations of 12-18 inches...",
            "severity": "Severe",
            "area": "Sierra Nevada Mountains including Lake Tahoe",
            "created_at": "2025-09-29T10:30:00Z"
        }
    ]
}
Get Specific Alert
http
GET /alerts/<alert_id>/
Authorization: Bearer <access_token>

Response:
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "source_id": "urn:oid:2.49.0.1.840.0.abc123",
    "event": "Flash Flood Watch",
    "headline": "Flash Flood Watch issued for Las Vegas Valley",
    "description": "Thunderstorms may produce heavy rainfall leading to flash flooding...",
    "severity": "Moderate",
    "area": "Las Vegas Valley including Henderson and North Las Vegas",
    "created_at": "2025-09-29T15:45:00Z"
}
Error Responses
http
# Invalid page parameter
{
    "error": "Page number must be greater than 0"
}

# Invalid severity filter
{
    "error": "Invalid severity. Valid options: Minor, Moderate, Severe, Extreme"
}

# Alert not found
{
    "error": "Alert not found"
}

# Invalid UUID format
{
    "error": "Invalid alert ID format"
}

3. Chatbot App:
The Chatbot app provides AI-powered conversational capabilities for the Hope Connect AI Flutter application. It integrates with OpenAI's API to process user queries, manages chat sessions, and utilizes CSV data for context-aware responses with location-based insights.
Features
AI-powered chat using OpenAI API integration
Context-aware responses using uploaded CSV data
Session management for authenticated and anonymous users
Location-based queries for personalized responses
Chat history with conversation persistence
Keyword extraction from user messages
Response time tracking for performance monitoring
CSV file management for knowledge base updates
Anonymous chat support using session keys
Multi-role messaging (user, assistant, system)
Admin Features
CSV file management with upload restrictions (single file policy)
File size display with automatic formatting (bytes, KB, MB)
User tracking for file uploads
Search functionality by name and description
Filtering by active status and upload date
Metadata sections with collapse functionality
Upload permissions restricted to prevent multiple files
Models
CSVFile
Primary Key: UUID
Fields: name, file, uploaded_at, uploaded_by, is_active, description
Purpose: Store knowledge base CSV files for contextual responses
Restrictions: Single active file policy
File Storage: uploaded to 'csv_files/' directory
ChatSession
Primary Key: UUID
Fields: user, session_key, title, created_at, updated_at, is_active
Purpose: Manage conversation sessions for users and anonymous visitors
Support: Both authenticated users and anonymous sessions
Auto-title: Generated from first user message
ChatMessage
Primary Key: UUID
Fields: session, role, content, location, keywords, timestamp, response_time, context_used
Roles: user, assistant, system
Tracking: Response time, keyword extraction, context usage
Location: Optional user location for contextual responses
API Endpoints
Chat Processing
http
POST /chatbot/chat/
Content-Type: application/json

{
    "message": "What's the weather like in Las Vegas?",
    "location": "Las Vegas, NV",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
}

Response:
{
    "success": true,
    "message": "Message processed successfully",
    "data": {
        "response": "Based on current weather conditions in Las Vegas...",
        "session_id": "550e8400-e29b-41d4-a716-446655440000",
        "keywords": ["weather", "Las Vegas"],
        "context_used": true,
        "response_time": 2.45
    }
}
Get Chat Sessions (Authenticated Users)
http
GET /chatbot/sessions/
Authorization: Bearer <access_token>

Response:
{
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "Weather inquiry in Las Vegas",
            "user_email": "user@example.com",
            "created_at": "2025-09-29T10:30:00Z",
            "updated_at": "2025-09-29T10:35:00Z",
            "is_active": true,
            "message_count": 4,
            "last_message": {
                "content": "Thank you for the weather update!",
                "role": "user",
                "timestamp": "2025-09-29T10:35:00Z"
            }
        }
    ]
}
Get Specific Chat Session
http
GET /chatbot/sessions/<session_id>/
Authorization: Bearer <access_token>

Response:
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Weather inquiry in Las Vegas",
    "user_email": "user@example.com",
    "created_at": "2025-09-29T10:30:00Z",
    "updated_at": "2025-09-29T10:35:00Z",
    "is_active": true,
    "message_count": 4,
    "messages": [
        {
            "id": "msg-uuid-1",
            "role": "user",
            "content": "What's the weather like in Las Vegas?",
            "location": "Las Vegas, NV",
            "keywords": ["weather", "Las Vegas"],
            "timestamp": "2025-09-29T10:30:00Z",
            "context_used": true,
            "response_time": null
        },
        {
            "id": "msg-uuid-2",
            "role": "assistant",
            "content": "Based on current conditions in Las Vegas...",
            "location": null,
            "keywords": ["weather", "Las Vegas"],
            "timestamp": "2025-09-29T10:30:15Z",
            "context_used": true,
            "response_time": 2.45
        }
    ]
}
Delete Chat Session
http
DELETE /chatbot/sessions/<session_id>/delete/
Authorization: Bearer <access_token>

Response:
{
    "success": true,
    "message": "Chat session deleted successfully"
}
Error Responses
http
# Invalid message
{
    "success": false,
    "message": {
        "message": ["Message cannot be empty."]
    }
}

# Processing error
{
    "success": false,
    "message": "Error processing message: OpenAI API error"
}

# Session not found
{
    "detail": "Not found."
}

