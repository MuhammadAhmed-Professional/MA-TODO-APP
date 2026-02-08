# 🚀 Phase 2 - Complete Local Setup Guide

**Status**: ✅ All services configured and ready to run
**Architecture**: Auth Server (3001) + Backend (8000) + Frontend (3000)

## Quick Start (Recommended)

### Option 1: Using Batch Files (Windows)

**Open 3 separate Command Prompt/PowerShell windows:**

```cmd
# Window 1: Auth Server (Port 3001)
cd E:\Hackathons-Panaversity\Hackathon-ii\MA-TODO\phase-2\auth-server
start_auth.bat

# Window 2: Backend (Port 8000)
cd E:\Hackathons-Panaversity\Hackathon-ii\MA-TODO\phase-2\backend
start_backend.bat

# Window 3: Frontend (Port 3000)
cd E:\Hackathons-Panaversity\Hackathon-ii\MA-TODO\phase-2\frontend
start_frontend.bat
```

### Option 2: Manual Commands

**Terminal 1 - Auth Server:**
```bash
cd phase-2/auth-server
npm install  # Only needed first time
npm run dev  # Starts on http://localhost:3001
```

**Terminal 2 - Backend:**
```bash
cd phase-2/backend
uv sync  # Only needed first time
uv run uvicorn src.main:app --reload --port 8000  # Starts on http://localhost:8000
```

**Terminal 3 - Frontend:**
```bash
cd phase-2/frontend
npm install --legacy-peer-deps  # Only needed first time
npm run dev  # Starts on http://localhost:3000
```

## 🌐 Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:3000 | Main Todo App (Next.js) |
| **Backend API** | http://localhost:8000 | RESTful API (FastAPI) |
| **API Docs** | http://localhost:8000/docs | Swagger UI Documentation |
| **Auth Server** | http://localhost:3001 | Authentication Service (Better Auth) |

## ✅ Verify Everything is Working

### 1. Check Auth Server (Port 3001)
```bash
curl http://localhost:3001/api/auth/health
# Should return authentication service status
```

### 2. Check Backend (Port 8000)
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy","timestamp":"..."}
```

Open: http://localhost:8000/docs (Swagger UI should load)

### 3. Check Frontend (Port 3000)
Open: http://localhost:3000 (Todo App should load)

## 🛠 Prerequisites

### Required Software:
- **Python 3.13+** (for backend)
- **UV** (Python package manager)
- **Node.js 18+** (for auth server & frontend)
- **npm** (comes with Node.js)

### Check Your Setup:
```bash
python --version    # Should be 3.13+
uv --version        # Should be 0.8+
node --version      # Should be 18+
npm --version       # Should be 8+
```

## 📁 Project Structure

```
phase-2/
├── auth-server/          # Better Auth service (Port 3001)
│   ├── src/
│   ├── package.json
│   ├── .env              # Auth configuration
│   └── start_auth.bat    # ✅ Windows startup script
├── backend/              # FastAPI server (Port 8000)
│   ├── src/
│   ├── pyproject.toml
│   ├── .env              # Database & JWT config
│   └── start_backend.bat # ✅ Windows startup script
└── frontend/             # Next.js app (Port 3000)
    ├── app/
    ├── components/
    ├── package.json
    ├── .env.local        # Frontend config
    └── start_frontend.bat # ✅ Windows startup script
```

## 🔧 Environment Configuration

All `.env` files are already configured with development defaults.

### Backend (.env)
```
DATABASE_URL=sqlite:///./phase2_todo.db
JWT_SECRET=your-secret-key-here
CORS_ORIGINS=http://localhost:3000
```

### Auth Server (.env)
```
PORT=3001
DATABASE_URL=sqlite://./auth.db
JWT_SECRET=your-auth-secret-here
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_AUTH_URL=http://localhost:3001
```

## 🧪 Testing

### Backend Tests
```bash
cd phase-2/backend
uv run pytest tests/ -v
```

### Frontend Tests
```bash
cd phase-2/frontend
npm test          # Unit tests (Vitest)
npm run test:e2e  # E2E tests (Playwright)
```

## 📋 Features Available

### ✅ Completed Features:
- User registration and login
- JWT authentication with HttpOnly cookies
- Task CRUD operations (Create, Read, Update, Delete)
- Task completion toggle
- Responsive UI with Tailwind CSS
- API documentation with Swagger UI

### 🚧 In Progress:
- Task filtering and search
- User profiles
- Task categories

## 🚨 Troubleshooting

### Port Already in Use:
```bash
# Kill process on port 8000 (Backend)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Kill process on port 3000 (Frontend)
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Kill process on port 3001 (Auth)
netstat -ano | findstr :3001
taskkill /PID <PID> /F
```

### Dependencies Issues:
```bash
# Backend: Clear UV cache and reinstall
cd phase-2/backend
uv sync --refresh

# Frontend: Clear npm cache and reinstall
cd phase-2/frontend
npm cache clean --force
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps

# Auth Server: Reinstall dependencies
cd phase-2/auth-server
rm -rf node_modules package-lock.json
npm install
```

### Database Issues:
```bash
cd phase-2/backend
# Reset database
rm phase2_todo.db
uv run alembic upgrade head
```

## 🎯 Next Steps

1. **Start All Services** using the batch files or manual commands above
2. **Open Frontend** at http://localhost:3000
3. **Register a new user** to test authentication
4. **Create some tasks** to test CRUD operations
5. **Check API Docs** at http://localhost:8000/docs

## 📞 Support

If you encounter issues:

1. Check that all three services are running on their respective ports
2. Verify environment files are present and configured
3. Ensure all dependencies are installed
4. Check the console output for error messages

**Service Dependencies:**
- Frontend depends on Backend (API calls)
- Backend depends on Auth Server (JWT validation)
- All services need to be running simultaneously

**Startup Order:**
1. Auth Server (3001) - Start first
2. Backend (8000) - Start second  
3. Frontend (3000) - Start last

---

**Status**: ✅ Phase 2 is fully configured and ready to run
**Total Setup Time**: ~5 minutes for first run, ~30 seconds for subsequent runs
**Architecture**: Modern full-stack with authentication