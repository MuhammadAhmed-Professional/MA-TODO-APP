<!--
Sync Impact Report (Phase III Constitution):
- Version: 3.0.0 (MAJOR - Introduces AI/Chatbot Architecture)
- Base: Evolved from Phase II 2.0.0 constitution
- Reason: Adding AI-native capabilities, MCP server architecture, stateless chatbot patterns, OpenAI integration
- Modified Principles:
  - I. Spec-Driven Development: Added MCP tool specifications and Agent behavior specs
  - III. Test-First Development: Added Agent behavior testing, MCP tool mock testing
  - V. Multi-Interface Excellence: Expanded to include ChatKit UI (web-based chat interface)
  - VI. Modern Technology Stack: Added OpenAI Agents SDK, Official MCP SDK, ChatKit framework
  - VII. Monorepo Organization: Added Phase III (chatbot) directory structure under frontend/
  - VIII. Full-Stack Architecture: Evolved to include MCP server architecture, Agent subsystem
- New Principles:
  - XIII. AI Agent Architecture: Defines OpenAI Agents SDK patterns, tool invocation, context management
  - XIV. MCP Server Design: Stateless tool design, database-backed state persistence, schema validation
  - XV. Conversation State Management: Stateless endpoints with database persistence, message history retrieval
  - XVI. Natural Language Understanding: Agent behavior specification, command disambiguation, confirmation flows
  - XVII. Error Handling & Resilience: Tool failure recovery, rate limiting, graceful degradation
  - XVIII. Observability for AI Systems: Logging tool invocations, tracking agent decisions, debugging traces
- Added Sections:
  - Phase III Technology Stack (ChatKit, Agents SDK, MCP SDK)
  - Chatbot Deployment Strategy
  - AI System Governance (Agent constraints, tool safety, output validation)
- Templates Requiring Updates:
  - spec-template.md: Add MCP tool specification section
  - plan-template.md: Add AI/Agent/MCP planning sections
  - tasks-template.md: Add Agent behavior task categories
- Follow-up TODOs:
  - Create frontend/chatbot/CLAUDE.md with ChatKit and Agent patterns
  - Define MCP tool templates in .claude/skills/
  - Document Agent behavior testing strategies
  - Create monitoring/observability spec for chatbot operations
-->

# Phase III Constitution: AI-Powered Todo Chatbot
## Evolution of Todo - Spec-Driven AI Development

**Project**: Hackathon II Phase III - AI-Powered Todo Chatbot
**Version**: 3.0.0
**Ratified**: 2025-12-13
**Last Amended**: 2025-12-13
**Base Constitution**: Phase II 2.0.0 (Full Stack Web Application)

---

## Overview

Phase III extends the Phase II full-stack todo application with AI-native capabilities. This phase introduces:

- **AI-Powered Conversation Interface**: OpenAI ChatKit UI component for natural language interaction
- **Stateless Chat Architecture**: FastAPI endpoint that maintains conversation state in database
- **MCP Tool Server**: Official MCP SDK server exposing task operations as standardized tools
- **OpenAI Agents SDK Integration**: Autonomous agent that interprets natural language and invokes MCP tools
- **Stateless Scalability**: Any backend instance can handle any request (no in-memory state)

**Key Principle**: All AI systems MUST be deterministic, testable, and observable. Natural language is a specification format; agent decisions must be traceable to tool outputs.

---

## Core Principles (Phase III Extensions)

### XIII. AI Agent Architecture (NEW)
All AI agent implementations MUST use OpenAI Agents SDK following strict patterns:

**Agent Design Pattern**:
```
User Input (Chat Message)
    ↓
Fetch Conversation History (Database)
    ↓
Build Message Array (System Prompt + History + New Message)
    ↓
Initialize Agent with MCP Tools
    ↓
Agent.run() with Message Array
    ↓
Agent Evaluates Tools (LLM Decision)
    ↓
Tool Invocation (via MCP Server)
    ↓
Tool Result Processing
    ↓
Agent Generates Response (with Tool Summary)
    ↓
Store User Message in Database
    ↓
Store Agent Response in Database
    ↓
Return Response to Client
```

**Agent Initialization** (FastAPI endpoint):
```python
from openai import OpenAI

agent = openai.agents.Agent(
    model="gpt-4-turbo",
    tools=mcp_tools,  # Tools from MCP server
    system_prompt="You are a helpful todo assistant...",
    temperature=0.7,
    max_iterations=10,  # Prevent infinite loops
)
```

**Agent Behavior Requirements**:
- **Tool Selection**: Agent MUST choose appropriate MCP tool for user intent
- **Parameter Extraction**: Agent MUST extract parameters from natural language accurately
- **Confirmation**: Agent MUST confirm actions before destructive operations (delete, clear all)
- **Error Recovery**: If tool fails, agent MUST explain error and suggest alternative
- **Conversation Context**: Agent MUST use full message history when relevant
- **Token Management**: Agent MUST be aware of context window limits

**System Prompt** (defines agent behavior):
```
You are a helpful todo assistant. Your role is to:
1. Help users manage their todo lists through natural conversation
2. Execute task operations (add, delete, update, complete) via available tools
3. Provide summaries and insights about user's tasks
4. Confirm destructive operations (delete, complete all)

Available Tools:
- add_task: Create a new task
- list_tasks: Retrieve tasks with optional filters
- complete_task: Mark a task as done
- delete_task: Remove a task from the list
- update_task: Modify task details

Behavior:
- Always confirm before deleting tasks
- Use friendly, conversational language
- Provide context when executing tools ("I found 5 pending tasks...")
- If user intent is unclear, ask clarifying questions
- Never make assumptions about user's intent
```

**Rationale**: OpenAI Agents SDK provides reliable, well-tested agent loop. Stateless pattern enables horizontal scaling. Message history ensures context awareness across requests.

### XIV. MCP Server Design (NEW)
MCP (Model Context Protocol) server MUST expose task operations as standardized tools:

**MCP Server Architecture**:
```
Client (Agent)
    ↓
HTTP/JSON-RPC (Protocol)
    ↓
MCP Server (FastAPI)
    ├── Tool: add_task
    ├── Tool: list_tasks
    ├── Tool: complete_task
    ├── Tool: delete_task
    └── Tool: update_task
    ↓
Database (Neon PostgreSQL)
```

**Tool Specifications** (JSON Schema):
```json
{
  "name": "add_task",
  "description": "Create a new task for the user",
  "inputSchema": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "description": "User's unique identifier"
      },
      "title": {
        "type": "string",
        "description": "Task title (1-200 characters)",
        "minLength": 1,
        "maxLength": 200
      },
      "description": {
        "type": "string",
        "description": "Optional task description (max 2000 characters)",
        "maxLength": 2000
      }
    },
    "required": ["user_id", "title"]
  }
}
```

**Tool Implementation Requirements**:
- **Stateless**: No in-memory state; all state persisted to database
- **Idempotent**: Same input → same output (safe to retry)
- **Validated**: Input validation per JSON Schema
- **Authorized**: User ID extraction and ownership verification
- **Transactional**: Database operations wrapped in transactions
- **Logged**: All tool invocations logged with user_id, timestamp, parameters, result
- **Error Handling**: Return structured error objects with `error` and `message` fields

**Tool Return Format** (standardized):
```json
{
  "success": true,
  "task_id": "12345",
  "message": "Task created successfully",
  "data": {
    "id": "12345",
    "title": "Buy groceries",
    "completed": false,
    "created_at": "2025-12-13T10:30:00Z"
  }
}
```

**MCP Server Best Practices**:
- **No Side Effects Outside Database**: Tools MUST NOT make external API calls (except database)
- **Atomic Operations**: Each tool call is a complete transaction
- **Consistent Responses**: Always return standardized JSON structure
- **Tool Composition**: Tools can be composed in agent (e.g., list_tasks → delete_task)
- **Performance**: Tool execution < 500ms (critical for conversational responsiveness)
- **Rate Limiting**: Database-level constraints prevent abuse

**Rationale**: Official MCP SDK provides standardized tool interface. Stateless design enables horizontal scaling. JSON Schema validation ensures type safety at protocol level.

### XV. Conversation State Management (NEW)
Chat endpoints MUST implement stateless, database-backed conversation persistence:

**Database Schema**:
```python
class Conversation(SQLModel, table=True):
    """Chat session container."""
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    # No in-memory state; all state in messages

class Message(SQLModel, table=True):
    """Individual message in conversation."""
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversation.id")
    user_id: UUID = Field(foreign_key="user.id")
    role: str = Field(max_length=10)  # "user" or "assistant"
    content: str = Field(max_length=10000)
    tool_calls: str | None = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Chat Endpoint Flow** (Stateless):
1. **Receive**: POST /api/chat with `{ conversation_id: UUID, message: str }`
2. **Validate**: Verify conversation_id exists and user owns it
3. **Fetch History**: Query all messages for conversation (ordered by creation)
4. **Build Context**: Create message array from history + new message
5. **Store Request**: Insert user message into database (before agent runs)
6. **Run Agent**: Agent.run(messages) with MCP tools
7. **Process Result**: Extract agent response and tool calls
8. **Store Response**: Insert assistant message into database
9. **Return**: Response to client (no state held in memory)
10. **Next Request**: Any server instance can retrieve full history

**Conversation Limits** (prevent abuse):
- Max messages per conversation: 1000
- Message retention: 90 days (then archive)
- Concurrent conversations per user: 10
- Message size limit: 10KB
- Rate limiting: 60 messages/minute per user

**Pagination** (for large conversations):
```python
# Endpoint: GET /api/conversations/{conversation_id}/messages
# Query params: ?limit=50&offset=0
# Returns: { messages: [...], total: 1000, hasMore: true }
```

**Rationale**: Stateless endpoints enable horizontal scaling. Database persistence survives server restarts. Full message history provides context for multi-turn conversations.

### XVI. Natural Language Understanding (NEW)
Agent behavior MUST be deterministic and testable through specified patterns:

**Command Recognition Patterns**:
| User Input | Agent Behavior | Tool(s) Used |
|-----------|----------------|-------------|
| "Add a task to buy milk" | Extract title, create task | `add_task` |
| "Show me my pending tasks" | Filter by incomplete status | `list_tasks(status="pending")` |
| "Mark task 1 as done" | Find task by position/ID, complete | `list_tasks() → complete_task(id=1)` |
| "Delete the meeting task" | Confirm deletion, execute | `list_tasks() → delete_task(id=X)` |
| "What have I completed?" | Filter by complete status | `list_tasks(status="completed")` |
| "Rename task 2 to 'Call mom'" | Update task title | `update_task(id=2, title="Call mom")` |
| "How many tasks do I have?" | Count total/status breakdown | `list_tasks(status="all")` |

**Intent Detection** (handled by LLM):
- Agent uses LLM to parse intent and extract parameters
- Ambiguities resolved through confirmations
- Multi-step operations composed from tools

**Confirmation Protocol** (for destructive operations):
```
User: "Delete all completed tasks"
Agent: "I found 5 completed tasks. Are you sure you want to delete them?
  • Buy groceries (completed 2 days ago)
  • Call mom (completed yesterday)
  • Pay bills (completed today)
  • ...

Reply 'yes' to confirm, or 'no' to cancel."

User: "yes"
Agent: "Deleted 5 tasks. You now have 12 pending tasks remaining."
```

**Natural Language Constraints**:
- **No Hallucination**: Agent responds only with data from database + tool results
- **No Invention**: Agent doesn't create facts not in database
- **Transparent Tools**: Agent explains which tools were used ("I searched your tasks and found...")
- **Error Clarity**: If tool fails, agent explains reason, not just error code
- **Context Awareness**: Agent remembers conversation history for pronouns ("it", "that task", "the one I mentioned")

**Testing Natural Language** (example unit test):
```python
def test_agent_adds_task_with_description():
    agent = initialize_agent(mcp_tools=mock_mcp_tools)
    response = agent.run(
        messages=[
            {"role": "user", "content": "Add a task to study Python for 2 hours"}
        ]
    )
    # Verify tool was called
    assert mock_mcp_tools.add_task.called
    assert mock_mcp_tools.add_task.call_args.user_id == test_user_id
    assert "Python" in mock_mcp_tools.add_task.call_args.title
    # Verify response acknowledges action
    assert "task" in response.lower() and "added" in response.lower()
```

**Rationale**: LLM-based intent parsing is flexible but must be validated. Confirmations prevent user regrets. Tool usage transparency builds user trust in AI decisions.

### XVII. Error Handling & Resilience (NEW)
Chatbot MUST gracefully handle failures and maintain user trust:

**Tool Failure Handling**:
```python
try:
    result = mcp_tool.execute(params)
except MCP_ToolError as e:
    # Log for debugging
    logger.error(f"Tool {tool_name} failed: {e}")

    # Inform user clearly
    agent_response = f"I had trouble {e.user_message}. " \
                     f"Please try again or rephrase your request."

    # Store failure in database for analysis
    db.store_error_event(
        user_id=user_id,
        tool_name=tool_name,
        error_type=e.type,
        timestamp=datetime.utcnow()
    )
```

**Rate Limiting** (prevent abuse):
- Per-user: 60 messages/minute
- Per-IP: 1000 messages/hour
- Concurrent requests: Max 5 per user
- Response: 429 Too Many Requests with `Retry-After` header

**Graceful Degradation**:
- If MCP server slow: Extend timeout, show "thinking..." indicator
- If database connection lost: Return cached results if available
- If LLM rate limited: Queue message, process when available
- If conversation lost: Offer to start fresh or recover from backup

**Error Categories**:
1. **User Error** (client's fault): "I couldn't understand that. Try 'add a task to...'
2. **Tool Error** (MCP tool failed): "I couldn't access your tasks. Please try again."
3. **System Error** (server down): "I'm having technical difficulties. Please try again in a few moments."

**Monitoring for Resilience**:
- Track tool success/failure rates
- Alert on error spikes (> 5% failure rate)
- Log all errors with full context (user_id, conversation_id, attempt #)
- Regular dead-letter queue cleanup (failed messages after 3 attempts)

**Rationale**: Users trust systems that fail gracefully. Rate limiting protects backend. Error logging enables post-incident analysis.

### XVIII. Observability for AI Systems (NEW)
All AI operations MUST be observable through logging and tracing:

**Logging Requirements**:
```python
import logging

logger = logging.getLogger(__name__)

# Log agent initialization
logger.info(f"Agent initialized for user {user_id}", extra={
    "user_id": user_id,
    "model": "gpt-4-turbo",
    "temperature": 0.7,
})

# Log message received
logger.info(f"Message received in conversation {conversation_id}", extra={
    "conversation_id": conversation_id,
    "message_length": len(message),
    "message_preview": message[:100],
})

# Log tool invocation
logger.info(f"Tool {tool_name} invoked", extra={
    "tool_name": tool_name,
    "parameters": {k: v for k, v in params.items() if k != "password"},
    "timestamp": datetime.utcnow().isoformat(),
})

# Log tool result
logger.info(f"Tool {tool_name} succeeded", extra={
    "tool_name": tool_name,
    "duration_ms": elapsed,
    "result_size": len(str(result)),
})

# Log agent decision
logger.info(f"Agent generated response", extra={
    "conversation_id": conversation_id,
    "tools_used": [t.name for t in tool_calls],
    "response_length": len(response),
})
```

**Structured Logging Format** (JSON):
```json
{
  "timestamp": "2025-12-13T10:30:00.000Z",
  "level": "INFO",
  "message": "Tool add_task invoked",
  "trace_id": "abc123...",
  "user_id": "user123",
  "conversation_id": "conv456",
  "tool_name": "add_task",
  "duration_ms": 145,
  "success": true
}
```

**Metrics to Track**:
1. **Agent Health**:
   - Messages processed per minute
   - Average response time (p50, p95, p99)
   - Tool success rate (%)
   - Tool usage distribution (which tools most used)

2. **Error Tracking**:
   - Tool failures by type
   - LLM API errors
   - Database timeouts
   - User input decode errors

3. **User Behavior**:
   - Messages per user per day (average)
   - Active users (daily, weekly, monthly)
   - Conversation length distribution
   - Most common intents (by tool usage)

**Debugging Traces**:
```python
# Full conversation trace for debugging
trace = {
    "conversation_id": "conv456",
    "timestamp": "2025-12-13T10:30:00Z",
    "user_message": "Add a task to buy milk",
    "message_history": [
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."},
    ],
    "agent_decision": {
        "tool_name": "add_task",
        "parameters": {"title": "Buy milk", "description": None},
        "reasoning": "User wants to create a new task",
    },
    "tool_result": {
        "success": True,
        "task_id": "task789",
        "data": {...},
    },
    "agent_response": "I've added 'Buy milk' to your task list.",
    "duration_ms": 342,
}
```

**Rationale**: Observability enables debugging, monitoring, and optimization. Structured logs enable automated alerts. Traces support post-incident analysis and continuous improvement.

---

## Technology Stack (Phase III)

### Frontend (ChatKit UI)
- **Framework**: OpenAI ChatKit (web component)
- **Integration**: Next.js 16+ component
- **Features**: Message history, typing indicators, error states
- **Location**: `frontend/src/components/ChatBot.tsx`

### Backend (OpenAI + MCP)
- **Framework**: FastAPI (from Phase II)
- **Agent Engine**: OpenAI Agents SDK
- **MCP Server**: Official MCP SDK
- **Database**: Neon PostgreSQL (from Phase II)
- **Message Broker**: Optional Kafka (Phase V)

### AI Models
- **LLM**: GPT-4-turbo (or latest available)
- **Embeddings**: OpenAI embeddings (for future semantic search)
- **Temperature**: 0.7 (balanced between creative + deterministic)

### Monitoring
- **Logging**: Structured JSON logs to stdout/file
- **Metrics**: Prometheus format (optional)
- **Tracing**: OpenTelemetry (optional)
- **Dashboard**: Grafana (optional)

---

## Monorepo Structure (Actual)

```
/mnt/e/Hackathons-Panaversity/Hackathon-ii/MA-TODO/    # Project root
├── phase-1/                          # Phase I: CLI Console App (COMPLETED)
│   ├── src/todo_app/
│   │   ├── main.py                   # CLI entry point
│   │   ├── models.py                 # Data models (Task)
│   │   ├── storage.py                # In-memory storage
│   │   ├── operations.py             # CRUD operations
│   │   ├── ui.py                     # Menu UI
│   │   └── banner.py                 # CLI banner
│   └── tests/                        # 87 passing tests, 77% coverage
│
├── phase-2/                          # Phase II: Full-Stack Web App (COMPLETED)
│   ├── frontend/                     # Next.js 16+ React 19+ TypeScript
│   │   ├── app/                      # Next.js App Router pages
│   │   │   ├── (auth)/login/
│   │   │   ├── (auth)/signup/
│   │   │   ├── (dashboard)/dashboard/
│   │   │   ├── (dashboard)/dashboard/tasks/
│   │   │   └── layout.tsx
│   │   ├── components/
│   │   │   ├── auth/
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   ├── SignupForm.tsx
│   │   │   │   └── SessionExpirationWarning.tsx
│   │   │   ├── tasks/
│   │   │   │   ├── TaskList.tsx
│   │   │   │   ├── TaskCard.tsx
│   │   │   │   └── TaskForm.tsx
│   │   │   └── layout/
│   │   │       ├── Header.tsx
│   │   │       └── Sidebar.tsx
│   │   ├── lib/
│   │   │   └── api/ (auth, tasks client)
│   │   ├── types/
│   │   │   ├── api.ts
│   │   │   ├── task.ts
│   │   │   └── user.ts
│   │   ├── tests/
│   │   │   ├── e2e/ (Playwright)
│   │   │   └── unit/ (Vitest)
│   │   ├── middleware.ts
│   │   └── CLAUDE.md
│   │
│   ├── backend/                      # FastAPI 0.110+ Python 3.13+ SQLModel
│   │   ├── src/
│   │   │   ├── main.py               # FastAPI app entry
│   │   │   ├── api/
│   │   │   │   ├── auth.py           # Auth endpoints (Better Auth)
│   │   │   │   ├── tasks.py          # Task CRUD endpoints
│   │   │   │   └── health.py         # Health check
│   │   │   ├── services/
│   │   │   │   ├── auth_service.py   # JWT token management
│   │   │   │   └── task_service.py   # Task business logic
│   │   │   ├── models/
│   │   │   │   ├── user.py           # User SQLModel
│   │   │   │   └── task.py           # Task SQLModel
│   │   │   ├── auth/
│   │   │   │   ├── jwt.py            # JWT utilities
│   │   │   │   └── dependencies.py   # Auth dependencies
│   │   │   └── db/
│   │   │       ├── session.py        # Database session
│   │   │       └── migrations/       # Alembic migrations
│   │   ├── tests/
│   │   │   ├── unit/
│   │   │   │   ├── test_auth.py
│   │   │   │   └── test_task_service.py
│   │   │   └── integration/
│   │   │       ├── test_auth_api.py
│   │   │       ├── test_authorization.py
│   │   │       └── test_tasks_api.py
│   │   └── CLAUDE.md
│   │
│   ├── auth-server/                  # Better Auth integration (Optional)
│   │   ├── src/
│   │   │   ├── server.ts
│   │   │   ├── auth.ts
│   │   │   ├── db.ts
│   │   │   └── migrate.ts
│   │   └── package.json
│   │
│   └── README.md
│
├── phase-3/                          # Phase III: AI-Powered Chatbot (SPECS CREATED)
│   └── README.md
│
├── phase-4/                          # Phase IV: Kubernetes Deployment (PLANNED)
│   └── README.md
│
├── phase-5/                          # Phase V: Cloud Deployment (PLANNED)
│   └── README.md
│
├── specs/                            # Specification documents
│   └── features/
│       ├── console-todo-app/        # Phase I specs
│       ├── web-todo-app/            # Phase II specs
│       ├── phase-3-chatbot/         # Phase III specs (NEW)
│       │   ├── CONSTITUTION.md      # v3.0.0 governance
│       │   ├── spec.md              # Feature specification
│       │   ├── agent-spec.md        # Agent behavior patterns
│       │   ├── mcp-tools-spec.md    # MCP tool specifications
│       │   ├── plan.md              # Implementation plan
│       │   └── tasks.md             # Granular tasks
│       └── ...other features...
│
├── history/                         # Development history & artifacts
│   ├── adr/                         # Architecture Decision Records
│   │   ├── 0001-in-memory-storage-phase-i.md
│   │   ├── 0002-uv-package-manager.md
│   │   ├── 0003-next-js-app-router.md
│   │   ├── 0004-fastapi-sqlmodel.md
│   │   ├── 0005-neon-serverless-postgresql.md
│   │   ├── 0006-jwt-httponly-cookies.md
│   │   ├── 0007-monorepo-phase-organization.md
│   │   └── README.md
│   │
│   └── prompts/                     # Prompt History Records (PHRs)
│       ├── constitution/
│       ├── console-todo-app/
│       ├── web-todo-app/
│       ├── phase-3-chatbot/
│       │   └── 001-phase-3-specifications.spec.prompt.md
│       └── general/
│
├── .specify/                        # Spec-Kit Plus infrastructure
│   ├── memory/
│   │   └── constitution.md          # v2.0.0 (Phase II base)
│   ├── templates/
│   │   ├── spec-template.md
│   │   ├── plan-template.md
│   │   ├── tasks-template.md
│   │   ├── adr-template.md
│   │   └── phr-template.prompt.md
│   └── scripts/bash/
│       ├── create-new-feature.sh
│       ├── setup-plan.sh
│       ├── create-phr.sh
│       ├── create-adr.sh
│       └── validate-migration.sh
│
├── .claude/                         # Claude Code configuration
│   ├── agents/                      # Specialized subagents
│   │   ├── auth-better-auth.md
│   │   ├── cloud-blueprint-generator.md
│   │   ├── project-structure-architect.md
│   │   ├── rag-chatbot-architect.md
│   │   └── ...12 more agents...
│   │
│   ├── commands/                    # Slash commands
│   │   ├── sp.specify.md
│   │   ├── sp.plan.md
│   │   ├── sp.implement.md
│   │   ├── sp.tasks.md
│   │   ├── sp.analyze.md
│   │   ├── sp.adr.md
│   │   └── ...more commands...
│   │
│   └── skills/                      # Reusable capabilities
│       ├── python-tdd-implementation.md
│       ├── create-fastapi-endpoint.md
│       ├── create-react-component.md
│       ├── generate-database-migration.md
│       └── ...more skills...
│
├── docs/                            # Documentation
│   └── neon-setup.md
│
├── shared/                          # Shared utilities
│   ├── types/
│   │   └── README.md
│   └── utils/
│       └── README.md
│
├── CLAUDE.md                        # Root-level instructions (THIS FILE)
├── README.md                        # Project overview
├── pyproject.toml                   # Python project config
├── .gitignore
├── .python-version
└── .git/                            # Git repository (initialized Dec 13)
```

### Project Layout Summary

**Root Directory**: `/mnt/e/Hackathons-Panaversity/Hackathon-ii/MA-TODO/`

**Three Active Phases**:
1. **phase-1/** - Complete CLI app with 87 tests (77% coverage)
2. **phase-2/** - Complete full-stack web app (frontend + backend + auth-server)
3. **phase-3/** - Ready for chatbot implementation (specs complete)

**Three Placeholder Phases**:
- **phase-4/** - Kubernetes deployment (future)
- **phase-5/** - Cloud deployment (future)

**Core Directories**:
- **specs/** - Feature specifications (by feature name, not phase)
- **history/** - ADRs and Prompt History Records
- **.specify/** - Spec-Kit Plus templates and scripts
- **.claude/** - Claude Code configuration (agents, commands, skills)

---

## API Contracts (Phase III)

### Chat Endpoint
```
POST /api/{user_id}/chat
Content-Type: application/json

Request:
{
  "conversation_id": "uuid" | null,  # null = create new conversation
  "message": "string"                 # User's message
}

Response (200 OK):
{
  "conversation_id": "uuid",
  "message_id": "uuid",
  "response": "string",               # Agent's response
  "tool_calls": [
    {
      "name": "add_task",
      "parameters": {...},
      "result": {...}
    }
  ],
  "timestamp": "2025-12-13T10:30:00Z"
}

Error Response (400/500):
{
  "error": "error_code",
  "message": "User-friendly error message"
}
```

### MCP Tool Examples
See detailed specifications in `specs/features/phase-3-chatbot/mcp-tools-spec.md`

---

## Development Workflow (Phase III)

**Feature: Add Natural Language Support for Task Priorities**

1. **Specify**:
   - Create agent behavior spec: "Agent should understand priority keywords (high, low, urgent)"
   - Create tool spec: `update_task` with `priority` field
   - Create acceptance criteria: Test cases for various phrasings

2. **Implement**:
   - Update MCP tool schema to include priority
   - Update SQLModel Task model with priority field
   - Generate Alembic migration
   - Update system prompt to mention priority support

3. **Test**:
   - Unit test: Agent parses "high priority" → priority="high"
   - Integration test: Agent invokes update_task with priority
   - E2E test: User says "make this urgent" → task updates

4. **Deploy**:
   - Database migration applied
   - New system prompt deployed
   - Agent tested with sample conversations

---

## Testing Strategy (Phase III)

### Unit Tests
- **Agent Logic**: Mock MCP tools, test intent parsing
- **Tool Implementations**: Test with in-memory database
- **Message Storage**: Test conversation history retrieval
- **Error Handling**: Test failure scenarios (missing params, auth errors)

### Integration Tests
- **Chat Endpoint**: Full request/response cycle
- **Agent + Tools**: Real MCP server with test database
- **Message History**: Multi-turn conversations

### E2E Tests (Playwright)
- **Full Conversation**: User opens chat, types message, sees response
- **Multi-Turn**: User asks multiple related questions
- **Tool Execution**: Verify task created in database

### Agent Behavior Tests
```python
def test_agent_lists_pending_tasks():
    """Agent should call list_tasks when asked for pending items."""
    agent = initialize_agent(mcp_tools=mock_mcp_tools)
    agent.run(messages=[
        {"role": "user", "content": "Show me my pending tasks"}
    ])

    assert mock_mcp_tools.list_tasks.called
    call_args = mock_mcp_tools.list_tasks.call_args
    assert call_args.status == "pending"

def test_agent_confirms_delete():
    """Agent should ask for confirmation before deleting."""
    agent = initialize_agent(mcp_tools=mock_mcp_tools)
    response = agent.run(messages=[
        {"role": "user", "content": "Delete all my tasks"}
    ])

    # Should ask for confirmation, not delete immediately
    assert "confirm" in response.lower() or "sure" in response.lower()
    assert not mock_mcp_tools.delete_task.called
```

---

## Governance (Phase III Extensions)

### Amendment Process (Enhanced)
1. Documented rationale with impact on AI system behavior
2. Agent behavior change testing (before/after)
3. Version increment (follows semantic versioning)
4. Update this constitution with new version

### Compliance (Extended)
- All agent decisions MUST be traceable to tool outputs
- All natural language processing MUST be testable
- All tool invocations MUST be logged
- All errors MUST be handled gracefully

### Quality Gates (for AI features)
- ✅ Agent behavior tests pass (intent parsing, tool selection)
- ✅ Tool invocation logs show expected calls
- ✅ Error handling prevents system crashes
- ✅ Conversation history persists across requests
- ✅ Rate limiting prevents abuse

---

## Success Criteria (Phase III)

A successful Phase III implementation demonstrates:

1. **Natural Language Interface**
   - Users can manage tasks through conversation
   - Agent understands task-related commands
   - Responses are helpful and contextual

2. **Reliable Tool Execution**
   - All MCP tools execute correctly
   - Tool failures handled gracefully
   - Task database remains consistent

3. **Persistent Conversations**
   - Conversation history survives server restarts
   - Multi-turn conversations maintain context
   - Users can resume conversations by ID

4. **Scalable Architecture**
   - Stateless endpoints enable horizontal scaling
   - No in-memory state per request
   - Database handles concurrent conversations

5. **Observable Operations**
   - All tool invocations logged
   - Errors tracked and alertable
   - Agent decisions traceable through logs

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 3.0.0 | 2025-12-13 | Initial Phase III constitution (AI Chatbot) |
| 2.0.0 | 2025-12-06 | Phase II constitution (Full-Stack Web App) |
| 1.0.0 | 2025-12-01 | Phase I constitution (CLI Console App) |

---

## References

- **Phase II Constitution**: `/phase-1/.specify/memory/constitution.md`
- **Hackathon Requirements**: `/phase-1/README.md`
- **OpenAI Agents SDK**: https://platform.openai.com/docs/agents
- **MCP Spec**: https://modelcontextprotocol.io/
- **Better Auth**: https://better-auth.com/

---

**This Constitution Governs Phase III Development**

All Phase III implementations MUST comply with these principles. Deviations require explicit justification in specs or ADRs. This constitution supersedes all previous guidance for Phase III scope.
