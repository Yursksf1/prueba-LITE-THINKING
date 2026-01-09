# Authentication and Authorization Implementation

## Overview

This document describes the authentication and authorization system implemented for the LITE THINKING project, following Clean Architecture principles.

## Architecture

The system follows a layered architecture:

```
API Layer (api/)
    ↓
Application Layer (application/)
    ↓
Infrastructure Layer (infrastructure/)
```

### Key Principles

1. **Domain Independence**: The domain layer (`domain/`) has NO knowledge of authentication
2. **Clean Separation**: Authentication logic is in infrastructure, not in business rules
3. **Native Django**: Uses Django's built-in authentication mechanisms with JWT tokens

## User Model

Location: `backend/infrastructure/models/user.py`

### Roles

The system supports two user roles:

- **ADMINISTRATOR**: Full access to all endpoints (create, read, update, delete)
- **EXTERNAL**: Read-only access to view companies and products

### User Fields

```python
- email (unique, used for login)
- first_name
- last_name
- role (ADMINISTRATOR or EXTERNAL)
- is_active
- is_staff
- date_joined
```

### Password Security

- Passwords are encrypted using Django's built-in password hashing (PBKDF2 with SHA256)
- Never stored in plain text
- Validated using Django's password validators

## Authentication Endpoints

All authentication endpoints are under `/api/auth/`:

### 1. Login

**POST** `/api/auth/login/`

Authenticates a user and returns JWT tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "ADMINISTRATOR",
    "date_joined": "2026-01-08T23:00:00Z"
  }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Invalid credentials"
}
```

### 2. Refresh Token

**POST** `/api/auth/refresh/`

Obtains a new access token using a refresh token.

**Request Body:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 3. Current User Info

**GET** `/api/auth/me/`

Returns information about the currently authenticated user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "ADMINISTRATOR",
  "date_joined": "2026-01-08T23:00:00Z"
}
```

## Authorization (Permissions)

Location: `backend/api/permissions.py`

### Permission Classes

#### 1. IsAdministrator

Allows access only to users with the ADMINISTRATOR role.

```python
@api_view(['POST'])
@permission_classes([IsAdministrator])
def admin_only_endpoint(request):
    # Only administrators can access this
    pass
```

#### 2. IsAdministratorOrReadOnly

Allows:
- **Read access (GET, HEAD, OPTIONS)**: All authenticated users
- **Write access (POST, PUT, PATCH, DELETE)**: Only administrators

```python
@api_view(['GET', 'POST'])
@permission_classes([IsAdministratorOrReadOnly])
def company_list_view(request):
    # GET: All authenticated users
    # POST: Only administrators
    pass
```

## Example: Protected Endpoints

### Companies Endpoints

**GET** `/api/companies/` - List companies (All authenticated users)
**POST** `/api/companies/` - Create company (Administrators only)
**GET** `/api/companies/{nit}/` - View company (All authenticated users)
**PUT** `/api/companies/{nit}/` - Update company (Administrators only)
**DELETE** `/api/companies/{nit}/` - Delete company (Administrators only)

### Example Usage

```bash
# 1. Login as administrator
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}'

# Response includes access token

# 2. Use token to create a company (Administrator only)
curl -X POST http://localhost:8000/api/companies/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"nit": "123456789", "name": "My Company", "address": "123 Street", "phone": "+123456789"}'

# 3. View companies (Any authenticated user)
curl -X GET http://localhost:8000/api/companies/ \
  -H "Authorization: Bearer <access_token>"
```

## JWT Configuration

Location: `backend/config/settings.py`

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=5),  # Access token valid for 5 hours
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),  # Refresh token valid for 1 day
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

## Security Considerations

1. **Password Encryption**: All passwords are hashed using Django's password hashers
2. **JWT Tokens**: Tokens are signed with SECRET_KEY and expire automatically
3. **HTTPS**: In production, always use HTTPS to protect tokens in transit
4. **Secret Key**: Never commit SECRET_KEY to version control
5. **Token Storage**: Store tokens securely on the client side (e.g., httpOnly cookies or secure storage)

## Testing

### Create Test Users

Run the following command to create test users:

```bash
python3 /tmp/create_test_users.py
```

This creates:
- Administrator: `admin@example.com` / `admin123`
- External User: `external@example.com` / `external123`

### Manual Testing

```bash
# Start the server
python manage.py runserver

# Test administrator login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}'

# Test external user login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "external@example.com", "password": "external123"}'
```

## Database Migrations

The User model is managed through Django migrations:

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

Migration file: `backend/infrastructure/migrations/0001_initial.py`

## Admin Interface

Users can be managed through Django Admin:

```bash
# Create a superuser
python manage.py createsuperuser

# Access admin at: http://localhost:8000/admin/
```

The admin interface is registered in `backend/infrastructure/admin.py` and allows:
- Creating/editing users
- Assigning roles
- Managing permissions
- Viewing user activity

## Integration with Business Logic

When implementing business logic (use cases), you can access the authenticated user:

```python
# In a view
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def some_business_operation(request):
    # Get the authenticated user
    user = request.user
    
    # Check role if needed
    if user.is_administrator:
        # Administrator-specific logic
        pass
    
    # Call application layer / use case
    # The use case doesn't need to know about authentication
    result = some_use_case.execute(data=request.data)
    
    return Response(result)
```

## Troubleshooting

### "Authentication credentials were not provided"

Make sure you're including the Authorization header:
```
Authorization: Bearer <your_access_token>
```

### "Invalid credentials"

Check that:
- Email and password are correct
- User account is active (`is_active=True`)

### "You do not have permission to perform this action"

Check that:
- User has the correct role for the endpoint
- Token is valid and not expired

## Next Steps

1. Implement password reset functionality
2. Add email verification for new users
3. Implement session management (logout, token blacklist)
4. Add audit logging for authentication events
5. Integrate with frontend authentication flow
