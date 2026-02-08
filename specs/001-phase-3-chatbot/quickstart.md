# Phase III Chatbot - Quick Start Guide

**Version**: 1.0.0
**Status**: Development Ready
**Created**: 2025-12-13
**Timeline**: 8 days (December 14-21, 2025)
**Points**: 200

---

## 1. Project Setup

### Prerequisites

- Python 3.13+
- Node.js 18+ (for frontend)
- PostgreSQL (via Neon)
- Git
- UV (Python package manager)
- pnpm (Node package manager)

### Environment Setup

#### Backend Environment

```bash
cd /mnt/d/Talal/Work/Hackathons-Panaversity/phase-1/phase-2/backend

# Copy environment template
cp .env.example .env.local

# Edit .env.local with:
OPENAI_API_KEY=sk-...                    # Get from OpenAI
DATABASE_URL=postgresql://...             # Neon connection string
JWT_SECRET=your-secret-key                # From Phase II
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=9000
RATE_LIMIT_PER_MINUTE=60
```

#### Frontend Environment

```bash
cd /mnt/d/Talal/Work/Hackathons-Panaversity/phase-1/phase-2/frontend

# Copy environment template
cp .env.example .env.local

# Edit .env.local with:
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

---

## 2. Database Setup

### Create Migration

```bash
cd /mnt/d/Talal/Work/Hackathons-Panaversity/phase-1/phase-2/backend

# Create migration for conversation tables
uv run alembic revision --autogenerate -m "Add conversation tables for Phase III"
```

### Review Migration

Edit the generated migration file to verify:
- Conversations table created
- Messages table created
- Indexes for performance
- Foreign key relationships

### Apply Migration

```bash
# Apply all pending migrations
uv run alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt"
# Should show: conversations, messages (plus existing Phase II tables)
```

---

## 3. Backend Implementation

### Project Structure

```
phase-2/backend/src/
├── api/
│   ├── __init__.py
│   ├── tasks.py           (existing Phase II)
│   └── chat.py            (NEW - Chat endpoint)
│
├── services/
│   ├── __init__.py
│   ├── task_service.py    (existing Phase II)
│   ├── agent_service.py   (NEW - OpenAI Agents SDK wrapper)
│   └── mcp_service.py     (NEW - MCP tool server)
│
├── models/
│   ├── __init__.py
│   ├── task.py            (existing Phase II)
│   ├── user.py            (existing Phase II)
│   └── conversation.py    (NEW - Conversation & Message models)
│
├── db/
│   ├── __init__.py
│   ├── session.py         (existing Phase II)
│   └── migrations/
│       └── versions/
│           └── 003_add_conversation_tables.py (NEW)
│
└── main.py                (update to include chat routes)
```

### Implementation Order

1. **models/conversation.py** - Define SQLModel classes
2. **db/migrations/versions/003_...py** - Create Alembic migration
3. **services/mcp_service.py** - Implement MCP server with 5 tools
4. **services/agent_service.py** - Wrap OpenAI Agents SDK
5. **api/chat.py** - Create POST /api/{user_id}/chat endpoint
6. **main.py** - Register routes and middleware

---

## 4. Key Implementation Files

### File 1: models/conversation.py

```python
# phase-2/backend/src/models/conversation.py

from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from uuid import UUID, uuid4
from datetime import datetime
from typing import List, Optional

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    title: Optional[str] = Field(None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    messages: List["Message"] = Relationship(back_populates="conversation")
    user: "User" = Relationship(back_populates="conversations")

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    role: str = Field(...)  # "user" or "assistant"
    content: str = Field(...)
    tool_calls: Optional[dict] = Field(None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    conversation: Conversation = Relationship(back_populates="messages")
    user: "User" = Relationship(back_populates="messages")
```

### File 2: services/mcp_service.py (Skeleton)

```python
# phase-2/backend/src/services/mcp_service.py

import json
from uuid import UUID
from sqlmodel import Session, select
from src.models.task import Task

class MCPServer:
    def __init__(self, session: Session):
        self.session = session

    async def handle_add_task(
        self, user_id: str, title: str, description: str | None = None
    ) -> dict:
        """Add task tool implementation"""
        # 1. Validate input
        # 2. Create task
        # 3. Return response

    async def handle_list_tasks(
        self, user_id: str, status: str = "all"
    ) -> dict:
        """List tasks tool implementation"""
        # 1. Query tasks from database
        # 2. Filter by status
        # 3. Return formatted list

    async def handle_complete_task(self, user_id: str, task_id: str) -> dict:
        """Complete task tool implementation"""
        # 1. Find task
        # 2. Mark as completed
        # 3. Return success/failure

    async def handle_delete_task(self, user_id: str, task_id: str) -> dict:
        """Delete task tool implementation"""
        # 1. Find task
        # 2. Delete from database
        # 3. Return success/failure

    async def handle_update_task(
        self,
        user_id: str,
        task_id: str,
        title: str | None = None,
        description: str | None = None
    ) -> dict:
        """Update task tool implementation"""
        # 1. Find task
        # 2. Update fields
        # 3. Return updated task
```

### File 3: services/agent_service.py (Skeleton)

```python
# phase-2/backend/src/services/agent_service.py

from openai import Anthropic
from src.services.mcp_service import MCPServer

class AgentService:
    def __init__(self, api_key: str, mcp_server: MCPServer):
        self.client = Anthropic(api_key=api_key)
        self.model = "gpt-4-turbo"  # or claude-3.5-sonnet
        self.temperature = 0.7
        self.mcp_server = mcp_server

    async def run_agent(
        self,
        user_message: str,
        conversation_history: list,
        user_id: str
    ) -> dict:
        """Run agent with conversation history"""
        # 1. Build system prompt
        # 2. Add conversation history
        # 3. Call agent API
        # 4. Handle tool calls
        # 5. Return response
        pass
```

### File 4: api/chat.py (Skeleton)

```python
# phase-2/backend/src/api/chat.py

from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from src.services.agent_service import AgentService
from src.models.conversation import Conversation, Message

router = APIRouter()

@router.post("/api/{user_id}/chat")
async def chat(
    user_id: UUID,
    request: dict,
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session),
    agent_service = Depends(get_agent_service)
):
    """
    Send message to chatbot and receive response with tool executions
    """
    # 1. Validate user_id matches current_user
    # 2. Get or create conversation
    # 3. Fetch message history
    # 4. Run agent
    # 5. Persist messages
    # 6. Return response
    pass
```

---

## 5. Dependencies to Install

### Backend

```bash
cd phase-2/backend

# Add OpenAI Agents SDK
uv add openai

# Verify installed
uv show openai

# For MCP (if needed)
uv add mcp
```

### Frontend

```bash
cd phase-2/frontend

# Add ChatKit component
pnpm add @openai/chatkit

# Verify
pnpm ls @openai/chatkit
```

---

## 6. Development Workflow

### Start Database

```bash
# Ensure Neon PostgreSQL is accessible
# Test connection:
psql $DATABASE_URL -c "SELECT version();"
```

### Start Backend

```bash
cd phase-2/backend

# Run with auto-reload
uv run uvicorn src.main:app --reload --port 8000
```

### Start Frontend

```bash
cd phase-2/frontend

# Run dev server
pnpm dev
```

Both will be accessible at:
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

---

## 7. Testing

### Unit Test Structure

```python
# tests/unit/test_agent_service.py

import pytest
from src.services.agent_service import AgentService

def test_agent_adds_task(mock_mcp_server):
    agent = AgentService(api_key="test", mcp_server=mock_mcp_server)
    response = agent.run_agent(
        user_message="Add a task to buy milk",
        conversation_history=[],
        user_id="550e8400-e29b-41d4-a716-446655440000"
    )
    assert "add_task" in response["tool_calls"]
```

### Run Tests

```bash
cd phase-2/backend

# Run all unit tests
uv run pytest tests/unit/

# Run integration tests
uv run pytest tests/integration/

# Run with coverage
uv run pytest tests/ --cov=src

# Run specific test file
uv run pytest tests/unit/test_agent_service.py -v
```

---

## 8. Deployment Checklist

### Pre-Deployment

- [ ] All environment variables set in .env
- [ ] Database migrations applied (`alembic upgrade head`)
- [ ] All tests passing (`pytest tests/`)
- [ ] No console errors in frontend (`pnpm build`)
- [ ] Rate limiting configured
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] CORS settings appropriate for production

### Deployment Commands

```bash
# Backend (Railway/Render)
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000

# Frontend (Vercel)
pnpm build && pnpm start
```

---

## 9. Key APIs & Documentation

### OpenAI Agents SDK

```python
from openai import Anthropic

client = Anthropic(api_key="sk-...")
response = client.messages.create(
    model="claude-3.5-sonnet-20241022",
    max_tokens=1024,
    tools=[...],
    messages=[...]
)
```

**Documentation**: https://sdk.vercel.ai/docs

### Official MCP SDK

```python
from mcp import Server

server = Server("todo-mcp")

@server.list_tools()
async def list_tools():
    return [...]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    return ...
```

**Documentation**: https://modelcontextprotocol.io/

### FastAPI

```python
from fastapi import FastAPI, Depends

app = FastAPI()

@app.post("/api/{user_id}/chat")
async def chat(...):
    pass
```

**Documentation**: https://fastapi.tiangolo.com/

---

## 10. Common Commands Reference

### Database

```bash
# Create migration
uv run alembic revision --autogenerate -m "Description"

# Apply migrations
uv run alembic upgrade head

# Rollback one version
uv run alembic downgrade -1

# View migration history
uv run alembic history
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test
uv run pytest tests/unit/test_chat_endpoint.py::test_add_task

# Run with coverage report
uv run pytest --cov=src --cov-report=html
```

### Git

```bash
# Check status
git status

# Stage changes
git add .

# Commit
git commit -m "Implement chat endpoint"

# Push to remote
git push origin 001-phase-3-chatbot

# Create pull request
gh pr create --title "Phase III: AI Chatbot" --body "Implements chat endpoint with MCP tools"
```

---

## 11. Troubleshooting

### Common Issues

**Issue: ModuleNotFoundError: No module named 'openai'**
```bash
# Solution: Install openai package
uv add openai
uv sync
```

**Issue: Database connection fails**
```bash
# Solution: Check DATABASE_URL environment variable
echo $DATABASE_URL
# Verify connection string format:
# postgresql://user:password@host:5432/dbname
```

**Issue: Agent not responding**
```bash
# Solution: Check OpenAI API key
echo $OPENAI_API_KEY
# Verify MCP server is running
# Check agent logs for errors
```

**Issue: Frontend can't connect to backend**
```bash
# Solution: Check CORS settings
# Verify backend is running on port 8000
# Check network tab in browser DevTools
```

---

## 12. Success Criteria

Phase III implementation is complete when:

✅ **Database**: Conversation and Message tables created and populated
✅ **Backend API**: POST /api/{user_id}/chat endpoint working
✅ **MCP Server**: All 5 tools executing correctly
✅ **Agent**: OpenAI integration responding with natural language
✅ **Frontend**: ChatBot component displays messages and accepts input
✅ **Tests**: Unit, integration, and E2E tests passing
✅ **Documentation**: API and MCP contracts documented
✅ **Performance**: Response times < 2 seconds for all operations
✅ **Security**: JWT authentication enforced on all endpoints
✅ **Deployment**: Successfully deployed to staging environment

---

## 13. Next Steps

1. **Day 1-2**: Database setup + Migration creation
2. **Day 3-4**: MCP server + Agent service implementation
3. **Day 5-6**: Chat endpoint + Frontend component
4. **Day 7**: Testing (unit, integration, E2E)
5. **Day 8**: Polish, optimization, final submission

---

## Resources

- [OpenAI Agents SDK](https://sdk.vercel.ai/)
- [MCP Specification](https://modelcontextprotocol.io/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLModel Docs](https://sqlmodel.tiangolo.com/)
- [Better Auth Docs](https://better-auth.com/)
- [Neon PostgreSQL](https://neon.tech/)
- [ChatKit Components](https://chatkit.ai/)

---

**Status**: ✅ Ready for Implementation
**Points**: 200
**Deadline**: December 21, 2025
