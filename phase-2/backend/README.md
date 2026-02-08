# Phase II Backend - FastAPI

Complete backend implementation for Phase II full-stack todo application.

**Status**: ✅ Production Ready
**Framework**: FastAPI 0.110+
**ORM**: SQLModel
**Database**: Neon Serverless PostgreSQL
**Authentication**: JWT (Better Auth integration)

---

## Quick Start

### Get Backend Running in 10 Seconds

**Linux/macOS:**
```bash
./START_BACKEND.sh
```

**Windows PowerShell:**
```powershell
.\RUN_BACKEND.ps1
```

**Windows Command Prompt:**
```cmd
RUN_BACKEND.bat
```

Then open browser: http://localhost:8000/docs

---

## Documentation

- **[START_HERE.md](START_HERE.md)** - Quick startup guide (READ THIS FIRST)
- **[SETUP_COMPLETE.md](SETUP_COMPLETE.md)** - Full setup documentation and verification
- **[CLAUDE.md](CLAUDE.md)** - Development guidelines and code standards
- **[VENV_FIX.md](VENV_FIX.md)** - Troubleshooting virtual environment issues

---

## Project Structure

```
backend/
├── src/
│   ├── main.py                 # FastAPI app entry point
│   ├── api/                    # Route handlers
│   │   ├── auth.py            # Authentication endpoints
│   │   └── tasks.py           # Task CRUD endpoints
│   ├── models/                # SQLModel definitions
│   │   ├── user.py            # User model
│   │   └── task.py            # Task model
│   ├── services/              # Business logic
│   │   ├── auth_service.py    # Auth operations
│   │   └── task_service.py    # Task operations
│   ├── auth/                  # Auth utilities
│   │   ├── jwt.py             # JWT handling
│   │   └── dependencies.py    # FastAPI dependencies
│   ├── db/                    # Database layer
│   │   ├── session.py         # Session management
│   │   └── migrations/        # Alembic migrations
│   └── config.py              # Configuration
├── tests/
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── conftest.py            # Pytest fixtures
├── pyproject.toml             # Dependencies and config
├── .env.example               # Environment variables template
├── alembic.ini                # Database migrations config
└── pytest.ini                 # Testing configuration
```

---

## Key Features

✅ **User Authentication**
- JWT tokens with 15-minute expiry
- HttpOnly cookie storage
- Bcrypt password hashing
- Token refresh mechanism

✅ **Task Management**
- Full CRUD operations
- User ownership verification
- Pagination support
- Sorting and filtering

✅ **Database**
- SQLModel ORM
- Neon Serverless PostgreSQL
- Alembic migrations
- Connection pooling

✅ **API Documentation**
- Swagger UI at `/docs`
- ReDoc at `/redoc`
- OpenAPI schema at `/openapi.json`

✅ **Security**
- CORS protection
- CSRF prevention
- SQL injection protection
- Input validation with Pydantic
- XSS protection

---

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Create account
- `POST /api/auth/login` - Login with credentials
- `POST /api/auth/logout` - Logout
- `POST /api/auth/refresh` - Refresh token

### Tasks
- `GET /api/tasks` - List user's tasks
- `POST /api/tasks` - Create task
- `GET /api/tasks/{id}` - Get task details
- `PATCH /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task

### Health
- `GET /health` - Health check endpoint

---

## Environment Variables

**Required:**
```env
DATABASE_URL=postgresql://user:password@host.region.neon.tech/dbname
JWT_SECRET=your-256-bit-secret-key
JWT_ALGORITHM=HS256
CORS_ORIGINS=http://localhost:3000
```

See `.env.example` for all available variables.

---

## Common Commands

```bash
# Start development server
./START_BACKEND.sh  # or RUN_BACKEND.ps1 on Windows

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Create database migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Lint code
uv run ruff check src/

# Format code
uv run ruff format src/
```

---

## Integration with Phase II Stack

The backend runs alongside:

| Service | Port | Technology | Purpose |
|---------|------|-----------|---------|
| **Backend** | 8000 | FastAPI | REST API |
| **Auth Server** | 3001 | Express + Better Auth | Authentication |
| **Frontend** | 3000 | Next.js | User interface |

### Starting All Services

```bash
# Terminal 1: Backend
cd backend
./START_BACKEND.sh

# Terminal 2: Auth Server
cd auth-server
npm run dev

# Terminal 3: Frontend
cd frontend
pnpm dev
```

Access application at: http://localhost:3000

---

## Virtual Environment

- **Location**: `backend/.venv/` (isolated to backend)
- **Manager**: UV (`uv sync`)
- **Python**: 3.13+
- **Status**: ✅ Properly configured, no root conflicts

Run `./START_BACKEND.sh` to verify and setup venv.

---

## Testing

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/unit/test_models.py

# Run with output
uv run pytest -v

# Run with coverage report
uv run pytest --cov=src --cov-report=html
```

---

## Troubleshooting

### Port 8000 Already in Use
```bash
# Find process
lsof -i :8000

# Kill it
kill -9 <PID>
```

### Module Import Errors
```bash
uv sync --no-cache
```

### Database Connection Failed
- Check `DATABASE_URL` in `.env`
- Verify Neon database is active
- Check connection string format

### Venv Issues
See [VENV_FIX.md](VENV_FIX.md)

---

## Performance

- Database connection pooling: 5 connections
- Query optimization with indexes
- Pagination: max 100 items per request
- CORS configured for frontend
- Gzip compression enabled

---

## Deployment

### Local Development
```bash
./START_BACKEND.sh
```

### Production
See root `README.md` for:
- Docker containerization
- Cloud deployment options (Railway, Render, Fly.io)
- Environment setup
- Database backups

---

## Code Standards

Follow guidelines in [CLAUDE.md](CLAUDE.md):

✅ Thin controllers, fat services
✅ SQLModel for all database models
✅ Type hints everywhere
✅ Max 300 lines per file
✅ Comprehensive error handling
✅ Full test coverage

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

---

## Support

For issues or questions:
1. Check [VENV_FIX.md](VENV_FIX.md) for common problems
2. Review [CLAUDE.md](CLAUDE.md) for development guidelines
3. Check test files in `tests/` for implementation examples

---

**Last Updated**: December 13, 2025
**Maintainer**: Talal
**License**: MIT
