# Phase III: Task Breakdown & Implementation Tasks

**Version**: 1.0.0
**Status**: Ready for Development
**Total Tasks**: 45 (organized in 5 epic groups)
**Estimated Duration**: 8 days
**Points**: 200 points

---

## Project Location & File Paths

**All file paths in this document are relative to**:
- **Project Root**: `/mnt/e/Hackathons-Panaversity/Hackathon-ii/MA-TODO/`
- **Backend Root**: `phase-2/backend/` OR `phase-3/backend/` (choose one structure)
- **Frontend Root**: `phase-2/frontend/` OR `phase-3/frontend/` (choose one structure)

**Examples**:
- `backend/src/models/conversation.py` = `/mnt/e/Hackathons-Panaversity/Hackathon-ii/MA-TODO/phase-2/backend/src/models/conversation.py`
  OR
  `/mnt/e/Hackathons-Panaversity/Hackathon-ii/MA-TODO/phase-3/backend/src/models/conversation.py`

- `frontend/src/components/ChatBot.tsx` = `/mnt/e/Hackathons-Panaversity/Hackathon-ii/MA-TODO/phase-2/frontend/src/components/ChatBot.tsx`
  OR
  `/mnt/e/Hackathons-Panaversity/Hackathon-ii/MA-TODO/phase-3/frontend/src/components/ChatBot.tsx`

**Recommendation**: Extend Phase II structure (use `phase-2/` backend & frontend) for continuity, as Phase II is already fully functional.

---

## Task Organization

Tasks are organized by epic (major functional area) and ordered by dependency. Each task includes:
- **Task ID**: Unique identifier
- **Title**: Clear action-oriented description
- **Type**: Backend/Frontend/DevOps/Testing/Docs
- **Complexity**: Easy/Medium/Hard
- **Estimate**: Story points or time
- **Description**: What needs to be done
- **Acceptance Criteria**: How to know it's complete
- **Dependencies**: What must be done first

---

## Epic 1: Database Infrastructure (Days 1-2, 5 tasks)

### TASK-001: Create Alembic Migration for Conversation Tables
**Type**: Backend/DevOps
**Complexity**: Medium
**Estimate**: 1-2 hours
**Dependencies**: None (Phase II DB complete)

**Description**:
Create Alembic migration script to add `conversations` and `messages` tables to PostgreSQL database.

**Acceptance Criteria**:
- [ ] Migration file created at `backend/alembic/versions/003_add_conversation_tables.py`
- [ ] Migration creates `conversations` table with columns: id (UUID pk), user_id (UUID fk), title (nullable), created_at (ts), updated_at (ts)
- [ ] Migration creates `messages` table with columns: id (UUID pk), conversation_id (UUID fk), user_id (UUID fk), role (string), content (text), tool_calls (JSONB), created_at (ts)
- [ ] Indexes created: conversations (user_id, created_at), messages (conversation_id, user_id, created_at)
- [ ] Foreign keys properly constrained
- [ ] Migration applies successfully: `uv run alembic upgrade head`
- [ ] Tables verified in database

**Definition of Done**:
```sql
SELECT * FROM conversations LIMIT 1;  -- Verify table exists
SELECT * FROM messages LIMIT 1;       -- Verify table exists
\d conversations                       -- Verify columns
\d messages                            -- Verify columns
```

---

### TASK-002: Define SQLModel Conversation Models
**Type**: Backend
**Complexity**: Easy
**Estimate**: 1-2 hours
**Dependencies**: TASK-001

**Description**:
Create SQLModel models for Conversation and Message entities in `backend/src/models/conversation.py`.

**Acceptance Criteria**:
- [ ] File created at `backend/src/models/conversation.py`
- [ ] `Conversation` model defined with: id, user_id, title, created_at, updated_at
- [ ] `Message` model defined with: id, conversation_id, user_id, role, content, tool_calls, created_at
- [ ] Proper type hints (UUID, datetime, str, dict)
- [ ] Relationships defined: Conversation.messages
- [ ] Models follow Phase II conventions (SQLModel, table=True)
- [ ] Models can be imported: `from src.models.conversation import Conversation, Message`
- [ ] Unit test verifies model instantiation
- [ ] Unit test verifies table structure matches migration

**Example Model Structure**:
```python
class Conversation(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    title: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    messages: list["Message"] = Relationship(back_populates="conversation")
```

---

### TASK-003: Create Database Access Layer (Query Functions)
**Type**: Backend
**Complexity**: Medium
**Estimate**: 2-3 hours
**Dependencies**: TASK-002

**Description**:
Implement database access functions in `backend/src/db/conversation_queries.py`.

**Acceptance Criteria**:
- [ ] File created at `backend/src/db/conversation_queries.py`
- [ ] Function: `get_or_create_conversation(session, user_id, conversation_id)` - Get or create conversation
- [ ] Function: `fetch_message_history(session, conversation_id, limit=1000)` - Fetch messages with pagination
- [ ] Function: `store_message(session, conversation_id, user_id, role, content, tool_calls)` - Store message
- [ ] Function: `list_conversations(session, user_id, limit=10)` - List user's conversations
- [ ] Function: `delete_old_messages(session, retention_days=90)` - Cleanup old messages
- [ ] All functions have proper type hints
- [ ] All functions have docstrings
- [ ] All queries execute in < 100ms (test with 1000 message conversation)
- [ ] Foreign key constraints enforced (authorization: can only access own conversations)
- [ ] Unit tests verify all functions (5+ tests)

**Example Function Signature**:
```python
async def get_or_create_conversation(
    session: AsyncSession,
    user_id: UUID,
    conversation_id: UUID | None = None
) -> Conversation:
    """Get existing conversation or create new one."""
```

---

### TASK-004: Create Unit Tests for Models & Queries
**Type**: Testing/Backend
**Complexity**: Medium
**Estimate**: 2 hours
**Dependencies**: TASK-001, TASK-002, TASK-003

**Description**:
Create comprehensive unit tests for conversation models and database access layer.

**Acceptance Criteria**:
- [ ] Test file created: `backend/tests/unit/test_conversation_models.py`
- [ ] Test file created: `backend/tests/unit/test_conversation_queries.py`
- [ ] 10+ unit tests total
- [ ] Tests cover: model instantiation, model validation, table structure
- [ ] Tests cover: get_or_create, fetch_history, store_message, list, delete
- [ ] Tests cover: authorization (can't access other user's conversations)
- [ ] Tests cover: edge cases (empty history, very long history, invalid IDs)
- [ ] All tests passing: `uv run pytest backend/tests/unit/test_conversation*`
- [ ] Coverage > 90%

**Example Test**:
```python
async def test_get_or_create_conversation_creates_new():
    async with get_session() as session:
        conv = await get_or_create_conversation(session, user_id, None)
        assert conv.id is not None
        assert conv.user_id == user_id
```

---

### TASK-005: Database Performance Optimization
**Type**: Backend/DevOps
**Complexity**: Medium
**Estimate**: 1-2 hours
**Dependencies**: TASK-004

**Description**:
Optimize database queries and indexes for performance.

**Acceptance Criteria**:
- [ ] Benchmark conversation queries: fetch_message_history with 1000 messages < 100ms
- [ ] Benchmark: store_message < 50ms
- [ ] Benchmark: list_conversations < 100ms
- [ ] Verify indexes are being used: EXPLAIN ANALYZE on queries
- [ ] Add query caching if needed (Redis, optional)
- [ ] Document performance characteristics in README
- [ ] Create benchmark script: `backend/scripts/benchmark_db.py`
- [ ] Performance report: `backend/docs/DATABASE_PERFORMANCE.md`

**Performance Targets**:
- fetch_message_history(1000 messages): < 100ms
- store_message: < 50ms
- list_conversations: < 100ms
- get_or_create_conversation: < 50ms

---

## Epic 2: MCP Tools Service (Days 2-4, 8 tasks)

### TASK-006: Implement add_task Tool
**Type**: Backend
**Complexity**: Medium
**Estimate**: 1-2 hours
**Dependencies**: TASK-005

**Description**:
Implement the `add_task` MCP tool handler with full validation and error handling.

**Acceptance Criteria**:
- [ ] File: `backend/src/services/mcp_service.py` exists with add_task implementation
- [ ] Function: `handle_add_task(user_id, title, description, session, current_user)` implemented
- [ ] Validates title: 1-200 characters
- [ ] Validates description: 0-2000 characters
- [ ] Validates user authorization (user_id == current_user.id)
- [ ] Creates task in database with pending status
- [ ] Returns: {task_id, title, description, status, created_at}
- [ ] Error handling: ValidationError (400), AuthorizationError (403), ServerError (500)
- [ ] Structured logging: timestamp, trace_id, user_id, task_id, duration
- [ ] Execution time < 500ms
- [ ] Unit tests: 5+ tests covering valid input, validation errors, auth errors

**MCP Tool Definition**:
```json
{
  "name": "add_task",
  "description": "Create a new task",
  "parameters": {
    "properties": {
      "user_id": {"type": "string", "format": "uuid"},
      "title": {"type": "string", "minLength": 1, "maxLength": 200},
      "description": {"type": "string", "maxLength": 2000}
    },
    "required": ["user_id", "title"]
  }
}
```

---

### TASK-007: Implement list_tasks Tool
**Type**: Backend
**Complexity**: Medium
**Estimate**: 1-2 hours
**Dependencies**: TASK-006

**Description**:
Implement the `list_tasks` MCP tool handler with status filtering.

**Acceptance Criteria**:
- [ ] Function: `handle_list_tasks(user_id, status, session, current_user)` implemented
- [ ] Status filter: "all", "pending", or "completed"
- [ ] Validates user authorization
- [ ] Returns: array of {task_id, title, description, status, created_at}
- [ ] Default sort: created_at descending (newest first)
- [ ] Handles: empty result, no matching status
- [ ] Error handling: ValidationError, AuthorizationError
- [ ] Execution time < 100ms (even for 1000+ tasks)
- [ ] Structured logging with duration
- [ ] Unit tests: 5+ tests (all status, empty results, auth)

---

### TASK-008: Implement complete_task Tool
**Type**: Backend
**Complexity**: Easy
**Estimate**: 1 hour
**Dependencies**: TASK-007

**Description**:
Implement the `complete_task` MCP tool handler.

**Acceptance Criteria**:
- [ ] Function: `handle_complete_task(user_id, task_id, session, current_user)` implemented
- [ ] Validates task exists and belongs to user
- [ ] Validates task not already completed
- [ ] Updates task status to "completed", updates updated_at
- [ ] Returns: {task_id, title, status, updated_at}
- [ ] Error handling: NotFoundError (404), InvalidStateError (409), AuthorizationError (403)
- [ ] Execution time < 200ms
- [ ] Unit tests: 4+ tests (success, already completed, not found, auth)

---

### TASK-009: Implement delete_task Tool
**Type**: Backend
**Complexity**: Easy
**Estimate**: 1 hour
**Dependencies**: TASK-008

**Description**:
Implement the `delete_task` MCP tool handler (agent must request confirmation first).

**Acceptance Criteria**:
- [ ] Function: `handle_delete_task(user_id, task_id, session, current_user)` implemented
- [ ] Validates task exists and belongs to user
- [ ] Deletes task from database (no soft delete, hard delete)
- [ ] Returns: {task_id, title, status: "deleted"}
- [ ] Error handling: NotFoundError, AuthorizationError
- [ ] Note in documentation: Agent should request confirmation before invoking
- [ ] Execution time < 200ms
- [ ] Unit tests: 3+ tests (success, not found, auth)

---

### TASK-010: Implement update_task Tool
**Type**: Backend
**Complexity**: Medium
**Estimate**: 1-2 hours
**Dependencies**: TASK-009

**Description**:
Implement the `update_task` MCP tool handler for updating title/description.

**Acceptance Criteria**:
- [ ] Function: `handle_update_task(user_id, task_id, title, description, session, current_user)` implemented
- [ ] Validates at least one field (title or description) provided
- [ ] Validates title: 1-200 chars (if provided)
- [ ] Validates description: 0-2000 chars (if provided)
- [ ] Updates task, sets updated_at
- [ ] Returns: {task_id, title, description, updated_at}
- [ ] Error handling: NotFoundError, ValidationError, AuthorizationError
- [ ] Execution time < 200ms
- [ ] Unit tests: 5+ tests (update title only, description only, both, validation, auth)

---

### TASK-011: Create MCP Tool Schemas & Registration
**Type**: Backend
**Complexity**: Medium
**Estimate**: 2 hours
**Dependencies**: TASK-010

**Description**:
Create MCP tool schema definitions and factory function to register all 5 tools.

**Acceptance Criteria**:
- [ ] File: `backend/src/services/mcp_tools_schemas.py` with JSON schema definitions
- [ ] Function: `create_mcp_tools(session: AsyncSession)` returns list of MCP Tool objects
- [ ] All 5 tools registered with proper schemas (see mcp-tools-spec.md)
- [ ] Schemas include: name, description, parameters (JSON Schema), returns, errors
- [ ] Tools can be passed to OpenAI Agents SDK: `client.agents.run(tools=mcp_tools)`
- [ ] Docstrings document each tool's behavior
- [ ] Unit tests verify schema validity

**Example Registration**:
```python
async def create_mcp_tools(session: AsyncSession) -> list[Tool]:
    tools = [
        Tool(
            name="add_task",
            description="Create a new task",
            parameters=ADD_TASK_SCHEMA,
            handler=lambda params: handle_add_task(**params, session=session)
        ),
        # ... other tools
    ]
    return tools
```

---

### TASK-012: Unit Test MCP Tools (50%+ Coverage)
**Type**: Testing/Backend
**Complexity**: Medium
**Estimate**: 2-3 hours
**Dependencies**: TASK-011

**Description**:
Create comprehensive unit tests for all MCP tools covering success paths, validation errors, authorization, and edge cases.

**Acceptance Criteria**:
- [ ] Test file: `backend/tests/unit/test_mcp_tools.py`
- [ ] 25+ unit tests total (5 per tool)
- [ ] Tests for each tool:
  - [ ] Valid input, successful execution
  - [ ] Invalid input (validation errors)
  - [ ] Authorization failure (user_id mismatch)
  - [ ] Resource not found (if applicable)
  - [ ] Edge cases (empty strings, maximum lengths)
- [ ] All tests passing: `uv run pytest backend/tests/unit/test_mcp_tools.py`
- [ ] Coverage > 90%
- [ ] Mock database for unit tests (don't use real DB)

---

## Epic 3: Agent Service (Days 3-4, 6 tasks)

### TASK-013: Create Agent Service with OpenAI Agents SDK
**Type**: Backend
**Complexity**: Hard
**Estimate**: 3-4 hours
**Dependencies**: TASK-012

**Description**:
Implement `AgentService` class that initializes and runs the OpenAI Agents SDK with MCP tools.

**Acceptance Criteria**:
- [ ] File: `backend/src/services/agent_service.py` created
- [ ] Class: `AgentService` with `__init__` method:
  - [ ] Initializes OpenAI Agents SDK client
  - [ ] Sets model to "gpt-4-turbo"
  - [ ] Sets temperature to 0.7
  - [ ] Sets max_tokens to 4096
- [ ] Method: `run_agent(messages, mcp_tools, user_context)` async:
  - [ ] Accepts conversation message history
  - [ ] Invokes OpenAI Agents SDK with MCP tools
  - [ ] Returns AgentResponse {response_text, tool_calls}
  - [ ] Handles OpenAI API errors gracefully
  - [ ] Logs with trace_id, user_id, duration
  - [ ] Execution time < 3 seconds (including LLM)
- [ ] System prompt defined (see agent-spec.md)
- [ ] Error handling: API failures, token limits, timeouts
- [ ] Unit tests with mocked OpenAI API

**Example Structure**:
```python
class AgentService:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "gpt-4-turbo"
        self.temperature = 0.7

    async def run_agent(self, messages, mcp_tools, user_context):
        # Initialize agent, run loop, return response
        pass
```

---

### TASK-014: Implement Agent System Prompt
**Type**: Backend
**Complexity**: Easy
**Estimate**: 1 hour
**Dependencies**: TASK-013

**Description**:
Define and test the agent system prompt that governs chatbot behavior.

**Acceptance Criteria**:
- [ ] System prompt defined (see agent-spec.md for reference)
- [ ] Prompt includes: role description, available tools, guidelines
- [ ] Prompt instructs agent on: intent recognition, tool selection, confirmations, error handling
- [ ] Prompt is configurable (loaded from env or config)
- [ ] Documented in: `backend/docs/AGENT_SYSTEM_PROMPT.md`
- [ ] Test with 5+ sample user inputs to verify behavior

**System Prompt Example**:
```
You are a helpful todo assistant. You can:
1. Add tasks: "Add a task to..."
2. List tasks: "Show me tasks"
3. Complete tasks: "Mark done"
4. Delete tasks: "Delete task" (requires confirmation)
5. Update tasks: "Change task..."

Guidelines:
- Be conversational and friendly
- Ask clarifying questions if needed
- For destructive ops, always confirm first
- Never expose technical errors
```

---

### TASK-015: Implement Intent Detection (Fallback)
**Type**: Backend
**Complexity**: Medium
**Estimate**: 1-2 hours
**Dependencies**: TASK-014

**Description**:
Implement fallback intent detection if OpenAI Agents SDK doesn't clearly identify intent.

**Acceptance Criteria**:
- [ ] Class: `IntentDetector` in agent_service.py
- [ ] Method: `detect_intent(user_input)` returns intent name
- [ ] Supported intents: add_task, list_tasks, complete_task, delete_task, update_task, unknown
- [ ] Keyword-based detection for primary intents
- [ ] Handles ambiguous input gracefully
- [ ] Used for clarification requests when needed
- [ ] Unit tests: 10+ test cases

**Example**:
```python
class IntentDetector:
    def detect_intent(self, user_input: str) -> str:
        if "delete" in user_input.lower():
            return "delete_task"
        # ... other intents
        return "unknown"
```

---

### TASK-016: Implement Confirmation Flow for Destructive Operations
**Type**: Backend
**Complexity**: Medium
**Estimate**: 2 hours
**Dependencies**: TASK-015

**Description**:
Implement confirmation flow that requires user approval before delete/update operations.

**Acceptance Criteria**:
- [ ] Class: `ConfirmationFlow` in agent_service.py
- [ ] Method: `confirm_delete_task(task_id, task_details, user_input)` async
- [ ] Method: `confirm_update_task(task_id, task_details, new_values)` async
- [ ] Delete confirmation: ask "Are you sure?" with task name
- [ ] Update confirmation: show what changed (lighter confirmation)
- [ ] Process confirmation response: "yes", "y", "confirm" → proceed; "no", "n", "cancel" → decline
- [ ] Ambiguous response: ask for clarification ("Please say yes or no")
- [ ] Agent blocks tool invocation until confirmation received
- [ ] Test with 5+ confirmation scenarios

**Example Flow**:
```
User: "Delete task 1"
Agent: "Are you sure you want to delete 'Buy groceries'?"
User: "yes"
Agent: [Invokes delete_task, confirms deletion]
```

---

### TASK-017: Implement Pronoun Resolution for Context Awareness
**Type**: Backend
**Complexity**: Hard
**Estimate**: 2-3 hours
**Dependencies**: TASK-016

**Description**:
Implement pronoun resolution that allows users to refer to previous messages using "it", "that", "this", and ordinal references ("first", "last").

**Acceptance Criteria**:
- [ ] Class: `PronounResolver` in agent_service.py
- [ ] Method: `resolve_pronoun(user_input, context, recent_tasks)` returns task_id or None
- [ ] Handles pronouns: "it", "that", "this", "the one"
- [ ] Handles ordinals: "first", "second", "last", "previous"
- [ ] Looks at last 5-10 messages for context
- [ ] Returns task_id if resolved, None otherwise
- [ ] Unit tests: 10+ test cases (pronouns, ordinals, ambiguous)
- [ ] Integration tests: multi-turn conversation with pronoun resolution

**Example**:
```
Message 1: Create 'Call mom'
Message 2: "Mark it complete"  → resolve "it" → "Call mom" task_id
Message 3: "Delete the first task"  → resolve "the first" → task at index 0
```

---

### TASK-018: Unit Tests for Agent Service
**Type**: Testing/Backend
**Complexity**: Medium
**Estimate**: 2-3 hours
**Dependencies**: TASK-017

**Description**:
Create comprehensive unit tests for agent service with mocked OpenAI API.

**Acceptance Criteria**:
- [ ] Test file: `backend/tests/unit/test_agent_service.py`
- [ ] Mock OpenAI Agents SDK responses (don't call real API in tests)
- [ ] Test: agent initializes with correct config
- [ ] Test: agent runs successfully and returns response
- [ ] Test: agent invokes correct MCP tools
- [ ] Test: error handling (API failure, timeout, invalid response)
- [ ] Test: system prompt is used
- [ ] Test: trace_id is generated and logged
- [ ] 15+ unit tests
- [ ] All tests passing
- [ ] Coverage > 85%

---

## Epic 4: Chat Endpoint & Integration (Days 4-5, 8 tasks)

### TASK-019: Create Chat Endpoint Request/Response Models
**Type**: Backend
**Complexity**: Easy
**Estimate**: 1 hour
**Dependencies**: TASK-003

**Description**:
Define Pydantic models for chat endpoint request and response.

**Acceptance Criteria**:
- [ ] File: `backend/src/api/chat.py` created with models
- [ ] Model: `ChatRequest` with fields: conversation_id (UUID, optional), message (str, non-empty, <5000 chars)
- [ ] Model: `ToolCall` with fields: name, parameters, result
- [ ] Model: `ChatResponse` with fields: conversation_id, message_id, response, tool_calls, timestamp
- [ ] Models have proper docstrings and field descriptions
- [ ] Models validate input (non-empty message, max length)
- [ ] Models have examples for documentation
- [ ] Unit tests verify validation (valid input, invalid input)

**Example**:
```python
class ChatRequest(BaseModel):
    conversation_id: UUID | None = None
    message: str = Field(..., min_length=1, max_length=5000)

class ChatResponse(BaseModel):
    conversation_id: UUID
    message_id: UUID
    response: str
    tool_calls: list[ToolCall]
    timestamp: datetime
```

---

### TASK-020: Create Chat Endpoint (POST /api/{user_id}/chat)
**Type**: Backend
**Complexity**: Hard
**Estimate**: 3-4 hours
**Dependencies**: TASK-019, TASK-013

**Description**:
Implement the main chat endpoint that orchestrates the conversation flow.

**Acceptance Criteria**:
- [ ] Endpoint: `POST /api/{user_id}/chat` created
- [ ] Step 1: Validate request (user_id matches authenticated user, message valid)
- [ ] Step 2: Get or create conversation (use database layer)
- [ ] Step 3: Fetch message history (max 1000 messages)
- [ ] Step 4: Store user message
- [ ] Step 5: Invoke agent with MCP tools
- [ ] Step 6: Store assistant message
- [ ] Step 7: Return ChatResponse
- [ ] Authorization: Verify user_id == authenticated user
- [ ] Rate limiting: 60 messages/minute per user
- [ ] Error handling:
  - [ ] 400: Invalid request (empty message, message too long)
  - [ ] 403: Authorization error (user_id mismatch)
  - [ ] 404: Conversation not found
  - [ ] 429: Rate limit exceeded (with Retry-After header)
  - [ ] 500: Server error
- [ ] Response time < 200ms (excluding LLM latency, which adds ~1-2 seconds)
- [ ] Structured logging with trace_id
- [ ] Integration tests: 8+ tests

**Endpoint Code Structure**:
```python
@app.post("/api/{user_id}/chat")
async def chat_endpoint(
    user_id: UUID,
    request: ChatRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    rate_limiter: RateLimiter = Depends(get_rate_limiter),
) -> ChatResponse:
    # Validate, get/create conversation, fetch history, store user msg,
    # run agent, store assistant msg, return response
```

---

### TASK-021: Implement Rate Limiting for Chat Endpoint
**Type**: Backend
**Complexity**: Medium
**Estimate**: 2 hours
**Dependencies**: TASK-020

**Description**:
Implement rate limiting to prevent abuse (60 messages/min per user, 1000/hour per IP).

**Acceptance Criteria**:
- [ ] Use FastAPI SlowAPI or similar library for rate limiting
- [ ] Per-user limit: 60 messages/minute (keyed by user_id)
- [ ] Per-IP limit: 1000 messages/hour (keyed by client IP)
- [ ] Returns 429 status with Retry-After header
- [ ] Error message: "Rate limit exceeded. Please try again in X seconds."
- [ ] Rate limit info available in response headers
- [ ] Redis backend for distributed rate limiting (optional, local storage for now)
- [ ] Unit tests: 5+ tests (limits, retry-after, multiple users)
- [ ] Load test: verify limits work under load

**Example**:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/{user_id}/chat")
@limiter.limit("60/minute")  # Per IP
@limiter.limit("1000/hour")
async def chat_endpoint(...):
    # Implementation
```

---

### TASK-022: Implement Structured Logging
**Type**: Backend
**Complexity**: Medium
**Estimate**: 2-3 hours
**Dependencies**: TASK-020

**Description**:
Implement structured JSON logging throughout the chat flow for observability.

**Acceptance Criteria**:
- [ ] File: `backend/src/logging/structured_logger.py` created
- [ ] All logs in JSON format: {timestamp, trace_id, user_id, conversation_id, component, action, duration_ms, success, level, message}
- [ ] Trace ID generated per request and passed through all operations
- [ ] Logging points:
  - [ ] Chat endpoint: request received, conversation fetched/created, user message stored
  - [ ] Agent service: agent initialization, agent start/end, tool invocations
  - [ ] MCP tools: tool start/end, authorization checks, data mutations
  - [ ] Error logging: all errors with full context
- [ ] Performance: logging adds < 5ms per operation
- [ ] Structured logger can output to stdout (development) and files/cloud (production)
- [ ] Test: 5+ logging scenarios verified

**Log Entry Example**:
```json
{
  "timestamp": "2025-12-13T14:30:45.123Z",
  "trace_id": "abc123",
  "user_id": "uuid",
  "conversation_id": "uuid",
  "component": "agent",
  "action": "tool_invoked",
  "tool_name": "add_task",
  "duration_ms": 145,
  "success": true,
  "level": "INFO"
}
```

---

### TASK-023: Create Integration Tests for Chat Endpoint
**Type**: Testing/Backend
**Complexity**: Hard
**Estimate**: 3-4 hours
**Dependencies**: TASK-022

**Description**:
Create comprehensive integration tests that test the full chat flow end-to-end.

**Acceptance Criteria**:
- [ ] Test file: `backend/tests/integration/test_chat_endpoint.py`
- [ ] Test: Full flow: add task → list → complete
- [ ] Test: Multi-turn context: create task → "mark it complete" (pronoun resolution)
- [ ] Test: Delete confirmation: delete requires user confirmation
- [ ] Test: Error handling: invalid input, auth errors, rate limit
- [ ] Test: Message persistence: messages stored in database
- [ ] Test: Conversation persistence: conversation ID maintained
- [ ] 10+ integration tests
- [ ] Mock or use test OpenAI API (don't use real API in tests)
- [ ] All tests passing
- [ ] Coverage > 80%

**Example Test**:
```python
async def test_full_chat_flow_add_list_complete():
    # 1. Send message to add task
    response1 = await client.post(f"/api/{user_id}/chat", ...)
    conv_id = response1.json()["conversation_id"]

    # 2. Send message to list tasks
    response2 = await client.post(f"/api/{user_id}/chat", ...)

    # 3. Send message to complete task
    response3 = await client.post(f"/api/{user_id}/chat", ...)

    # Verify flow
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response3.status_code == 200
```

---

### TASK-024: Create API Documentation (OpenAPI/Swagger)
**Type**: Docs/Backend
**Complexity**: Easy
**Estimate**: 1-2 hours
**Dependencies**: TASK-020

**Description**:
Document the chat endpoint in OpenAPI/Swagger format with examples.

**Acceptance Criteria**:
- [ ] OpenAPI schema generated automatically by FastAPI
- [ ] Endpoint documented with: description, parameters, request/response examples
- [ ] Request schema documented: ChatRequest with field descriptions
- [ ] Response schema documented: ChatResponse with field descriptions
- [ ] Error responses documented: 400, 403, 404, 429, 500 with examples
- [ ] Examples provided:
  - [ ] Successful add_task request/response
  - [ ] Successful list_tasks request/response
  - [ ] Rate limit error (429) response
  - [ ] Authorization error (403) response
- [ ] Swagger UI accessible at `/docs`
- [ ] ReDoc documentation accessible at `/redoc`
- [ ] Documentation markdown file: `backend/docs/CHAT_API.md`

---

### TASK-025: Integration Test: Rate Limiting
**Type**: Testing/Backend
**Complexity**: Medium
**Estimate**: 1-2 hours
**Dependencies**: TASK-021

**Description**:
Test rate limiting works correctly under normal and stress conditions.

**Acceptance Criteria**:
- [ ] Test: Send 60 messages in rapid succession → 60 succeed, 61st blocked
- [ ] Test: Verify Retry-After header in 429 response
- [ ] Test: Rate limits reset after time window
- [ ] Test: Multiple users have independent limits
- [ ] Test: Per-IP limits work correctly
- [ ] 5+ rate limiting tests
- [ ] All passing
- [ ] Load test: 100 concurrent users, verify limits enforced

---

## Epic 5: Frontend Implementation (Days 3-6, 10 tasks)

### TASK-026: Create Chat API Client
**Type**: Frontend
**Complexity**: Medium
**Estimate**: 2-3 hours
**Dependencies**: TASK-020 (chat endpoint stable)

**Description**:
Implement TypeScript API client for chat endpoint in `frontend/src/lib/chatApi.ts`.

**Acceptance Criteria**:
- [ ] File: `frontend/src/lib/chatApi.ts` created
- [ ] Function: `sendMessage(userId, conversationId, message)` sends POST request
- [ ] Function: `createConversation(userId)` creates new conversation
- [ ] Function: `fetchConversationHistory(userId, conversationId, limit)` fetches messages
- [ ] Function: `listConversations(userId)` lists user's conversations
- [ ] Type definitions: ChatRequest, ChatResponse, ToolCall, Message, Conversation
- [ ] Error handling: ValidationError, NotFoundError, RateLimitError, ServerError
- [ ] Retry logic: exponential backoff (3 retries, max 5 second wait)
- [ ] Timeout: 30 second max per request
- [ ] Rate limit awareness: detect 429, display "try again later"
- [ ] Unit tests: 10+ tests with mocked API responses

**Example**:
```typescript
export async function sendMessage(
  userId: string,
  conversationId: string,
  message: string
): Promise<ChatResponse> {
  // Validate, send request, handle errors
  try {
    const response = await fetch(`/api/${userId}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ conversation_id: conversationId, message }),
    });
    if (!response.ok) {
      if (response.status === 429) throw new RateLimitError(...);
      // ... other error handling
    }
    return response.json();
  } catch (error) {
    // Retry logic
  }
}
```

---

### TASK-027: Create ChatBot React Component
**Type**: Frontend
**Complexity**: Hard
**Estimate**: 4-5 hours
**Dependencies**: TASK-026

**Description**:
Implement the main ChatBot React component with message display, input, and state management.

**Acceptance Criteria**:
- [ ] Component: `frontend/src/components/ChatBot.tsx` created
- [ ] Props: `conversationId` (optional), `onConversationChange` (callback)
- [ ] State: messages, input, loading, error, currentConversationId
- [ ] Display:
  - [ ] Message list with scrolling to latest message
  - [ ] User messages: right-aligned, blue background
  - [ ] Assistant messages: left-aligned, gray background
  - [ ] Loading spinner during request
  - [ ] Error message display (red box with message)
- [ ] Input:
  - [ ] Text input field for user message
  - [ ] Send button
  - [ ] Enter key to send message
  - [ ] Disable send while loading
  - [ ] Clear input after send
- [ ] Features:
  - [ ] Auto-create conversation on first message
  - [ ] Load conversation history on mount (if conversationId provided)
  - [ ] Display tool calls and results (optional, for transparency)
  - [ ] Mobile responsive (full-width on mobile)
- [ ] Styling:
  - [ ] Use Tailwind CSS 4+
  - [ ] Professional look, consistent with Phase II design
  - [ ] Dark mode support (optional, defer if time-constrained)
- [ ] Unit tests: 8+ tests
  - [ ] Component renders
  - [ ] Message sending
  - [ ] Message display
  - [ ] Error handling
  - [ ] Loading state
- [ ] Component Stories (Storybook, optional)

**Component Structure**:
```typescript
export function ChatBot({ conversationId, onConversationChange }: ChatBotProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentConversationId, setCurrentConversationId] = useState(conversationId);

  const handleSendMessage = async (text: string) => {
    // Send message, handle response, update state
  };

  return (
    <div className="chatbot-container">
      {/* Messages list, input field, send button */}
    </div>
  );
}
```

---

### TASK-028: Create Chatbot Page (Next.js)
**Type**: Frontend
**Complexity**: Easy
**Estimate**: 1-2 hours
**Dependencies**: TASK-027

**Description**:
Create the chatbot page at `/chatbot` using Next.js App Router.

**Acceptance Criteria**:
- [ ] File: `frontend/src/app/chatbot/page.tsx` created
- [ ] Page renders ChatBot component
- [ ] Page title: "Todo Assistant" or similar
- [ ] Page description/subtitle
- [ ] Layout: professional header + ChatBot component
- [ ] Responsive: works on mobile, tablet, desktop
- [ ] Navigation: link to tasks page, home page (optional)
- [ ] Authentication: redirect to login if not authenticated
- [ ] Styling: consistent with Phase II design system

**Example Page**:
```typescript
export default function ChatbotPage() {
  const [conversationId, setConversationId] = useState<string>();

  return (
    <div className="chatbot-page">
      <header className="page-header">
        <h1>Todo Assistant</h1>
        <p>Chat with your AI-powered assistant</p>
      </header>
      <ChatBot
        conversationId={conversationId}
        onConversationChange={setConversationId}
      />
    </div>
  );
}
```

---

### TASK-029: Create Chat API Client Types & Tests
**Type**: Frontend/Testing
**Complexity**: Medium
**Estimate**: 1-2 hours
**Dependencies**: TASK-026

**Description**:
Define TypeScript types for chat API and create comprehensive unit tests.

**Acceptance Criteria**:
- [ ] File: `frontend/src/types/chat.ts` with type definitions
- [ ] Types: ChatRequest, ChatResponse, Message, ToolCall, Conversation
- [ ] Types have proper JSDoc comments
- [ ] Export types from lib/chatApi.ts
- [ ] Test file: `frontend/tests/unit/chatApi.test.ts`
- [ ] 10+ unit tests:
  - [ ] sendMessage successful request
  - [ ] sendMessage with retry on network error
  - [ ] sendMessage rate limit error
  - [ ] sendMessage validation error
  - [ ] createConversation
  - [ ] fetchConversationHistory
  - [ ] listConversations
  - [ ] Timeout handling
  - [ ] Error types
- [ ] Mock fetch using jest or vitest
- [ ] All tests passing
- [ ] Coverage > 90%

---

### TASK-030: Create ChatBot Component Tests
**Type**: Frontend/Testing
**Complexity**: Medium
**Estimate**: 2-3 hours
**Dependencies**: TASK-027

**Description**:
Create comprehensive unit tests for ChatBot component using React Testing Library.

**Acceptance Criteria**:
- [ ] Test file: `frontend/tests/unit/ChatBot.test.tsx`
- [ ] 10+ tests covering:
  - [ ] Component renders without crashing
  - [ ] Displays initial message (if provided)
  - [ ] Sends message on button click
  - [ ] Sends message on Enter key
  - [ ] Updates messages on response
  - [ ] Shows loading state during request
  - [ ] Shows error message on API error
  - [ ] Disables send button while loading
  - [ ] Clears input after send
  - [ ] Handles empty message (doesn't send)
- [ ] Use React Testing Library best practices
- [ ] Mock chatApi functions
- [ ] All tests passing
- [ ] Coverage > 85%

**Example Test**:
```typescript
test("sends message and displays response", async () => {
  const { getByPlaceholderText, getByRole, getByText } = render(<ChatBot />);
  const input = getByPlaceholderText("Type your message...");
  const button = getByRole("button", { name: /send/i });

  fireEvent.change(input, { target: { value: "Add task" } });
  fireEvent.click(button);

  await waitFor(() => {
    expect(getByText(/response text/)).toBeInTheDocument();
  });
});
```

---

### TASK-031: Create E2E Tests for Chatbot
**Type**: Frontend/Testing
**Complexity**: Hard
**Estimate**: 3-4 hours
**Dependencies**: TASK-028

**Description**:
Create end-to-end tests using Playwright that test real chatbot interactions.

**Acceptance Criteria**:
- [ ] Test file: `frontend/tests/e2e/chatbot.spec.ts`
- [ ] 8+ E2E tests covering:
  - [ ] Open chatbot page
  - [ ] Send first message
  - [ ] Add task via natural language
  - [ ] List tasks
  - [ ] Complete task
  - [ ] Delete task with confirmation
  - [ ] Error handling (invalid input)
  - [ ] Mobile view responsive
- [ ] Use Playwright best practices
- [ ] Tests use real backend (or mock with MSW)
- [ ] All tests passing in CI/CD
- [ ] Tests run in headless and headed modes

**Example E2E Test**:
```typescript
test("user can chat with assistant and complete task", async ({ page }) => {
  await page.goto("/chatbot");

  // Send message to add task
  await page.fill("[data-testid='chat-input']", "Add task: buy milk");
  await page.click("[data-testid='send-button']");
  await page.waitForSelector("[data-testid='assistant-message']");

  // Verify response
  const response = page.locator("[data-testid='assistant-message']").last();
  await expect(response).toContainText("created");

  // Complete task
  await page.fill("[data-testid='chat-input']", "Mark it complete");
  await page.click("[data-testid='send-button']");

  await expect(page.locator("[data-testid='assistant-message']")).toContainText("complete");
});
```

---

### TASK-032: Frontend Integration Tests
**Type**: Frontend/Testing
**Complexity**: Medium
**Estimate**: 2 hours
**Dependencies**: TASK-031

**Description**:
Create integration tests that verify frontend and backend work together.

**Acceptance Criteria**:
- [ ] Test file: `frontend/tests/integration/chatbot.test.ts`
- [ ] 5+ integration tests:
  - [ ] Full flow with real backend
  - [ ] Multi-turn conversation
  - [ ] Conversation persistence
  - [ ] Rate limiting display
  - [ ] Error recovery
- [ ] Use test database (if applicable)
- [ ] Mock only external services (OpenAI API)
- [ ] All tests passing
- [ ] Coverage of integration points

---

## Epic 6: Testing & Quality Assurance (Days 6-8, 8 tasks)

### TASK-033: Create Performance Benchmarks
**Type**: Testing/DevOps
**Complexity**: Medium
**Estimate**: 2-3 hours
**Dependencies**: TASK-025

**Description**:
Create performance benchmarks and tests to verify response times meet targets.

**Acceptance Criteria**:
- [ ] Benchmark script: `backend/scripts/benchmark_chat.py`
- [ ] Measures:
  - [ ] Chat response time (including LLM)
  - [ ] Tool execution time (individual tools)
  - [ ] Database query time
  - [ ] Message history fetch time
- [ ] Targets:
  - [ ] Chat response: < 3 seconds (p95)
  - [ ] Tool execution: < 500ms per tool
  - [ ] Database query: < 100ms
  - [ ] Message history (1000 msg): < 100ms
- [ ] Load test: 100 concurrent users
- [ ] Results documented in: `backend/docs/PERFORMANCE.md`
- [ ] Performance dashboard (optional, Grafana/DataDog)

**Benchmark Script Example**:
```python
import time
import statistics

times = []
for i in range(10):
    start = time.time()
    response = send_chat_message(...)
    times.append(time.time() - start)

p95 = statistics.quantiles(times, n=20)[18]  # 95th percentile
print(f"p95 response time: {p95:.2f}s")
assert p95 < 3.0, "Response time exceeds target"
```

---

### TASK-034: Load Testing (100 Concurrent Users)
**Type**: Testing/DevOps
**Complexity**: Medium
**Estimate**: 2 hours
**Dependencies**: TASK-025

**Description**:
Perform load testing with 100 concurrent users to verify system stability.

**Acceptance Criteria**:
- [ ] Load test script: `backend/scripts/load_test.py` (using k6 or locust)
- [ ] Scenarios:
  - [ ] 100 concurrent users sending messages
  - [ ] Ramp-up: 10 users/second
  - [ ] Duration: 5 minutes
  - [ ] Mix: 40% add task, 30% list, 20% complete, 10% delete
- [ ] Success criteria:
  - [ ] 95% of requests succeed (< 5% errors)
  - [ ] p95 response time < 5 seconds
  - [ ] No database connection pool exhaustion
  - [ ] Rate limiting working correctly
- [ ] Load test report: `backend/docs/LOAD_TEST_RESULTS.md`
- [ ] Identify bottlenecks and document improvements

---

### TASK-035: Security Review & Hardening
**Type**: Backend/Security
**Complexity**: Medium
**Estimate**: 2-3 hours
**Dependencies**: TASK-024

**Description**:
Review security implementation and harden the application.

**Acceptance Criteria**:
- [ ] Security checklist:
  - [ ] All endpoints require authentication (JWT)
  - [ ] Authorization checks prevent cross-user access
  - [ ] Input validation prevents XSS, injection
  - [ ] SQL injection prevention (use parameterized queries)
  - [ ] Rate limiting prevents abuse
  - [ ] No hardcoded secrets in code
  - [ ] Sensitive data not logged (passwords, API keys)
  - [ ] HTTPS enforced (in production)
  - [ ] CORS configured correctly
  - [ ] No debug mode in production
- [ ] Run security scanners:
  - [ ] `bandit` for Python vulnerabilities
  - [ ] `safety` for dependency vulnerabilities
  - [ ] Manual code review
- [ ] Security documentation: `backend/docs/SECURITY.md`
- [ ] All issues resolved before deployment

**Bandit Check**:
```bash
bandit -r backend/src/ -ll  # Low severity threshold
```

---

### TASK-036: Code Quality & Linting
**Type**: Backend/Frontend
**Complexity**: Easy
**Estimate**: 1-2 hours
**Dependencies**: All code tasks

**Description**:
Ensure code quality meets standards with linting, formatting, and type checking.

**Acceptance Criteria**:
- [ ] Backend:
  - [ ] `ruff check backend/` passes (no style issues)
  - [ ] `mypy backend/` passes (no type errors)
  - [ ] `isort` formatting correct
- [ ] Frontend:
  - [ ] `eslint` passes (no linting issues)
  - [ ] `prettier` formatting correct
  - [ ] `tsc --noEmit` passes (no type errors)
- [ ] Pre-commit hooks installed and working
- [ ] CI/CD pipeline includes linting checks
- [ ] All issues fixed or documented

**Commands**:
```bash
cd backend && ruff check . && mypy . && ruff format .
cd ../frontend && eslint . && prettier --check . && tsc --noEmit
```

---

### TASK-037: Test Coverage & CI/CD Setup
**Type**: DevOps/Testing
**Complexity**: Medium
**Estimate**: 2-3 hours
**Dependencies**: All test tasks

**Description**:
Ensure test coverage meets targets and CI/CD pipeline is configured.

**Acceptance Criteria**:
- [ ] Backend test coverage > 80%
  - [ ] `uv run pytest --cov=src backend/tests/`
  - [ ] Coverage report: `backend/htmlcov/index.html`
- [ ] Frontend test coverage > 85%
  - [ ] `npm test -- --coverage frontend/`
  - [ ] Coverage report visible in terminal
- [ ] CI/CD pipeline (GitHub Actions):
  - [ ] Linting: `ruff check`, `eslint`
  - [ ] Type checking: `mypy`, `tsc`
  - [ ] Tests: `pytest`, `npm test`
  - [ ] Coverage: `pytest --cov`
  - [ ] Security: `bandit`, `safety`
  - [ ] Runs on PR and push to main
  - [ ] Must pass before merging
- [ ] Coverage badges in README
- [ ] Coverage report accessible online (codecov.io, optional)

**Coverage Commands**:
```bash
# Backend
uv run pytest --cov=src --cov-report=html backend/tests/

# Frontend
npm test -- --coverage
```

---

### TASK-038: Documentation & Developer Guides
**Type**: Docs
**Complexity**: Easy
**Estimate**: 2-3 hours
**Dependencies**: All implementation tasks

**Description**:
Create comprehensive documentation for developers, API users, and operators.

**Acceptance Criteria**:
- [ ] API Documentation:
  - [ ] `backend/docs/CHAT_API.md` - Chat endpoint specification
  - [ ] OpenAPI schema available at `/docs`
  - [ ] Examples for all endpoints
- [ ] Architecture Documentation:
  - [ ] `backend/docs/ARCHITECTURE.md` - System design overview
  - [ ] Data flow diagrams
  - [ ] Deployment architecture
- [ ] Developer Guides:
  - [ ] `backend/chatbot/CLAUDE.md` - Developer guidance for Phase III
  - [ ] `frontend/chatbot/CLAUDE.md` - Frontend developer guide
  - [ ] Testing guide: `backend/docs/TESTING.md`
- [ ] Operational Guides:
  - [ ] `backend/docs/DEPLOYMENT.md` - How to deploy
  - [ ] `backend/docs/TROUBLESHOOTING.md` - Common issues and fixes
  - [ ] `backend/docs/MONITORING.md` - Observability setup
- [ ] README updates:
  - [ ] Phase III section in root README.md
  - [ ] Update backend/README.md with new endpoints
  - [ ] Update frontend/README.md with new components

**Documentation Structure**:
```
backend/docs/
├── CHAT_API.md
├── ARCHITECTURE.md
├── TESTING.md
├── DEPLOYMENT.md
├── TROUBLESHOOTING.md
├── MONITORING.md
├── PERFORMANCE.md
├── SECURITY.md
└── DATABASE_PERFORMANCE.md

backend/chatbot/
├── CLAUDE.md
└── README.md

frontend/chatbot/
├── CLAUDE.md
└── README.md
```

---

### TASK-039: Final QA & Bug Fixes
**Type**: Testing/QA
**Complexity**: Easy
**Estimate**: 1-2 hours
**Dependencies**: TASK-038

**Description**:
Final quality assurance round, bug fixes, and polish before submission.

**Acceptance Criteria**:
- [ ] Manual testing:
  - [ ] Chat works end-to-end
  - [ ] All 5 tools work correctly
  - [ ] Confirmation flows work
  - [ ] Error messages are helpful
  - [ ] Mobile view works
- [ ] Bug fixes:
  - [ ] All known bugs documented and fixed
  - [ ] No console errors or warnings
  - [ ] No unhandled promise rejections
- [ ] Edge case testing:
  - [ ] Very long input (5000 chars)
  - [ ] Very long conversation (1000 messages)
  - [ ] Rapid message sending
  - [ ] Network failures
- [ ] Final checklist:
  - [ ] All tests passing
  - [ ] All documentation complete
  - [ ] All code commented/documented
  - [ ] Environment variables configured
  - [ ] Database migrations applied
  - [ ] Ready for deployment

---

### TASK-040: Prepare Submission Materials
**Type**: Docs/Admin
**Complexity**: Easy
**Estimate**: 1 hour
**Dependencies**: TASK-039

**Description**:
Prepare submission materials for hackathon (video demo, README, etc).

**Acceptance Criteria**:
- [ ] Demo video (3-5 minutes):
  - [ ] Show chat interface loading
  - [ ] Add task via natural language
  - [ ] List tasks
  - [ ] Complete task
  - [ ] Delete task with confirmation
  - [ ] Show multi-turn conversation
  - [ ] Show error handling
- [ ] README updates:
  - [ ] Phase III feature description
  - [ ] Screenshots of chatbot
  - [ ] How to run Phase III
  - [ ] Architecture overview
  - [ ] Points earned (200)
- [ ] Submission checklist:
  - [ ] Code committed to git
  - [ ] All tests passing in CI/CD
  - [ ] README complete
  - [ ] Demo video uploaded (if required)
  - [ ] Documentation complete
  - [ ] No hardcoded secrets

---

## Task Dependencies & Critical Path

```
TASK-001 (Migration)
  ↓
TASK-002 (Models)
  ↓
TASK-003 (Queries)
  ↓ TASK-004 (DB Tests)
TASK-005 (Performance)
  ↓
TASK-006-010 (MCP Tools)
  ↓ TASK-012 (Tools Tests)
TASK-013-017 (Agent)
  ↓ TASK-018 (Agent Tests)
TASK-019-022 (Chat Endpoint)
  ↓ TASK-023 (Integration Tests)
TASK-024-025 (API Docs & Rate Limiting)

TASK-026 (Chat API Client)
  ↓
TASK-027 (ChatBot Component)
  ↓ TASK-029-030 (Tests)
TASK-028 (Chatbot Page)
  ↓ TASK-031-032 (E2E Tests)

TASK-033-039 (Testing & Polish)
  ↓
TASK-040 (Submission)
```

---

## Success Criteria Summary

### Functional Requirements
- [x] Chat interface responds to natural language
- [x] All 5 MCP tools working (add, list, complete, delete, update)
- [x] Multi-turn conversation with context awareness
- [x] Confirmation flows for destructive operations
- [x] Error handling with user-friendly messages
- [x] Conversation persistence in database
- [x] Rate limiting (60 msg/min per user)

### Quality Requirements
- [x] 100+ tests (unit, integration, E2E)
- [x] 80%+ code coverage
- [x] All linting checks passing
- [x] No type errors
- [x] Security review passed

### Performance Requirements
- [x] Chat response time < 3 seconds (p95)
- [x] Tool execution < 500ms
- [x] Load test: 100 concurrent users
- [x] Message history fetch < 100ms

### Documentation Requirements
- [x] API documentation complete
- [x] Architecture documented
- [x] Developer guides created
- [x] Deployment guide provided
- [x] Troubleshooting guide provided

---

## Task Completion Tracking

**Total Tasks**: 40
**Status**: Ready for Development

| Task ID | Task Name | Status | Assigned To | Due Date |
|---------|-----------|--------|------------|----------|
| TASK-001 | Migration | Ready | Backend | Day 1 |
| TASK-002 | Models | Ready | Backend | Day 1 |
| ... | ... | Ready | ... | ... |
| TASK-040 | Submission | Ready | Team | Day 8 |

---

**Last Updated**: 2025-12-13
**Next**: Begin implementation of tasks in priority order (TASK-001 first)
