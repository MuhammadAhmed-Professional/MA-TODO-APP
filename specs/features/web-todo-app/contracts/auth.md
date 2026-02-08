# Authentication API Contract

**Feature**: 004-phase-2-web-app
**Base URL**: `/api/auth`
**Authentication**: Public endpoints (signup, login, logout)

## Overview

Authentication API provides user account creation, login, and logout functionality using JWT tokens stored in HttpOnly cookies.

---

## Endpoints

### 1. User Signup

**Endpoint**: `POST /api/auth/signup`
**Authentication**: None (public)
**Description**: Create a new user account

#### Request

**Headers**:
```
Content-Type: application/json
```

**Body**:
```json
{
  "name": "Alice Smith",
  "email": "alice@example.com",
  "password": "SecurePass123"
}
```

**Schema**:
```typescript
interface SignupRequest {
  name: string;          // 1-100 characters
  email: string;         // Valid email format
  password: string;      // Min 8 characters
}
```

**Validation Rules**:
- `name`: Required, 1-100 characters
- `email`: Required, valid email format (RFC 5322), unique (not already registered)
- `password`: Required, 8-100 characters, must contain at least one letter and one number

#### Response

**Success (201 Created)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "alice@example.com",
  "name": "Alice Smith",
  "created_at": "2025-12-06T10:30:00Z"
}
```

**Cookies Set**:
```
Set-Cookie: auth_token=<JWT>; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=900
Set-Cookie: refresh_token=<Refresh_JWT>; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=604800
```

**Errors**:
- `400 Bad Request`: Validation errors
  ```json
  {
    "detail": "Email already registered"
  }
  ```
- `422 Unprocessable Entity`: Invalid request format
  ```json
  {
    "detail": [
      {
        "loc": ["body", "email"],
        "msg": "value is not a valid email address",
        "type": "value_error.email"
      }
    ]
  }
  ```

---

### 2. User Login

**Endpoint**: `POST /api/auth/login`
**Authentication**: None (public)
**Description**: Authenticate user and issue JWT tokens

#### Request

**Headers**:
```
Content-Type: application/json
```

**Body**:
```json
{
  "email": "alice@example.com",
  "password": "SecurePass123"
}
```

**Schema**:
```typescript
interface LoginRequest {
  email: string;         // Valid email format
  password: string;      // User's password
}
```

#### Response

**Success (200 OK)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "alice@example.com",
  "name": "Alice Smith",
  "created_at": "2025-12-06T10:30:00Z"
}
```

**Cookies Set**:
```
Set-Cookie: auth_token=<JWT>; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=900
Set-Cookie: refresh_token=<Refresh_JWT>; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=604800
```

**Errors**:
- `401 Unauthorized`: Invalid credentials
  ```json
  {
    "detail": "Invalid credentials"
  }
  ```
  **Note**: Do not reveal whether email or password was incorrect (security best practice)

- `429 Too Many Requests`: Rate limit exceeded (5 attempts/minute)
  ```json
  {
    "detail": "Too many login attempts. Please try again later."
  }
  ```

---

### 3. User Logout

**Endpoint**: `POST /api/auth/logout`
**Authentication**: Required (valid JWT in cookie)
**Description**: Terminate user session by clearing authentication cookies

#### Request

**Headers**:
```
Cookie: auth_token=<JWT>; refresh_token=<Refresh_JWT>
```

**Body**: None (empty)

#### Response

**Success (204 No Content)**:
- Empty body
- Cookies cleared:
  ```
  Set-Cookie: auth_token=; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=0
  Set-Cookie: refresh_token=; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=0
  ```

**Errors**:
- `401 Unauthorized`: Missing or invalid token
  ```json
  {
    "detail": "Not authenticated"
  }
  ```

---

## JWT Token Structure

### Access Token (auth_token)

**Claims**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "alice@example.com",
  "exp": 1733486100,   // Expiration (15 minutes from issue)
  "iat": 1733485200    // Issued at timestamp
}
```

**Expiration**: 15 minutes
**Algorithm**: HS256 (HMAC with SHA-256)
**Secret**: Server-side environment variable (256-bit random string)

### Refresh Token (refresh_token)

**Claims**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "refresh",
  "exp": 1734089300,   // Expiration (7 days from issue)
  "iat": 1733485200    // Issued at timestamp
}
```

**Expiration**: 7 days
**Algorithm**: HS256
**Purpose**: Obtain new access token without re-entering credentials

---

## Security Headers

All responses include:
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Content-Security-Policy: default-src 'self'
```

---

## Rate Limiting

- **Signup**: 3 requests per minute per IP
- **Login**: 5 requests per minute per IP
- **Logout**: 10 requests per minute per user

**Rate Limit Headers** (included in all responses):
```
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 4
X-RateLimit-Reset: 1733485260
```

---

## Error Response Format

All errors follow consistent structure:

```typescript
interface ErrorResponse {
  detail: string | ValidationError[];
}

interface ValidationError {
  loc: string[];         // Location of error (e.g., ["body", "email"])
  msg: string;           // Human-readable message
  type: string;          // Error type (e.g., "value_error.email")
}
```

---

## Frontend Integration Example

```typescript
// Signup
const signup = async (name: string, email: string, password: string) => {
  const response = await fetch("/api/auth/signup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, password }),
    credentials: "include",  // Include cookies
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  return await response.json();
};

// Login
const login = async (email: string, password: string) => {
  const response = await fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
    credentials: "include",
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  return await response.json();
};

// Logout
const logout = async () => {
  const response = await fetch("/api/auth/logout", {
    method: "POST",
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error("Logout failed");
  }
};
```
