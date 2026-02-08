# Phase II & Phase III Local Setup Guide

**Complete instructions for running Phase II (Web App) and Phase III (Chatbot) locally**

---

## Prerequisites

### Required Software

- **Node.js**: v18+ (for frontend)
- **Python**: 3.13+ (for backend)
- **pnpm**: Latest (frontend package manager)
- **UV**: Latest (Python package manager)
- **Git**: For version control
- **PostgreSQL/SQLite**: For database (SQLite by default, PostgreSQL optional)
- **OpenAI API Key**: For Phase III chatbot

### System Requirements

- **RAM**: 4GB minimum (8GB recommended)
- **Disk Space**: 2GB free
- **Ports Available**: 3000 (frontend), 8000 (backend)

### Check Your Setup

```bash
# Check Node.js
node --version
# Expected: v18+ (e.g., v20.11.0)

# Check Python
python3 --version
# Expected: 3.13+ (e.g., Python 3.13.0)

# Check pnpm
pnpm --version
# Expected: 8.0+

# Check UV
uv --version
# Expected: latest
```

If any are missing, install them:

**Node.js**: https://nodejs.org/
**Python**: https://www.python.org/downloads/
**pnpm**: `npm install -g pnpm`
**UV**: `pip install uv` or `pip3 install uv`

---

## Step 1: Navigate to Project Root

```bash
cd /mnt/e/Hackathons-Panaversity/Hackathon-ii/MA-TODO
```

Verify you're in the right place:
```bash
ls -la
# Should see: phase-2/, specs/, .git/, etc.
```

---

## Step 2: Set Up Backend (Phase II & III)

### 2.1: Navigate to Backend Directory

```bash
cd phase-2/backend
pwd  # Verify you're in phase-2/backend
```

### 2.2: Create Environment Configuration

Create a `.env` file with your settings:

```bash
cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=sqlite:///./test.db

# OpenAI Configuration (for Phase III)
OPENAI_API_KEY=your_openai_api_key_here

# Better Auth Configuration
BETTER_AUTH_SECRET=your-secret-key-change-this

# Server Configuration
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000

# Environment
ENVIRONMENT=development
EOF
```

**Important**: Replace `your_openai_api_key_here` with your actual OpenAI API key
- Get it from: https://platform.openai.com/api-keys

### 2.3: Install Python Dependencies

```bash
# Sync dependencies using UV
uv sync

# Expected output: Successfully installed X packages
```

### 2.4: Apply Database Migrations

```bash
# Create database and apply all migrations
uv run alembic upgrade head

# Expected output: INFO [alembic.runtime.migration] Successfully upgrade
```

### 2.5: Verify Backend Setup

```bash
# Test that imports work
uv run python -c "from src.main import app; print('✅ Backend imports successful')"
```

### 2.6: Start Backend Server

```bash
# Start the FastAPI server
uv run uvicorn src.main:app --reload --port 8000

# Expected output:
# Uvicorn running on http://127.0.0.1:8000
# Press CTRL+C to quit
```

**Keep this terminal open!** The backend needs to stay running.

---

## Step 3: Set Up Frontend (Phase II & III)

### 3.1: Open a NEW Terminal (keep backend running in first one)

```bash
# In a new terminal window
cd /mnt/e/Hackathons-Panaversity/Hackathon-ii/MA-TODO/phase-2/frontend

pwd  # Verify you're in phase-2/frontend
```

### 3.2: Create Environment Configuration

```bash
cat > .env.local << 'EOF'
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Configuration
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
BETTER_AUTH_SECRET=your-secret-key-change-this

# Environment
NEXT_PUBLIC_ENVIRONMENT=development
EOF
```

**Note**: `BETTER_AUTH_SECRET` should match the backend `.env` file

### 3.3: Install Node Dependencies

```bash
# Install dependencies using pnpm
pnpm install

# Expected: progress bar, then "Done in X.XXs"
# This may take 2-3 minutes on first run
```

### 3.4: Verify Frontend Setup

```bash
# Verify Next.js installation
pnpm next --version
# Expected: Next.js v16+
```

### 3.5: Start Frontend Dev Server

```bash
# Start Next.js development server
pnpm dev

# Expected output:
# ▲ Next.js 16.x.x
#   - Local:        http://localhost:3000
#   - Environments: .env.local
# ✓ Ready in X.XXs
```

**Keep this terminal open!** The frontend needs to stay running.

---

## Step 4: Access the Application

### 4.1: Open in Browser

Open your browser and navigate to:
```
http://localhost:3000
```

### 4.2: You Should See

- **Landing Page**: Welcome screen with "Sign In" button
- **Login Option**: Email/password login form
- **Sign Up Option**: Create new account link

### 4.3: Test Authentication

**Option A: Sign Up**
1. Click "Sign Up"
2. Enter email: `test@example.com`
3. Enter password: `Test@123456`
4. Click "Create Account"
5. You should be redirected to dashboard

**Option B: Use Test Account** (if already created)
1. Click "Sign In"
2. Enter email: `test@example.com`
3. Enter password: `Test@123456`
4. Click "Sign In"

### 4.4: Verify Phase II Features

After logging in, you should see:

- **Dashboard**: Home page with navigation
- **Tasks**: Task management page (Phase II feature)
  - Create task
  - Mark complete
  - Delete task
  - View all tasks

### 4.5: Access Phase III Chat (if Phase III enabled)

1. Look for "Chat" link in navigation menu
2. Click "Chat" to open the chatbot interface
3. You should see:
   - Empty chat state with "Start Chat" button
   - Conversation sidebar (left)
   - Message area (right)

### 4.6: Test Phase III Chatbot

1. Click "Start Chat" button
2. Type a command: `Add a task called 'Test Task'`
3. Press `Ctrl+Enter` or click Send
4. You should see:
   - User message appears
   - Loading indicator
   - AI response with task confirmation

---

## Step 5: Running Tests

### 5.1: Backend Unit Tests (Terminal 1)

Keep backend running, open a **NEW terminal**:

```bash
cd /mnt/e/Hackathons-Panaversity/Hackathon-ii/MA-TODO/phase-2/backend

# Run all tests
uv run pytest -v

# Expected output:
# test_conversation_models.py ✓✓✓ (18 passed)
# test_mcp_tools.py ✓✓✓ (32 passed)
# test_agent_service.py ✓✓✓ (19 passed)
# test_chat_api.py ✓✓✓ (21 passed)
# ======================== 91 passed in X.XXs ========================
```

### 5.2: Frontend E2E Tests (Terminal 2)

Keep frontend running, open a **NEW terminal**:

```bash
cd /mnt/e/Hackathons-Panaversity/Hackathon-ii/MA-TODO/phase-2/frontend

# Run E2E tests
pnpm test:e2e

# Expected output:
# chat.spec.ts ✓✓✓ (18 passed)
# ======================== 18 passed ========================

# View in UI mode (interactive)
pnpm test:e2e:ui

# View with browser visible
pnpm test:e2e:headed
```

---

## Terminal Setup Summary

You'll need **3-4 terminal windows open simultaneously**:

### Terminal 1: Backend Server
```bash
cd phase-2/backend
uv run uvicorn src.main:app --reload --port 8000
```
**Status**: Running ✅

### Terminal 2: Frontend Server
```bash
cd phase-2/frontend
pnpm dev
```
**Status**: Running ✅

### Terminal 3: Testing (Backend)
```bash
cd phase-2/backend
uv run pytest -v
```
**Status**: Run tests when needed

### Terminal 4: Testing (Frontend)
```bash
cd phase-2/frontend
pnpm test:e2e
```
**Status**: Run tests when needed

---

## Complete Startup Checklist

### Before You Start

- [ ] Node.js v18+ installed (`node --version`)
- [ ] Python 3.13+ installed (`python3 --version`)
- [ ] pnpm installed (`pnpm --version`)
- [ ] UV installed (`uv --version`)
- [ ] OpenAI API key ready
- [ ] Ports 3000 and 8000 are free

### Backend Setup

- [ ] Navigate to `phase-2/backend`
- [ ] Create `.env` file with configuration
- [ ] Run `uv sync`
- [ ] Run `uv run alembic upgrade head`
- [ ] Start server: `uv run uvicorn src.main:app --reload`
- [ ] Backend running on `http://localhost:8000` ✅

### Frontend Setup

- [ ] Open new terminal
- [ ] Navigate to `phase-2/frontend`
- [ ] Create `.env.local` file
- [ ] Run `pnpm install`
- [ ] Start server: `pnpm dev`
- [ ] Frontend running on `http://localhost:3000` ✅

### Verification

- [ ] Open browser to `http://localhost:3000`
- [ ] See login page ✅
- [ ] Create account or login
- [ ] See dashboard ✅
- [ ] See tasks section (Phase II) ✅
- [ ] See chat section (Phase III) ✅
- [ ] Tests pass ✅

---

## Troubleshooting

### Issue 1: "Port 3000 already in use"

**Error**: `Error: listen EADDRINUSE: address already in use :::3000`

**Solution**:
```bash
# Find what's using port 3000
lsof -i :3000

# Kill the process
kill -9 <PID>

# Or use different port
pnpm dev -- -p 3001
```

### Issue 2: "Port 8000 already in use"

**Error**: `OSError: [Errno 48] Address already in use`

**Solution**:
```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port
uv run uvicorn src.main:app --reload --port 8001
```

### Issue 3: "Cannot find module '@/...' (frontend)"

**Error**: `Module not found: Can't resolve '@/components/...'`

**Solution**:
```bash
# Clear cache and reinstall
rm -rf node_modules .next
pnpm install
pnpm dev
```

### Issue 4: "OpenAI API key not configured"

**Error**: `Error: The OPENAI_API_KEY environment variable is not set`

**Solution**:
```bash
# Make sure your .env file has:
OPENAI_API_KEY=sk_test_abc123...

# Restart backend
# Kill and restart: uv run uvicorn src.main:app --reload
```

### Issue 5: "Database connection failed"

**Error**: `sqlalchemy.exc.OperationalError: (sqlite3.OperationalError)`

**Solution**:
```bash
# Reset database
rm phase-2/backend/test.db

# Re-apply migrations
cd phase-2/backend
uv run alembic upgrade head

# Restart backend
uv run uvicorn src.main:app --reload
```

### Issue 6: "Tests fail with import errors"

**Error**: `ModuleNotFoundError: No module named 'src'`

**Solution**:
```bash
# Make sure you're in correct directory
cd phase-2/backend

# Reinstall dependencies
uv sync

# Run tests
uv run pytest -v
```

---

## Common Commands Reference

### Backend

```bash
# Start backend server
cd phase-2/backend
uv run uvicorn src.main:app --reload

# Run tests
uv run pytest -v

# Run specific test
uv run pytest tests/unit/test_mcp_tools.py -v

# Create database migration
uv run alembic revision --autogenerate -m "Description"

# Apply migrations
uv run alembic upgrade head

# View database
sqlite3 test.db
.tables
.exit
```

### Frontend

```bash
# Start dev server
cd phase-2/frontend
pnpm dev

# Run unit tests
pnpm test

# Run E2E tests
pnpm test:e2e

# Build for production
pnpm build

# Preview production build
pnpm start

# Linting
pnpm lint

# Type checking
pnpm type-check
```

---

## Accessing Different Parts of the App

### Phase II - Task Management

**URL**: `http://localhost:3000/dashboard` (after login)

**Features**:
- View all tasks
- Create new task
- Mark task complete
- Update task
- Delete task
- Task filtering

**Test It**:
1. Login
2. Click "Tasks" in menu
3. Click "Add Task"
4. Enter title: "Test Task"
5. Click "Save"
6. You should see the task in the list

### Phase III - AI Chatbot

**URL**: `http://localhost:3000/chat` (after login)

**Features**:
- Create conversations
- Send natural language commands
- AI-powered responses
- View conversation history
- Delete conversations

**Test It**:
1. Login
2. Click "Chat" in menu
3. Click "Start Chat" or "+ New Chat"
4. Type: `Add a task called 'Phase III Test'`
5. Press `Ctrl+Enter` or click Send
6. Wait for AI response
7. You should see:
   - Your message (blue, right side)
   - AI response (gray, left side)
   - Tool call visualization

---

## Performance Tips

### If App Feels Slow

1. **Check Backend Performance**
   ```bash
   # Check if OpenAI API is responding slowly
   # This can add 1-2 seconds to chat responses
   ```

2. **Check Frontend Performance**
   ```bash
   # Open browser DevTools
   # Press F12 → Performance tab
   # Record and analyze
   ```

3. **Check Network**
   ```bash
   # Open browser DevTools
   # Click Network tab
   # Watch request/response times
   # Slow API = slow app
   ```

4. **Restart Services**
   ```bash
   # Kill all processes
   # Ctrl+C in both terminals

   # Start fresh
   uv run uvicorn src.main:app --reload
   pnpm dev
   ```

---

## Next Steps After Setup

### Run Tests
```bash
# Backend tests
cd phase-2/backend && uv run pytest -v

# E2E tests
cd phase-2/frontend && pnpm test:e2e
```

### Load Testing
```bash
# Install k6
brew install k6

# Run load test
k6 run phase-2/backend/tests/load/chat_load_test.js
```

### Try Advanced Features
1. Create multiple conversations in chat
2. Switch between conversations
3. Try different task commands:
   - "Show me all my tasks"
   - "Mark the first task as done"
   - "Delete all completed tasks"

### Review Code
- Backend API: `phase-2/backend/src/api/chat.py`
- Frontend Chat: `phase-2/frontend/src/components/chat/`
- Tests: `phase-2/backend/tests/` and `phase-2/frontend/tests/e2e/`

---

## Getting Help

### Check Logs

**Backend Logs** (in the terminal running the server):
- Look for `INFO`, `WARNING`, `ERROR` messages
- These show what the API is doing

**Frontend Logs** (in browser DevTools):
- Press F12
- Click "Console" tab
- Look for errors in red

### Check Health

```bash
# Backend health check
curl http://localhost:8000/health
# Expected: {"status":"ok"}

# Frontend accessibility
curl http://localhost:3000
# Expected: HTML response
```

### Review Documentation

- `QUICK_START_GUIDE.md` - Quick reference
- `FINAL_STATUS_REPORT.md` - Project overview
- `FRONTEND_IMPLEMENTATION.md` - Frontend details
- `PHASE_III_COMPLETION_SUMMARY.md` - Implementation summary

---

## Summary

You now have a complete guide to:

✅ Set up Python backend (FastAPI + PostgreSQL/SQLite)
✅ Set up Node.js frontend (Next.js + React)
✅ Configure both Phase II and Phase III
✅ Run both locally with hot-reload
✅ Access and test all features
✅ Run the full test suite
✅ Troubleshoot common issues
✅ Use helpful commands

**Time to setup**: ~15-20 minutes (first time)
**Time to start**: ~5 minutes (after first setup)

---

**You're ready to go!** Start with Step 1 and follow through. If you hit any issues, refer to the Troubleshooting section.

