# Quick Network Check - 2 Requests Only

Ignore the forgot-password 404 error - that's a Next.js prefetch issue, not the problem.

## Check These 2 Requests:

### 1. Login POST Request

Filter Network tab for: `sign-in`

Find: `POST https://backend-production-9a40.up.railway.app/api/auth/sign-in/email`

**Click on it → Headers tab → Response Headers**

**Do you see `Set-Cookie: auth_token=...`?**
- YES → Copy the full line
- NO → This is the problem

### 2. Tasks GET Request

Filter Network tab for: `tasks`

Find: `GET https://backend-production-9a40.up.railway.app/api/tasks`

**Click on it → Headers tab → Request Headers**

**Do you see `Cookie: auth_token=...`?**
- YES → Copy it
- NO → **This confirms SameSite issue**

---

## Quick Answer:

If you see Set-Cookie in login response but NO Cookie in tasks request, the issue is `SameSite=Lax` blocking cross-domain cookies.

**Just tell me**: Does tasks request have a Cookie header? (Yes/No)
