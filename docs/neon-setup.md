# Neon Serverless PostgreSQL Setup Guide

## T011: Create Neon Database

### Prerequisites
- Neon account (sign up at https://neon.tech)
- GitHub account (for OAuth login) or email/password

### Step-by-Step Instructions

#### 1. Create Neon Account
1. Visit https://neon.tech
2. Click "Sign Up" and authenticate with GitHub or email
3. Complete account verification

#### 2. Create New Project
1. Click "Create Project" from dashboard
2. **Project Name**: `phase2-todo-production` (or your preferred name)
3. **PostgreSQL Version**: Select latest (16.x recommended)
4. **Region**: Choose closest to your deployment region
   - US East (N. Virginia) - `us-east-1`
   - US West (Oregon) - `us-west-2`
   - Europe (Frankfurt) - `eu-central-1`
5. Click "Create Project"

#### 3. Get Connection String
After project creation, you'll see the connection details:

```
postgresql://[username]:[password]@[endpoint].neon.tech/[database]?sslmode=require
```

Example:
```
postgresql://alex:AbC123xyz@ep-cool-meadow-123456.us-east-2.neon.tech/neondb?sslmode=require
```

#### 4. Configure Backend Environment
1. Copy connection string from Neon dashboard
2. Navigate to `backend/.env` (create if doesn't exist)
3. Add the following:

```bash
# Copy from backend/.env.example and update with real values
DATABASE_URL=postgresql://[username]:[password]@[endpoint].neon.tech/[database]?sslmode=require

# Generate with: openssl rand -hex 32
JWT_SECRET=your-actual-secret-here

# Your frontend URL
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

ENVIRONMENT=development
```

#### 5. Test Connection
Once configured, test the connection:

```bash
cd backend
uv run python -c "
from sqlmodel import create_engine
import os
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    result = conn.execute('SELECT version()')
    print('Connected!', result.fetchone())
"
```

### Neon Features Relevant to This Project

**Autoscaling**: Automatically scales to zero when inactive (free tier)
**Branching**: Create database branches for testing (like Git for databases)
**Connection Pooling**: Built-in pooling via `?pooling=true` parameter
**Point-in-Time Recovery**: Automated backups

### Connection String Parameters

Standard connection:
```
postgresql://user:pass@host/db?sslmode=require
```

With connection pooling (recommended for production):
```
postgresql://user:pass@host/db?sslmode=require&pooling=true
```

### Security Best Practices

1. ✅ Never commit `.env` with real credentials to Git
2. ✅ Use `.env.example` for documentation only
3. ✅ Rotate database password if accidentally exposed
4. ✅ Use separate databases for development/staging/production
5. ✅ Enable SSL mode (`sslmode=require`) always

### Troubleshooting

**Connection timeout**:
- Check if your IP is allowed (Neon allows all IPs by default)
- Verify region selection (use closest region for lower latency)

**Authentication failed**:
- Double-check username and password (copy-paste to avoid typos)
- Ensure no extra spaces in connection string

**SSL error**:
- Always include `?sslmode=require` in connection string
- Neon requires SSL connections

### Alternative: Local PostgreSQL for Development

If you prefer local development first:

```bash
# Install PostgreSQL locally
# macOS: brew install postgresql@16
# Ubuntu: sudo apt install postgresql-16

# Start PostgreSQL
# macOS: brew services start postgresql@16
# Ubuntu: sudo systemctl start postgresql

# Create database
createdb phase2_todo_dev

# Use local connection string in .env
DATABASE_URL=postgresql://localhost/phase2_todo_dev
```

Then migrate to Neon for deployment.

---

## Next Steps After T011

Once Neon database is created and `DATABASE_URL` is configured:

1. **T012**: Initialize Alembic for migrations
2. **T013**: Create database session manager
3. **T017**: Test with health check endpoint
4. **Phase 3**: Create User and Task database models

---

*Last Updated*: 2025-12-06
*Phase*: Phase 2 - Foundational Infrastructure
