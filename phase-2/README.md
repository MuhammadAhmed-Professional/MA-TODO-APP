# Phase II: Full-Stack Web App + Phase III: AI Chatbot

**Status**: Complete (100%)
**Live**: [https://frontend-six-coral-90.vercel.app](https://frontend-six-coral-90.vercel.app)
**API**: [https://backend-production-9a40.up.railway.app/docs](https://backend-production-9a40.up.railway.app/docs)
**Auth**: [https://auth-server-production-cd0e.up.railway.app/health](https://auth-server-production-cd0e.up.railway.app/health)

---

## Architecture

| Service | Port | Technology | Deployment | URL |
|---------|------|-----------|------------|-----|
| **Frontend** | 3000 | Next.js 16, React 19, TypeScript | Vercel | [frontend-six-coral-90.vercel.app](https://frontend-six-coral-90.vercel.app) |
| **Backend** | 8000 | FastAPI 0.120+, SQLModel | Railway | [backend-production-9a40.up.railway.app](https://backend-production-9a40.up.railway.app) |
| **Auth Server** | 3001 | Express, Better Auth | Railway | [auth-server-production-cd0e.up.railway.app](https://auth-server-production-cd0e.up.railway.app) |
| **Database** | - | Neon Serverless PostgreSQL | Neon | - |

---

## Features

### Phase II - Web App
- User signup/login with Better Auth (JWT + HttpOnly cookies)
- Full CRUD task management (7 RESTful endpoints)
- Priority levels, due dates, tags
- Sorting, filtering, pagination
- Responsive UI with Tailwind CSS + shadcn/ui
- Multi-language support (English + Urdu with RTL)
- Dark/light mode

### Phase III - AI Chatbot
- Natural language task management via chat interface
- OpenAI Agents SDK with Gemini model rotation
- Official MCP SDK (5 tools: add, list, complete, delete, update)
- Conversation history persisted in PostgreSQL
- Voice input (Web Speech API) + Voice output (Speech Synthesis)
- Stateless server design

---

## Running Locally

### Backend
```bash
cd phase-2/backend
cp .env.example .env  # Configure DATABASE_URL, JWT_SECRET
uv sync
uv run alembic upgrade head
uv run uvicorn src.main:app --reload --port 8000
```

### Auth Server
```bash
cd phase-2/auth-server
npm install
cp .env.example .env  # Configure DATABASE_URL, BETTER_AUTH_SECRET
npm run dev  # http://localhost:3001
```

### Frontend
```bash
cd phase-2/frontend
pnpm install
cp .env.local.example .env.local  # Configure NEXT_PUBLIC_API_URL
pnpm dev  # http://localhost:3000
```

---

## Testing

```bash
# Backend
cd phase-2/backend && uv run pytest tests/ -v

# Frontend
cd phase-2/frontend && pnpm test
```

---

## API Endpoints

### Authentication
- `POST /api/auth/sign-up/email` - Create account
- `POST /api/auth/sign-in/email` - Login
- `POST /api/auth/sign-out` - Logout
- `GET /api/auth/get-session` - Current user

### Tasks
- `GET /api/tasks` - List tasks (filter, sort, paginate)
- `POST /api/tasks` - Create task
- `GET /api/tasks/{id}` - Get task
- `PUT /api/tasks/{id}` - Full update
- `PATCH /api/tasks/{id}` - Partial update
- `PATCH /api/tasks/{id}/complete` - Toggle complete
- `DELETE /api/tasks/{id}` - Delete task

### Chat (Phase III)
- `POST /api/chat/conversations` - Create conversation
- `GET /api/chat/conversations` - List conversations
- `GET /api/chat/conversations/{id}` - Get conversation
- `POST /api/chat/conversations/{id}/messages` - Send message
- `GET /api/chat/conversations/{id}/messages` - Get messages
- `DELETE /api/chat/conversations/{id}` - Delete conversation

### Health
- `GET /health` - Health check

---

## Project Structure

```
phase-2/
├── frontend/                    # Next.js 16 (App Router)
│   ├── src/app/                # Pages (dashboard, chat, login, signup)
│   ├── src/components/         # UI components (tasks, chat, layout)
│   ├── src/hooks/              # Custom hooks (speech recognition/synthesis)
│   ├── src/locales/            # i18n translations (en.json, ur.json)
│   ├── src/lib/                # API client, auth, utilities
│   ├── Dockerfile              # Multi-stage build (standalone)
│   └── next.config.ts          # output: 'standalone'
├── backend/                     # FastAPI 0.120+
│   ├── src/api/                # Route handlers (auth, tasks, chat, tags)
│   ├── src/models/             # SQLModel models (user, task, conversation)
│   ├── src/services/           # Business logic (agent, task, auth)
│   ├── src/mcp_tools/          # 5 MCP tools
│   ├── src/mcp_server.py       # Official MCP SDK server
│   ├── src/auth/               # JWT utilities
│   ├── src/db/                 # Database session + Alembic migrations
│   └── Dockerfile              # Multi-stage build
└── auth-server/                 # Better Auth (Express)
    ├── src/auth.ts             # Better Auth configuration
    ├── src/server.ts           # Express server
    └── Dockerfile              # Multi-stage build
```

See `backend/CLAUDE.md` and `frontend/CLAUDE.md` for development guidelines.
