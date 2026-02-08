# Chat API Contract - Phase III

**Version**: 1.0.0
**Status**: Active
**Created**: 2025-12-13

---

## Endpoint: POST /api/{user_id}/chat

Send a message to the AI chatbot and receive a response with tool executions.

### Authentication
- **Method**: Bearer Token (JWT from Better Auth)
- **Header**: `Authorization: Bearer <jwt_token>`
- **Required**: YES
- **Scope**: Must be authenticated user

### URL Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `user_id` | UUID | User ID from URL path | `550e8400-e29b-41d4-a716-446655440000` |

**Validation**: `user_id` must match authenticated user from JWT token

### Request Body

```json
{
  "conversation_id": "string (UUID) or null",
  "message": "string (1-10000 characters)"
}
```

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `conversation_id` | UUID \| null | YES | Valid UUID format or null | Existing conversation ID or null for new conversation |
| `message` | string | YES | 1-10000 chars | User's message to send to AI |

### Request Examples

**New Conversation**
```bash
curl -X POST http://localhost:8000/api/550e8400-e29b-41d4-a716-446655440000/chat \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": null,
    "message": "Add a task to buy groceries"
  }'
```

**Existing Conversation**
```bash
curl -X POST http://localhost:8000/api/550e8400-e29b-41d4-a716-446655440000/chat \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "660f9511-f30c-52e5-b827-557766551111",
    "message": "Mark it complete"
  }'
```

**TypeScript Request**
```typescript
interface ChatRequest {
  conversation_id: string | null;
  message: string;
}

const response = await fetch(`/api/${userId}/chat`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    conversation_id: null,
    message: 'Add a task to buy milk'
  })
});
```

---

## Response: 200 OK

### Success Response Body

```json
{
  "conversation_id": "string (UUID)",
  "message_id": "string (UUID)",
  "response": "string",
  "tool_calls": [
    {
      "id": "string",
      "type": "function",
      "function": {
        "name": "string",
        "arguments": {}
      },
      "result": {}
    }
  ],
  "timestamp": "string (ISO8601)"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `conversation_id` | UUID | ID of conversation (created if new) |
| `message_id` | UUID | ID of assistant's response message |
| `response` | string | AI's text response to user |
| `tool_calls` | array | Array of tool invocations and results |
| `timestamp` | ISO8601 | Server timestamp of response |

### Tool Call Structure

```json
{
  "id": "call_123abc",
  "type": "function",
  "function": {
    "name": "add_task",
    "arguments": {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Buy groceries"
    }
  },
  "result": {
    "task_id": "550e8400-e29b-41d4-a716-446655440001",
    "title": "Buy groceries",
    "status": "pending",
    "created_at": "2025-12-13T10:30:00Z"
  }
}
```

### Success Response Examples

**Add Task Response**
```json
{
  "conversation_id": "660f9511-f30c-52e5-b827-557766551111",
  "message_id": "770g0622-g41d-63f6-c938-668877662222",
  "response": "I've created a task: 'Buy groceries'. Would you like to add any details?",
  "tool_calls": [
    {
      "id": "call_abc123",
      "type": "function",
      "function": {
        "name": "add_task",
        "arguments": {
          "user_id": "550e8400-e29b-41d4-a716-446655440000",
          "title": "Buy groceries"
        }
      },
      "result": {
        "task_id": "550e8400-e29b-41d4-a716-446655440001",
        "title": "Buy groceries",
        "status": "pending",
        "created_at": "2025-12-13T10:30:00Z"
      }
    }
  ],
  "timestamp": "2025-12-13T10:30:00Z"
}
```

**List Tasks Response (No Tool Calls)**
```json
{
  "conversation_id": "660f9511-f30c-52e5-b827-557766551111",
  "message_id": "770g0622-g41d-63f6-c938-668877662223",
  "response": "You have 3 pending tasks:\n1. Buy groceries\n2. Fix bug in dashboard\n3. Call mom",
  "tool_calls": [
    {
      "id": "call_def456",
      "type": "function",
      "function": {
        "name": "list_tasks",
        "arguments": {
          "user_id": "550e8400-e29b-41d4-a716-446655440000",
          "status": "pending"
        }
      },
      "result": {
        "tasks": [
          {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "title": "Buy groceries",
            "status": "pending"
          },
          {
            "id": "550e8400-e29b-41d4-a716-446655440002",
            "title": "Fix bug in dashboard",
            "status": "pending"
          },
          {
            "id": "550e8400-e29b-41d4-a716-446655440003",
            "title": "Call mom",
            "status": "pending"
          }
        ]
      }
    }
  ],
  "timestamp": "2025-12-13T10:30:00Z"
}
```

---

## Error Responses

### 400 Bad Request

**Invalid Message**
```json
{
  "error": "VALIDATION_ERROR",
  "message": "Message must be between 1 and 10000 characters"
}
```

**Invalid Conversation ID**
```json
{
  "error": "VALIDATION_ERROR",
  "message": "conversation_id must be a valid UUID or null"
}
```

### 401 Unauthorized

**Missing or Invalid JWT Token**
```json
{
  "error": "UNAUTHORIZED",
  "message": "Authentication required. Provide valid JWT token in Authorization header."
}
```

### 403 Forbidden

**User ID Mismatch**
```json
{
  "error": "FORBIDDEN",
  "message": "Cannot access conversations for this user"
}
```

**Conversation Belongs to Different User**
```json
{
  "error": "FORBIDDEN",
  "message": "Access denied. This conversation belongs to another user."
}
```

### 404 Not Found

**Conversation Not Found**
```json
{
  "error": "NOT_FOUND",
  "message": "Conversation with ID '660f9511-f30c-52e5-b827-557766551111' not found"
}
```

### 429 Too Many Requests

**Rate Limited**
```json
{
  "error": "RATE_LIMITED",
  "message": "Too many requests. Please wait before sending another message.",
  "retry_after": 60
}
```

### 500 Internal Server Error

**Agent Failure**
```json
{
  "error": "AGENT_ERROR",
  "message": "Failed to process your message. Please try again.",
  "trace_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Database Error**
```json
{
  "error": "SERVER_ERROR",
  "message": "An unexpected error occurred. Please try again later.",
  "trace_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## Rate Limiting

### Rate Limit Headers

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1702464000
```

| Header | Meaning |
|--------|---------|
| `X-RateLimit-Limit` | Requests allowed per minute |
| `X-RateLimit-Remaining` | Requests remaining in current window |
| `X-RateLimit-Reset` | Unix timestamp when limit resets |

### Rate Limit Policy

- **Limit**: 60 requests per minute per authenticated user
- **Burst**: Up to 5 requests in 5 seconds
- **Window**: Rolling 60-second window
- **Status Code**: 429 when exceeded

---

## Implementation Requirements

### Request Validation

```python
from pydantic import BaseModel, Field, validator
from uuid import UUID
from typing import Optional

class ChatRequest(BaseModel):
    conversation_id: Optional[UUID] = None
    message: str = Field(..., min_length=1, max_length=10000)

    @validator('message')
    def message_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty or whitespace only')
        return v.strip()

    class Config:
        schema_extra = {
            "example": {
                "conversation_id": None,
                "message": "Add a task to buy milk"
            }
        }
```

### Response Structure

```python
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

class ToolCall(BaseModel):
    id: str
    type: str
    function: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    conversation_id: UUID
    message_id: UUID
    response: str
    tool_calls: List[ToolCall] = []
    timestamp: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() + 'Z'
        }
```

### Endpoint Implementation

```python
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

router = APIRouter()

@router.post(
    "/api/{user_id}/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    tags=["Chat"],
    summary="Send message to chatbot"
)
async def chat(
    user_id: UUID,
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    rate_limiter: RateLimiter = Depends(get_rate_limiter)
) -> ChatResponse:
    """
    Send a message to the AI chatbot and receive a response.

    - **user_id**: User's UUID from URL
    - **conversation_id**: Existing conversation (null for new)
    - **message**: Your message (1-10000 chars)

    Returns:
    - **conversation_id**: Chat session ID
    - **response**: AI's text response
    - **tool_calls**: Tool executions and results
    """

    # 1. Validate authorization
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # 2. Check rate limit
    if not rate_limiter.is_allowed(user_id):
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please wait.",
            headers={"Retry-After": "60"}
        )

    # 3. Fetch or create conversation
    conversation = await get_or_create_conversation(
        user_id=user_id,
        conversation_id=request.conversation_id,
        session=session
    )

    # 4. Fetch message history
    history = await fetch_message_history(conversation.id, session)

    # 5. Run agent
    agent_response = await agent_service.run_agent(
        user_message=request.message,
        conversation_history=history,
        mcp_tools=mcp_tools,
        user_id=user_id
    )

    # 6. Persist messages
    user_msg = Message(
        conversation_id=conversation.id,
        user_id=user_id,
        role="user",
        content=request.message
    )
    assistant_msg = Message(
        conversation_id=conversation.id,
        user_id=user_id,
        role="assistant",
        content=agent_response.text,
        tool_calls=agent_response.tool_calls
    )
    session.add(user_msg)
    session.add(assistant_msg)
    session.commit()

    # 7. Return response
    return ChatResponse(
        conversation_id=conversation.id,
        message_id=assistant_msg.id,
        response=agent_response.text,
        tool_calls=agent_response.tool_calls,
        timestamp=datetime.utcnow()
    )
```

---

## Performance SLOs

| Scenario | Target | Acceptable | Limit |
|----------|--------|-----------|-------|
| Add Task | < 2s | < 3s | > 5s ❌ |
| List Tasks | < 1s | < 2s | > 3s ❌ |
| Complete Task | < 1.5s | < 2s | > 3s ❌ |
| Delete Task | < 2s | < 3s | > 5s ❌ |
| Conversation Retrieval | < 100ms | < 200ms | > 500ms ❌ |

---

## Backward Compatibility

This contract is version 1.0.0. Future versions will maintain backward compatibility:

- New optional fields may be added to responses
- New optional parameters may be added to requests
- Existing fields will not be removed or renamed
- Clients should ignore unknown fields

---

## Testing Checklist

- [ ] Valid request returns 200 OK
- [ ] Invalid message length returns 400
- [ ] Invalid UUID format returns 400
- [ ] Missing JWT token returns 401
- [ ] Mismatched user_id returns 403
- [ ] Non-existent conversation returns 404
- [ ] Rate limit exceeded returns 429
- [ ] Agent error returns 500 with trace_id
- [ ] Response includes all required fields
- [ ] Tool calls correctly formatted
- [ ] Timestamps in ISO8601 format
- [ ] Rate limit headers present

---

**Status**: ✅ Complete
**Next**: MCP Tools Contract
