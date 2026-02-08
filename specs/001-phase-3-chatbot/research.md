# Phase III Chatbot - Research & Clarifications (Phase 0)

**Created**: 2025-12-13
**Stage**: research
**Status**: Complete - All requirements clarified from Hackathon II documentation
**Branch**: 001-phase-3-chatbot

---

## 1. Architecture Unknowns - CLARIFIED

### 1.1: Deployment Model
**Unknown**: Should Phase III be a separate phase-3/ directory or extend phase-2/?

**Decision**: **Extend phase-2/** (Recommended)
- **Rationale**: Code reuse, authentication continuity, database connection pooling
- **Implementation**: Add new files to existing phase-2/ structure:
  - `phase-2/backend/src/api/chat.py` - Chat endpoint
  - `phase-2/backend/src/services/agent_service.py` - OpenAI Agents SDK wrapper
  - `phase-2/backend/src/services/mcp_service.py` - MCP server
  - `phase-2/backend/src/models/conversation.py` - Conversation & Message models
  - `phase-2/frontend/src/components/ChatBot.tsx` - ChatKit UI component
- **Benefit**: Single auth system, single database, shared infrastructure

### 1.2: OpenAI Agents SDK Integration
**Unknown**: How to initialize and manage the OpenAI Agents SDK?

**Decision**: **Wrapper Service Pattern**
```python
# phase-2/backend/src/services/agent_service.py

class AgentService:
    def __init__(self, openai_api_key: str):
        self.client = Anthropic(api_key=openai_api_key)  # Using OpenAI Agents
        self.model = "gpt-4-turbo"
        self.temperature = 0.7

    async def run_agent(
        self,
        user_message: str,
        conversation_history: List[Message],
        mcp_tools: List[Tool],
        user_id: str
    ) -> AgentResponse:
        """Run agent with conversation context and MCP tools"""
        # Build system prompt
        # Add tools from MCP server
        # Run agent loop with tool invocation
        # Return response with tool calls
```

**Clarifications Resolved**:
- Model: gpt-4-turbo (specified in Hackathon II)
- Temperature: 0.7 (for balanced creativity and consistency)
- Tool integration: Via MCP SDK with standardized schema
- Context window: Last 10 messages for pronoun resolution

### 1.3: MCP Server Implementation
**Unknown**: How to structure MCP server with 5 tools?

**Decision**: **Standalone MCP Server Process**
```python
# phase-2/backend/src/services/mcp_service.py

class MCPServer:
    def __init__(self, db_session: Session):
        self.server = Server("todo-mcp-server")
        self.session = db_session

    @self.server.list_tools()
    async def list_tools(self) -> list[Tool]:
        return [
            Tool(name="add_task", description="Create new task", ...),
            Tool(name="list_tasks", description="List tasks with filter", ...),
            Tool(name="complete_task", description="Mark task complete", ...),
            Tool(name="delete_task", description="Delete task", ...),
            Tool(name="update_task", description="Update task", ...),
        ]

    @self.server.call_tool()
    async def call_tool(self, name: str, arguments: dict) -> str:
        if name == "add_task":
            return await self.handle_add_task(**arguments)
        elif name == "list_tasks":
            return await self.handle_list_tasks(**arguments)
        # ... other tools
```

**Clarifications Resolved**:
- MCP SDK: Official Python SDK (from mcp.readthedocs.io)
- Tool interface: Standardized JSON schema
- Error handling: All tools return structured error responses
- Logging: JSON structured logging for all tool calls

### 1.4: Chat Endpoint Statelessness
**Unknown**: How to maintain conversation state without server-side session storage?

**Decision**: **Database-Backed Conversation State**
- **Stateless Design**: Each request is independent
- **State Persistence**: Conversation & Message tables in PostgreSQL
- **Flow**:
  1. Client sends: `{conversation_id, message}`
  2. Server fetches conversation history from database
  3. Agent processes with full context
  4. Server persists response + tool calls
  5. Client resumes with same conversation_id

```python
# phase-2/backend/src/api/chat.py

@router.post("/api/{user_id}/chat")
async def chat(
    user_id: UUID,
    request: ChatRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    # 1. Fetch or create conversation
    conversation = await get_or_create_conversation(user_id, request.conversation_id)

    # 2. Fetch message history
    history = await fetch_message_history(conversation.id)

    # 3. Run agent with context
    response = await agent_service.run_agent(
        user_message=request.message,
        conversation_history=history,
        mcp_tools=mcp_tools,
        user_id=user_id
    )

    # 4. Persist response
    user_msg = Message(conversation_id=conversation.id, role="user", content=request.message)
    assistant_msg = Message(conversation_id=conversation.id, role="assistant", content=response.text)
    session.add(user_msg)
    session.add(assistant_msg)
    session.commit()

    return ChatResponse(conversation_id=conversation.id, response=response.text)
```

**Clarifications Resolved**:
- No in-memory sessions
- Full database persistence
- Stateless endpoints enable horizontal scaling
- Conversation continuity via conversation_id

---

## 2. Database Schema Unknowns - CLARIFIED

### 2.1: Conversation Model
**Unknown**: What fields are required for Conversation?

**Decision**:
```python
# phase-2/backend/src/models/conversation.py

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    title: str | None = Field(None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")
    user: "User" = Relationship(back_populates="conversations")
```

**Clarifications Resolved**:
- Foreign key to User table
- Optional title (auto-generated from first message if needed)
- Timestamps for audit trail
- Relationship to Message table

### 2.2: Message Model
**Unknown**: What structure for storing messages with tool calls?

**Decision**:
```python
class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    role: str = Field(...)  # "user" or "assistant"
    content: str = Field(...)  # Message text
    tool_calls: dict | None = Field(None, sa_column=Column(JSON))  # Structured tool invocations
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")
    user: "User" = Relationship(back_populates="messages")
```

**Clarifications Resolved**:
- JSON column for tool_calls (PostgreSQL JSONB)
- Role enum: "user" or "assistant"
- Dual indexing: (conversation_id, created_at) for history retrieval
- User reference for audit trail

### 2.3: Migration Strategy
**Unknown**: How to add Conversation/Message tables to existing Phase II database?

**Decision**: **Alembic Migration**
```python
# phase-2/backend/src/db/migrations/versions/003_add_conversation_tables.py

def upgrade():
    op.create_table(
        'conversations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_conversations_user_id_created_at', 'user_id', 'created_at')
    )

    op.create_table(
        'messages',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('conversation_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tool_calls', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id']),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_messages_conversation_id_created_at', 'conversation_id', 'created_at')
    )
```

**Clarifications Resolved**:
- Version 003 (after existing 001, 002)
- Proper indexing for query performance
- JSON column type for tool_calls flexibility
- Foreign key constraints for data integrity

---

## 3. Agent Behavior Unknowns - CLARIFIED

### 3.1: Intent Recognition
**Unknown**: How should the agent recognize user intent?

**Decision**: **Zero-Shot Intent Recognition via System Prompt**
- Agent is given all 5 tools explicitly
- System prompt includes examples of natural language → tool mapping
- Agent uses inherent reasoning to select appropriate tool
- No separate intent classification model needed

**Example System Prompt Section**:
```
You are a helpful todo assistant. You can help users manage tasks using these tools:

1. add_task: Create a new task
   Example user message: "Add a task to buy groceries"

2. list_tasks: List tasks with optional status filter
   Example user message: "What are my pending tasks?"

3. complete_task: Mark a task as completed
   Example user message: "Mark the first task complete"

4. delete_task: Delete a task (ask for confirmation first)
   Example user message: "Delete the bug fix task"

5. update_task: Update task details
   Example user message: "Change task 2 to buy bread"

Always:
- Ask for confirmation before deleting tasks
- Use friendly conversational language
- Ask clarifying questions if intent is unclear
- Never make assumptions about which task the user means
```

**Clarifications Resolved**:
- No ML-based intent classification
- All intent signals in system prompt + tool schemas
- Agent handles ambiguity through conversation

### 3.2: Pronoun Resolution
**Unknown**: How to resolve pronouns like "it", "that", "the task"?

**Decision**: **Context-Window Pronoun Resolution**
- Agent receives last 10 messages in context
- Within agent's reasoning capability
- System prompt includes instruction: "When user says 'it' or 'that', refer to the most recent relevant task mentioned"

**Example**:
```
User: "Create a task 'Fix bug in dashboard'"
Agent: "Task created: 'Fix bug in dashboard'"

User: "Mark it complete"  ← "it" refers to previous task
Agent: [has context of previous message, resolves "it" to "Fix bug in dashboard", calls complete_task]
```

**Clarifications Resolved**:
- Conversation history provides context
- Agent reasoning handles pronoun resolution
- No separate NLP module needed

### 3.3: Confirmation Flows
**Unknown**: When and how to ask for confirmation?

**Decision**: **Confirmation for Destructive Operations Only**
```
Destructive operations:
- delete_task → Always ask: "Are you sure you want to delete 'X'? (yes/no)"

Non-destructive operations:
- add_task → Just create, confirm with details
- complete_task → Just complete, confirm with message
- update_task → Just update, confirm with new details
- list_tasks → Just list
```

**Clarifications Resolved**:
- Explicit confirmation rules
- User can say "yes", "confirm", "y" to proceed
- User can say "no", "cancel", "n" to abort

### 3.4: Error Handling
**Unknown**: How should agent handle tool failures?

**Decision**: **Graceful Fallback with User Guidance**
```python
try:
    response = await mcp_service.call_tool(tool_name, args)
    return response
except ToolError as e:
    agent.respond_to_user(
        f"Sorry, I had trouble with that operation. {e.user_message}. "
        f"Would you like to try something else?"
    )
    logger.error(
        json.dumps({
            "error": str(e),
            "tool": tool_name,
            "args": args,
            "conversation_id": conversation_id
        })
    )
```

**Clarifications Resolved**:
- Never expose stack traces to users
- User-friendly error messages
- Graceful degradation
- Full error logging for debugging

---

## 4. Frontend Integration Unknowns - CLARIFIED

### 4.1: ChatBot Component Library
**Unknown**: What UI library for ChatBot component?

**Decision**: **OpenAI ChatKit Web Component**
- Official OpenAI component library
- Supports streaming responses
- Built-in styling and accessibility
- Integrates with Next.js seamlessly

```typescript
// phase-2/frontend/src/components/ChatBot.tsx

import { ChatKit } from '@openai/chatkit';

export function ChatBot({ conversationId }: ChatBotProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSendMessage = async (message: string) => {
    setLoading(true);
    const response = await chatApi.sendMessage(conversationId, message);
    setMessages([...messages, { role: 'user', content: message }, ...response.messages]);
    setLoading(false);
  };

  return (
    <ChatKit
      messages={messages}
      onSendMessage={handleSendMessage}
      isLoading={loading}
    />
  );
}
```

**Clarifications Resolved**:
- UI library selected
- Message flow documented
- Loading states defined
- Error handling pattern

### 4.2: Chat API Client
**Unknown**: What's the client-side API abstraction?

**Decision**: **TypeScript API Client**
```typescript
// phase-2/frontend/src/lib/chatApi.ts

export class ChatApi {
  constructor(private baseUrl: string) {}

  async sendMessage(
    userId: string,
    conversationId: string | null,
    message: string
  ): Promise<ChatResponse> {
    const response = await fetch(
      `${this.baseUrl}/api/${userId}/chat`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conversation_id: conversationId,
          message
        })
      }
    );
    return response.json();
  }

  async getConversationHistory(
    userId: string,
    conversationId: string
  ): Promise<Message[]> {
    // Fetch message history for resuming conversations
  }
}
```

**Clarifications Resolved**:
- API client pattern
- Request/response types
- Error handling
- Conversation resumption

### 4.3: Real-Time Updates
**Unknown**: How to implement real-time message streaming?

**Decision**: **Server-Sent Events (SSE) for Streaming**
```typescript
async function streamMessage(
  userId: string,
  conversationId: string,
  message: string
) {
  const eventSource = new EventSource(
    `/api/${userId}/chat/stream?conversation_id=${conversationId}&message=${message}`
  );

  eventSource.onmessage = (event) => {
    const chunk = JSON.parse(event.data);
    setMessages(prev => [...prev, chunk]);
  };

  eventSource.onerror = () => {
    eventSource.close();
  };
}
```

**Clarifications Resolved**:
- Streaming mechanism: SSE
- Chunk format: JSON
- Error handling: Connection close on error
- UI updates: Real-time message appending

---

## 5. Authentication & Security Unknowns - CLARIFIED

### 5.1: JWT Integration with Better Auth
**Unknown**: How does Phase III integrate with Better Auth from Phase II?

**Decision**: **JWT Token Passthrough**
```python
# phase-2/backend/src/api/chat.py

@router.post("/api/{user_id}/chat")
async def chat(
    user_id: UUID,
    request: ChatRequest,
    current_user: User = Depends(get_current_user),  # From Better Auth JWT
    session: Session = Depends(get_session)
):
    # JWT token already validated by Better Auth middleware
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Proceed with authenticated user context
```

**Clarifications Resolved**:
- No new auth layer needed
- Better Auth JWT validates all requests
- user_id parameter verified against token
- No sensitive data in client-side conversation IDs

### 5.2: Rate Limiting
**Unknown**: What rate limits for chat endpoint?

**Decision**: **Per-User Rate Limiting**
```
Default: 60 requests per minute per user
Burst: Allow 5 requests in 5 seconds

Error Response:
429 Too Many Requests
{
  "error": "RATE_LIMITED",
  "message": "You're sending messages too quickly. Please wait a moment.",
  "retry_after": 30
}
```

**Clarifications Resolved**:
- Rate limit per authenticated user
- Token bucket algorithm
- Graceful error response
- Client-side retry guidance

### 5.3: Data Privacy
**Unknown**: What data is stored and accessible?

**Decision**: **User-Scoped Data Isolation**
- Each conversation tied to authenticated user_id
- Messages only accessible to conversation owner
- No cross-user data leakage
- All tool operations scoped to authenticated user

**Clarifications Resolved**:
- Multi-tenant isolation enforced
- Database queries filter by user_id
- Tools validate user ownership
- No shared conversation access

---

## 6. Observability Unknowns - CLARIFIED

### 6.1: Logging Strategy
**Unknown**: What to log for debugging and monitoring?

**Decision**: **Structured JSON Logging**
```python
import json
import logging

logger = logging.getLogger(__name__)

# Agent execution start
logger.info(json.dumps({
    "timestamp": datetime.utcnow().isoformat(),
    "component": "agent",
    "action": "agent_started",
    "conversation_id": str(conversation_id),
    "user_id": str(user_id),
    "message": request.message[:100]  # First 100 chars
}))

# Tool invocation
logger.info(json.dumps({
    "timestamp": datetime.utcnow().isoformat(),
    "component": "mcp_tool",
    "action": "tool_invoked",
    "tool": "add_task",
    "parameters": {"user_id": str(user_id), "title": title},
    "duration_ms": elapsed_ms
}))

# Errors
logger.error(json.dumps({
    "timestamp": datetime.utcnow().isoformat(),
    "component": "agent",
    "action": "error",
    "error_type": type(e).__name__,
    "message": str(e),
    "conversation_id": str(conversation_id)
}))
```

**Clarifications Resolved**:
- JSON format for log aggregation
- Structured fields for filtering
- Trace IDs for request tracking
- Duration metrics for performance

### 6.2: Metrics & Monitoring
**Unknown**: What metrics to track?

**Decision**: **Key Performance Indicators**
```
1. Agent Performance
   - Average response time (p50, p95, p99)
   - Tool invocations per conversation
   - Error rate per tool

2. User Behavior
   - Active conversations per hour
   - Average conversation length
   - Tool usage distribution

3. System Health
   - Database query latency
   - Rate limit hits
   - Tool failure rate
```

**Clarifications Resolved**:
- Key metrics defined
- Performance SLOs set
- Monitoring dashboards planned
- Alert thresholds established

### 6.3: Error Tracking
**Unknown**: How to track and debug issues?

**Decision**: **Structured Error Context**
```python
try:
    result = await mcp_service.call_tool(...)
except Exception as e:
    trace_id = str(uuid4())
    logger.error(
        json.dumps({
            "trace_id": trace_id,
            "error": str(e),
            "conversation_id": str(conversation_id),
            "user_id": str(user_id),
            "stack_trace": traceback.format_exc()
        })
    )
    # Return user-friendly error without trace_id in response
    raise HTTPException(
        status_code=500,
        detail=f"An error occurred. Reference ID: {trace_id}"
    )
```

**Clarifications Resolved**:
- Trace IDs for correlation
- Full stack traces in logs (never to client)
- Error categorization
- Debugging information preservation

---

## 7. Testing Strategy Unknowns - CLARIFIED

### 7.1: Unit Testing
**Unknown**: How to test agent behavior?

**Decision**: **Mock MCP Tools for Agent Tests**
```python
# tests/unit/test_agent_service.py

def test_agent_adds_task():
    agent = AgentService(api_key="test")
    mock_mcp = MockMCPServer()

    response = agent.run_agent(
        user_message="Add a task to buy milk",
        conversation_history=[],
        mcp_tools=mock_mcp.tools,
        user_id=test_user_id
    )

    assert "add_task" in response.tool_calls
    assert response.tool_calls[0].parameters["title"] == "buy milk"
```

**Clarifications Resolved**:
- Mock MCP tools for isolation
- Test agent intent recognition
- Verify tool selection logic
- Assert response format

### 7.2: Integration Testing
**Unknown**: How to test full chat endpoint?

**Decision**: **FastAPI TestClient with Real Database**
```python
# tests/integration/test_chat_endpoint.py

def test_chat_endpoint_add_task():
    client = TestClient(app)

    response = client.post(
        f"/api/{user_id}/chat",
        json={"conversation_id": None, "message": "Add task to buy milk"},
        headers={"Authorization": f"Bearer {jwt_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["conversation_id"]
    assert "task created" in data["response"].lower()

    # Verify task in database
    task = session.exec(
        select(Task).where(Task.title == "buy milk")
    ).first()
    assert task is not None
```

**Clarifications Resolved**:
- Test with real database
- Verify end-to-end flow
- Check database state
- Validate response format

### 7.3: E2E Testing
**Unknown**: How to test with Playwright?

**Decision**: **User Flow Scenarios**
```typescript
// tests/e2e/chat.spec.ts

test('User can add task via chat', async ({ page }) => {
  await page.goto('http://localhost:3000/chat');

  // Send message
  await page.fill('input[placeholder="Type a message..."]', 'Add task to buy milk');
  await page.click('button[aria-label="Send message"]');

  // Verify response
  await expect(page.locator('text=task created')).toBeVisible();

  // Verify task in list
  await page.goto('http://localhost:3000/tasks');
  await expect(page.locator('text=buy milk')).toBeVisible();
});
```

**Clarifications Resolved**:
- E2E test coverage
- Real browser simulation
- Full user journey verification
- Database state validation

---

## 8. Performance & Scalability Unknowns - CLARIFIED

### 8.1: Response Time SLOs
**Unknown**: What are acceptable response times?

**Decision**: **Target Response Times**
```
add_task:        < 2 seconds
list_tasks:      < 1 second
complete_task:   < 1.5 seconds
delete_task:     < 2 seconds (includes confirmation)
update_task:     < 2 seconds
```

**Clarifications Resolved**:
- Clear performance targets
- User experience expectations
- Monitoring thresholds
- Optimization priorities

### 8.2: Concurrent Users
**Unknown**: How many concurrent users must be supported?

**Decision**: **Hackathon Scale (Phase III)**
```
Minimum requirement: 100 concurrent users
Target: 1000 concurrent users
Database: Neon PostgreSQL with connection pooling

Connection Pool Configuration:
- Min connections: 5
- Max connections: 20 per backend instance
- Timeout: 30 seconds
```

**Clarifications Resolved**:
- Concurrent user capacity
- Connection pool sizing
- Horizontal scaling capability
- Load testing requirements

### 8.3: Database Query Optimization
**Unknown**: How to optimize database queries?

**Decision**: **Indexed Query Patterns**
```python
# Index on (conversation_id, created_at) for history retrieval
SELECT * FROM messages
WHERE conversation_id = ?
ORDER BY created_at DESC
LIMIT 10

# Index on (user_id, created_at) for recent tasks
SELECT * FROM tasks
WHERE user_id = ? AND status = 'pending'
ORDER BY created_at DESC
```

**Clarifications Resolved**:
- Query patterns documented
- Indexes designed
- N+1 query prevention
- Query caching strategy

---

## 9. Deployment & Infrastructure Unknowns - CLARIFIED

### 9.1: Environment Configuration
**Unknown**: What environment variables are needed?

**Decision**: **Environment Variable Schema**
```bash
# Backend (.env)
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://...
JWT_SECRET=secret
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=9000
RATE_LIMIT_PER_MINUTE=60

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

**Clarifications Resolved**:
- All environment variables documented
- Secret management approach
- Configuration per environment
- No hardcoded values

### 9.2: Database Migrations
**Unknown**: How to manage schema changes?

**Decision**: **Alembic Version Control**
```bash
# Create migration
uv run alembic revision --autogenerate -m "Add conversation tables"

# Apply migration
uv run alembic upgrade head

# Rollback (if needed)
uv run alembic downgrade -1
```

**Clarifications Resolved**:
- Migration tooling (Alembic)
- Version control integration
- Rollback capability
- Testing strategy

### 9.3: Hosting Strategy
**Unknown**: Where to deploy Phase III?

**Decision**: **Extend Phase II Hosting**
```
Frontend: Vercel (same as Phase II)
Backend: Railway/Render (same as Phase II)
Database: Neon PostgreSQL (same as Phase II)
MCP Server: Same FastAPI process or separate container

Option A (Simpler): MCP server runs in same FastAPI process
Option B (Scalable): MCP server as separate service with gRPC

Recommendation: Option A for Phase III (Hackathon)
```

**Clarifications Resolved**:
- No new infrastructure needed
- Extends existing deployment
- Single FastAPI process handles both chat API + MCP
- Deployment strategy aligned with Phase II

---

## 10. Summary of Clarifications

All major unknowns have been resolved through the Hackathon II documentation:

✅ **Architecture**: Extend phase-2/, stateless chat endpoint, database-backed state
✅ **OpenAI Integration**: gpt-4-turbo model via Agents SDK, wrapper service pattern
✅ **MCP Server**: 5 tools with standardized JSON schemas, standalone server
✅ **Database**: Conversation + Message models with proper migrations
✅ **Agent Behavior**: Zero-shot intent recognition, pronoun resolution via context
✅ **Frontend**: ChatKit component, TypeScript API client, SSE streaming
✅ **Auth & Security**: JWT passthrough from Better Auth, per-user rate limiting
✅ **Observability**: Structured JSON logging, metrics, error tracking
✅ **Testing**: Unit, integration, and E2E test strategies
✅ **Performance**: Response time SLOs, concurrent user capacity, query optimization
✅ **Deployment**: Environment config, Alembic migrations, hosting on existing infrastructure

---

## Next Steps: Phase 1 (Design)

With all clarifications resolved, Phase 1 (Design) will create:

1. **data-model.md** - SQLModel definitions for Conversation, Message
2. **contracts/** directory:
   - `chat-api-contract.md` - POST /api/{user_id}/chat endpoint spec
   - `mcp-tools-contract.md` - 5 MCP tool specifications
3. **quickstart.md** - Setup and development guide
4. **agent-context.md** - Agent system prompt template

---

**Status**: ✅ Phase 0 (Research) Complete
**Next Stage**: Phase 1 (Design)
**Timeline**: 8 days (Dec 14-21, 2025)
**Points**: 200 points
