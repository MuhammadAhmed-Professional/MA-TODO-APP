# Quick Reference - Phase II & III Local Setup

**One-page cheat sheet for getting everything running**

---

## 📋 Pre-Setup Checklist (5 minutes)

```bash
# Check requirements
node --version      # Need: v18+
python3 --version   # Need: 3.13+
pnpm --version      # Need: 8.0+
uv --version        # Need: latest
```

Missing something? Install from:
- **Node**: https://nodejs.org/
- **Python**: https://www.python.org/downloads/
- **pnpm**: `npm install -g pnpm`
- **UV**: `pip install uv`

---

## 🚀 Quick Start (15 minutes)

### Terminal 1: Backend

```bash
cd /path/to/phase-1/phase-2/backend

# Create .env file
cat > .env << 'EOF'
DATABASE_URL=sqlite:///./test.db
OPENAI_API_KEY=sk_your_key_here
BETTER_AUTH_SECRET=your-secret
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
ENVIRONMENT=development
EOF

# Setup and start
uv sync
uv run alembic upgrade head
uv run uvicorn src.main:app --reload --port 8000
```

✅ Backend ready: http://localhost:8000

### Terminal 2: Frontend

```bash
cd /path/to/phase-1/phase-2/frontend

# Create .env.local
cat > .env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
BETTER_AUTH_SECRET=your-secret
NEXT_PUBLIC_ENVIRONMENT=development
EOF

# Setup and start
pnpm install
pnpm dev
```

✅ Frontend ready: http://localhost:3000

---

## 🌐 Access the App

| Feature | URL | After Login? |
|---------|-----|--------------|
| **Login/Signup** | http://localhost:3000 | No |
| **Dashboard** | http://localhost:3000/dashboard | Yes |
| **Tasks (Phase II)** | http://localhost:3000/dashboard/tasks | Yes |
| **Chat (Phase III)** | http://localhost:3000/chat | Yes |
| **API Health** | http://localhost:8000/health | No |

### Test Login Credentials
- **Email**: `test@example.com`
- **Password**: `Test@123456`

Or sign up with any email/password

---

## 🧪 Running Tests

### Backend Tests (Terminal 3)

```bash
cd phase-2/backend
uv run pytest -v
# Expected: 91 passed ✅
```

### Frontend E2E Tests (Terminal 4)

```bash
cd phase-2/frontend
pnpm test:e2e
# Expected: 18 passed ✅

# Interactive mode
pnpm test:e2e:ui

# With visible browser
pnpm test:e2e:headed
```

---

## 📁 Important File Locations

```
phase-1/
├── phase-2/backend/
│   ├── .env                    ← Create this
│   ├── src/main.py            ← FastAPI app
│   ├── tests/                 ← Test files (91 tests)
│   └── tests/load/            ← Load testing script
├── phase-2/frontend/
│   ├── .env.local             ← Create this
│   ├── src/app/               ← Next.js routes
│   ├── src/components/chat/   ← Chat components
│   └── tests/e2e/             ← E2E tests (18 tests)
├── LOCAL_SETUP_GUIDE.md       ← Detailed setup (you are here → QUICK_START_GUIDE.md)
└── QUICK_START_GUIDE.md       ← 3-step quick start
```

---

## 🔧 Terminal Setup

You need **4 terminals total**:

| # | Purpose | Command |
|---|---------|---------|
| 1 | Backend | `cd phase-2/backend && uv run uvicorn src.main:app --reload` |
| 2 | Frontend | `cd phase-2/frontend && pnpm dev` |
| 3 | Backend Tests | `cd phase-2/backend && uv run pytest -v` |
| 4 | E2E Tests | `cd phase-2/frontend && pnpm test:e2e` |

**Note**: Keep terminals 1 & 2 running. Use 3 & 4 for testing.

---

## 🆘 Troubleshooting Quick Fix

| Problem | Solution |
|---------|----------|
| **Port 3000 in use** | `kill -9 $(lsof -t -i :3000)` |
| **Port 8000 in use** | `kill -9 $(lsof -t -i :8000)` |
| **API key not set** | Add `OPENAI_API_KEY=sk_...` to `.env` |
| **DB connection error** | Delete `test.db`, run `uv run alembic upgrade head` |
| **Module not found** | `cd phase-2/backend && uv sync` |
| **Node modules broken** | `cd phase-2/frontend && rm -rf node_modules && pnpm install` |
| **Cache issues** | `rm -rf .next` in frontend dir |

---

## 📊 Expected Output

### Backend Startup ✅
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Frontend Startup ✅
```
▲ Next.js 16.x.x
  - Local:        http://localhost:3000
✓ Ready in X.XXs
```

### Backend Tests ✅
```
test_conversation_models.py ........ (18 passed)
test_mcp_tools.py .............. (32 passed)
test_agent_service.py ........... (19 passed)
test_chat_api.py ................ (21 passed)
======================== 91 passed in X.XXs ========================
```

### E2E Tests ✅
```
chat.spec.ts ..................... (18 passed)
======================== 18 passed ========================
```

---

## 🧭 API Endpoints

### Authentication (Phase II)
```
POST   /api/auth/signup              Create account
POST   /api/auth/signin              Login
POST   /api/auth/signout             Logout
GET    /api/auth/me                  Get current user
```

### Tasks (Phase II)
```
POST   /api/tasks                    Create task
GET    /api/tasks                    List tasks
GET    /api/tasks/{id}               Get one task
PATCH  /api/tasks/{id}               Update task
DELETE /api/tasks/{id}               Delete task
```

### Chat (Phase III)
```
POST   /api/chat/conversations           Create conversation
GET    /api/chat/conversations           List conversations
GET    /api/chat/conversations/{id}      Get conversation
POST   /api/chat/conversations/{id}/messages   Send message
GET    /api/chat/conversations/{id}/messages   Get messages
DELETE /api/chat/conversations/{id}      Delete conversation
```

---

## 💻 Useful Commands

### Backend
```bash
# Database
uv run alembic upgrade head          # Apply migrations
uv run alembic revision --autogenerate -m "Description"

# Tests
uv run pytest -v                     # Run all tests
uv run pytest tests/unit/ -v         # Run only unit tests
uv run pytest tests/integration/ -v  # Run only integration tests
uv run pytest -k "test_name" -v      # Run specific test

# Linting
uv run ruff check .                  # Check code style
uv run ruff format .                 # Format code
```

### Frontend
```bash
# Development
pnpm dev                             # Start dev server
pnpm build                           # Build for production
pnpm start                           # Start production server

# Tests
pnpm test                            # Unit tests
pnpm test:e2e                        # E2E tests
pnpm test:coverage                   # Coverage report

# Quality
pnpm lint                            # ESLint
pnpm type-check                      # TypeScript check
```

---

## 🔐 Environment Variables

### Backend (.env)
```
DATABASE_URL=sqlite:///./test.db
OPENAI_API_KEY=sk_test_abc123...
BETTER_AUTH_SECRET=your-secret-key
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
ENVIRONMENT=development
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
BETTER_AUTH_SECRET=your-secret-key
NEXT_PUBLIC_ENVIRONMENT=development
```

---

## 📱 Test the Chat Feature

**Start a conversation with the AI:**

1. Open http://localhost:3000/chat
2. Click "Start Chat" or "+ New Chat"
3. Type: `Add a task called 'Demo Task'`
4. Press `Ctrl+Enter` or click Send
5. See AI response with task created!

**Try these commands:**
- "Show me all my tasks"
- "Mark the first task as complete"
- "Delete all completed tasks"
- "How many tasks do I have?"

---

## 📞 Getting Help

| Issue | See |
|-------|-----|
| **Detailed setup** | `LOCAL_SETUP_GUIDE.md` |
| **Quick start (3 steps)** | `QUICK_START_GUIDE.md` |
| **Project overview** | `FINAL_STATUS_REPORT.md` |
| **Test details** | `CHAT_E2E_TESTS.md` |
| **Load testing** | `LOAD_TESTING_GUIDE.md` |

---

## ✅ Verification Checklist

After setup, verify everything:

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Can see login page at http://localhost:3000
- [ ] Can create account / login
- [ ] Can see dashboard after login
- [ ] Can see tasks section (Phase II)
- [ ] Can see chat section (Phase III)
- [ ] Backend tests pass (91/91)
- [ ] E2E tests pass (18/18)

If all checked ✅, you're ready to go!

---

## ⏱️ Time Estimates

```
First-time setup:    15-20 minutes
   - Environment:    2 minutes
   - Dependencies:   8-10 minutes
   - Database:       2 minutes
   - Starting:       3-5 minutes

Subsequent runs:     5 minutes
   - Just start:     5 minutes
   - No setup needed

Testing:            5 minutes
   - Backend tests:  2 minutes
   - E2E tests:      3 minutes
```

---

## 🎯 What You'll Have

✅ Phase II (Web App)
- Full-featured task management
- User authentication
- Dashboard with statistics

✅ Phase III (AI Chatbot)
- Natural language task commands
- OpenAI GPT-4 integration
- Conversation persistence
- Real-time messaging

✅ Complete Test Coverage
- 91 backend tests
- 18 E2E tests
- All passing ✅

---

## 🚀 You're Ready!

Start with **Terminal 1 & 2** from the quick start section above, then:
1. Open http://localhost:3000
2. Create account or login
3. Try creating a task
4. Try the chat feature

**Enjoy!** 🎉

---

**Questions?** See detailed guide: `LOCAL_SETUP_GUIDE.md`

