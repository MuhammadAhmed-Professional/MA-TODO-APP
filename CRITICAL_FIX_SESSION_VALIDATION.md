# CRITICAL: Session Validation Architecture Fix

**Date**: December 28, 2025
**Status**: Solution Identified
**Issue**: Session validation fails because of token format mismatch

---

## Problem Analysis

### What's Happening

1. **Auth Server Sets Full Cookie**:
   ```
   Set-Cookie: __Secure-better-auth.session_token=TOKEN.SIGNATURE; HttpOnly; Secure; SameSite=Lax
   ```
   - Cookie name: `__Secure-better-auth.session_token`
   - Cookie value: `TOKEN.SIGNATURE` (URL-encoded, includes signature)

2. **Auth Server Returns Incomplete Token in JSON**:
   ```json
   {
     "token": "TOKEN",  ← Missing .SIGNATURE part!
     "user": {...}
   }
   ```

3. **Frontend Extracts Incomplete Token**:
   - Frontend can't read HttpOnly cookies
   - Extracts `token` from JSON response
   - Stores incomplete token (without signature)
   - Sends incomplete token in Authorization header

4. **Backend Tries to Validate with Auth Server**:
   - Receives incomplete token from frontend
   - Calls auth server with `Cookie: better-auth.session_token=TOKEN`
   - Auth server returns `null` because token is incomplete/invalid

---

## Root Cause

**Cross-Domain Architecture** + **Better Auth Cookie-Based Sessions** = INCOMPATIBLE

- Better Auth designed for same-domain (frontend + backend on same origin)
- Cookies work seamlessly in same-domain
- Cross-domain (Vercel frontend + Railway backend) breaks cookie-based auth
- SameSite restrictions block cross-origin cookies

---

## Solution

**Query Database Directly for Session Validation**

Instead of calling the auth server, look up the session in the Better Auth database tables:

```python
# backend/src/auth/dependencies.py

from sqlmodel import Session, select
from src.models.user import User

# Better Auth stores sessions in the `session` table
# with `id` matching the token from the JSON response

async def get_current_user(
    request: Request,
    db_session: Session = Depends(get_session),
) -> User:
    # Extract token from Authorization header
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]

    if not token:
        raise HTTPException(401, "Not authenticated")

    # Query Better Auth's session table directly
    from sqlmodel import select
    query = select(BetterAuthSession).where(BetterAuthSession.id == token)
    session = db_session.exec(query).first()

    if not session:
        raise HTTPException(401, "Invalid or expired session")

    # Check if session is expired
    if session.expiresAt < datetime.utcnow():
        raise HTTPException(401, "Session expired")

    # Fetch user from database
    user = db_session.get(User, session.userId)

    if not user:
        raise HTTPException(401, "User not found")

    return user
```

---

## Required Changes

1. **Create Better Auth Session Model** (`backend/src/models/session.py`):
   ```python
   from sqlmodel import SQLModel, Field
   from datetime import datetime
   from uuid import UUID

   class BetterAuthSession(SQLModel, table=True):
       __tablename__ = "session"

       id: str = Field(primary_key=True)  # Session token
       userId: str = Field(index=True)  # User ID
       expiresAt: datetime
       ipAddress: str | None = None
       userAgent: str | None = None
   ```

2. **Update Dependencies** (`backend/src/auth/dependencies.py`):
   - Remove auth server HTTP calls
   - Add database query for session table
   - Validate expiration time

3. **Redeploy Backend**:
   ```bash
   cd phase-2/backend
   railway up --service tda-backend
   ```

---

## Why This Works

- **No Network Calls**: Faster validation (no HTTP round-trip to auth server)
- **Direct Database Access**: Single source of truth
- **Token Format Agnostic**: Works with incomplete token from JSON response
- **Same Database**: Backend and auth server share Neon PostgreSQL database
- **Better Auth Compatible**: Uses Better Auth's session table schema

---

## Next Steps

1. Create `BetterAuthSession` model
2. Update `get_current_user()` to query database
3. Test with fresh login
4. Redeploy to Railway
5. Verify dashboard loads without 401 errors
