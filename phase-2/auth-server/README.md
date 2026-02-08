# Better Auth Server

**Authentication microservice for Phase II Todo Application**

This is a standalone Node.js/TypeScript server that handles all authentication concerns using [Better Auth](https://better-auth.com). It works in tandem with the FastAPI backend, providing a clean separation of concerns:

- **Better Auth Server**: User authentication (signup, login, logout, sessions)
- **FastAPI Backend**: Business logic (task CRUD operations)
- **Shared**: Same PostgreSQL database, compatible JWT tokens

---

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and update values:

```bash
cp .env.example .env
```

**Critical**: Ensure `BETTER_AUTH_SECRET` matches `JWT_SECRET` in backend `.env`!

### 3. Run Database Migration

```bash
npm run migrate
```

This creates Better Auth tables: `user`, `session`, `account`, `verification`

### 4. Start Development Server

```bash
npm run dev
```

Server runs on `http://localhost:3001`

---

## API Endpoints

### Health Check
```http
GET /health
```

Returns server status and version.

### Sign Up (Create Account)
```http
POST /auth/sign-up
Content-Type: application/json

{
  "name": "Alice Smith",
  "email": "alice@example.com",
  "password": "SecurePass123!"
}
```

**Response**: User object + sets `auth_token` cookie

### Sign In (Login)
```http
POST /auth/sign-in/email
Content-Type: application/json

{
  "email": "alice@example.com",
  "password": "SecurePass123!"
}
```

**Response**: User object + sets `auth_token` cookie

### Sign Out (Logout)
```http
POST /auth/sign-out
Cookie: auth_token=<token>
```

**Response**: Success message + clears `auth_token` cookie

### Get Session (Current User)
```http
GET /auth/get-session
Cookie: auth_token=<token>
```

**Response**: User object if authenticated, null otherwise

---

## Architecture

### Integration with FastAPI

```
Frontend (Next.js)
    │
    ├─► Better Auth Server (Port 3001)
    │   • POST /auth/sign-up
    │   • POST /auth/sign-in/email
    │   • POST /auth/sign-out
    │   • GET /auth/get-session
    │   └─► Creates JWT token in cookie
    │
    └─► FastAPI Backend (Port 8000)
        • GET /api/tasks
        • POST /api/tasks
        • PUT /api/tasks/{id}
        • DELETE /api/tasks/{id}
        └─► Validates JWT token from cookie
```

### Database Schema

**Better Auth Tables**:
- `user`: User accounts (id, name, email, emailVerified, createdAt, updatedAt, hashed_password)
- `session`: Active sessions (id, token, userId, expiresAt, ipAddress, userAgent)
- `account`: OAuth provider accounts (for future social auth)
- `verification`: Email verification tokens (for future email verification)

**FastAPI Tables**:
- `tasks`: Todo tasks (id, title, description, is_complete, user_id, created_at, updated_at)

**Foreign Keys**:
- `tasks.user_id` → `user.id`
- `session.userId` → `user.id`
- `account.userId` → `user.id`

---

## Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Neon PostgreSQL connection string | `postgresql://user:pass@host/db?sslmode=require` |
| `BETTER_AUTH_SECRET` | JWT signing secret (must match backend) | `your-256-bit-secret-key` |
| `BETTER_AUTH_URL` | Server base URL | `http://localhost:3001` |
| `CORS_ORIGINS` | Allowed frontend origins (comma-separated) | `http://localhost:3000,http://127.0.0.1:3000` |
| `PORT` | Server port | `3001` |
| `NODE_ENV` | Environment | `development` or `production` |

### JWT Token Structure

Better Auth generates JWT tokens with this payload:

```json
{
  "userId": "550e8400-e29b-41d4-a716-446655440000",
  "email": "alice@example.com",
  "sessionId": "abc123...",
  "exp": 1702345678,
  "iat": 1702344778
}
```

FastAPI validates these tokens using the same secret (`BETTER_AUTH_SECRET` == `JWT_SECRET`).

---

## Development

### Run Development Server with Auto-Reload

```bash
npm run dev
```

Uses `tsx watch` for hot reloading on file changes.

### Build for Production

```bash
npm run build
```

Compiles TypeScript to `dist/` directory.

### Start Production Server

```bash
npm start
```

Runs compiled JavaScript from `dist/`.

### Run Migration

```bash
npm run migrate
```

Creates/updates database tables. Safe to run multiple times (idempotent).

---

## Testing

### Test with cURL

**Sign Up**:
```bash
curl -X POST http://localhost:3001/auth/sign-up \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"password123"}' \
  -c cookies.txt
```

**Sign In**:
```bash
curl -X POST http://localhost:3001/auth/sign-in/email \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' \
  -c cookies.txt
```

**Get Session**:
```bash
curl http://localhost:3001/auth/get-session \
  -b cookies.txt
```

**Sign Out**:
```bash
curl -X POST http://localhost:3001/auth/sign-out \
  -b cookies.txt
```

---

## Security Features

### Password Security
- Minimum 8 characters (configurable in `src/auth.ts`)
- Bcrypt hashing (handled by Better Auth)
- Never stored in plaintext

### Session Security
- JWT tokens with 15-minute expiration
- HttpOnly cookies (prevent XSS)
- SameSite=lax (prevent CSRF)
- Secure flag in production (HTTPS only)

### Rate Limiting
- 10 requests per minute per IP
- Prevents brute-force attacks

### CORS Protection
- Only allowed origins can make requests
- Credentials (cookies) require explicit origin whitelist

---

## Deployment

### Railway / Render / Fly.io

1. **Set Environment Variables** in dashboard:
   - `DATABASE_URL`
   - `BETTER_AUTH_SECRET` (same as backend)
   - `BETTER_AUTH_URL` (your deployed URL)
   - `CORS_ORIGINS` (your frontend URL)
   - `NODE_ENV=production`

2. **Build Command**:
   ```bash
   npm install && npm run build
   ```

3. **Start Command**:
   ```bash
   npm start
   ```

4. **Port**: Auto-detected from `PORT` env var

### Docker

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --production

COPY . .
RUN npm run build

EXPOSE 3001

CMD ["npm", "start"]
```

---

## Troubleshooting

### Database Connection Failed
- Verify `DATABASE_URL` is correct
- Check Neon dashboard for connection string
- Ensure SSL is enabled: `?sslmode=require`

### JWT Token Validation Fails
- Ensure `BETTER_AUTH_SECRET` == `JWT_SECRET` (backend)
- Check token hasn't expired (15 minute default)
- Verify cookie is being sent (credentials: 'include')

### CORS Errors
- Add frontend origin to `CORS_ORIGINS`
- Ensure `credentials: true` in frontend fetch options
- Check browser console for specific CORS error

### Migration Errors
- Ensure database connection works first
- Check for existing tables with different schemas
- Review migration logs for specific SQL errors

---

## Future Enhancements

- [ ] Email verification (SMTP configuration)
- [ ] Password reset via email
- [ ] OAuth providers (Google, GitHub)
- [ ] Two-factor authentication (2FA)
- [ ] Passkey authentication
- [ ] Admin panel for user management
- [ ] Session management dashboard
- [ ] Audit logs for security events

---

## Resources

- **Better Auth Docs**: https://better-auth.com/docs
- **Better Auth GitHub**: https://github.com/better-auth/better-auth
- **Integration Plan**: See `../BETTER_AUTH_INTEGRATION_PLAN.md`

---

## Support

For issues related to:
- **Better Auth**: See [Better Auth GitHub Issues](https://github.com/better-auth/better-auth/issues)
- **Integration**: See `../BETTER_AUTH_INTEGRATION_PLAN.md`
- **FastAPI Backend**: See `../backend/CLAUDE.md`
- **Frontend**: See `../frontend/CLAUDE.md`
