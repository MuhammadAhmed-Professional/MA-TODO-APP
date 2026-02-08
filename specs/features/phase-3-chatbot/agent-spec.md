# Phase III: Agent Behavior Specification

**Version**: 1.0.0
**Status**: Active
**Created**: 2025-12-13
**Last Updated**: 2025-12-13

---

## Overview

This document specifies the exact behavior of the OpenAI Agents SDK-based todo assistant, including intent recognition patterns, tool selection logic, confirmation flows, error handling strategies, and multi-turn conversation context management. This ensures consistent, predictable agent behavior across all user interactions.

---

## Agent Configuration

### Model & Parameters

```python
{
    "model": "gpt-4-turbo",
    "temperature": 0.7,  # Balanced: not too creative, not too deterministic
    "max_tokens": 4096,  # Sufficient for multi-turn conversations
    "top_p": 0.9,  # Slightly more deterministic
    "frequency_penalty": 0.0,  # Allow natural language variety
    "presence_penalty": 0.0,  # Don't penalize topic repetition
}
```

### System Prompt

```
You are a helpful todo assistant powered by AI. Your goal is to help users manage their tasks through natural conversation.

You can perform the following operations:
1. Add tasks: When users want to create a new task
2. List tasks: Show users their pending, completed, or all tasks
3. Complete tasks: Mark tasks as done
4. Delete tasks: Remove tasks (requires user confirmation first)
5. Update tasks: Change task titles or descriptions

Guidelines:
- Be conversational and friendly
- Ask clarifying questions when intent is unclear
- For destructive operations (delete/update), always confirm with the user first
- Never expose technical errors - always provide helpful, user-friendly messages
- When a tool fails, offer alternative solutions
- Remember context from earlier in the conversation
- Resolve pronouns (it, that, this) based on recent conversation
- Suggest follow-up actions when helpful

Example interactions:
- User: "Add a task to buy groceries"
  → You recognize this as add_task intent
  → You ask for optional details or confirm task creation

- User: "Delete my oldest task"
  → You first fetch the task to be deleted
  → You ask for explicit confirmation with task name
  → Only after confirmation, you invoke the delete_task tool

- User: "Mark it complete"
  → You remember context from earlier messages
  → You identify which task "it" refers to
  → You confirm completion
```

---

## Intent Recognition

### Intent Categories

The agent recognizes 5 primary intents from user input:

| Intent | User Examples | Tool(s) | Confirmation Required |
|--------|---------------|---------|----------------------|
| **add_task** | "Add a task to...", "Create task...", "I need to...", "Remember to..." | `add_task` | No |
| **list_tasks** | "Show my tasks", "What do I need to do?", "List pending tasks", "Any tasks for today?" | `list_tasks` | No |
| **complete_task** | "Mark complete", "Done with...", "Finished...", "That's done" | `complete_task` | No |
| **delete_task** | "Delete...", "Remove...", "Drop that task", "Get rid of..." | `delete_task` | Yes |
| **update_task** | "Change...", "Update...", "Rename...", "Modify..." | `update_task` | No (but brief confirmation) |

### Intent Detection Logic

```python
class IntentDetector:
    """Detect user intent from natural language input."""

    ADD_TASK_KEYWORDS = {
        "add", "create", "new", "task", "remember", "todo",
        "need to", "should", "make", "set up", "schedule"
    }

    LIST_TASK_KEYWORDS = {
        "list", "show", "what", "all tasks", "pending",
        "completed", "today", "upcoming", "view", "get", "see"
    }

    COMPLETE_KEYWORDS = {
        "complete", "done", "finish", "mark", "check off",
        "finished", "accomplished", "closed", "resolved"
    }

    DELETE_KEYWORDS = {
        "delete", "remove", "drop", "erase", "discard",
        "destroy", "eliminate", "get rid", "no longer"
    }

    UPDATE_KEYWORDS = {
        "update", "change", "rename", "modify", "edit",
        "alter", "transform", "switch", "revise"
    }

    def detect_intent(self, user_input: str) -> str:
        """
        Detect intent from user input.

        Args:
            user_input: User's message

        Returns:
            Intent name: 'add_task', 'list_tasks', 'complete_task', 'delete_task', 'update_task', or 'unknown'
        """
        text_lower = user_input.lower()

        # Destructive operations take priority
        if any(kw in text_lower for kw in self.DELETE_KEYWORDS):
            return "delete_task"

        # Update operations
        if any(kw in text_lower for kw in self.UPDATE_KEYWORDS):
            return "update_task"

        # Complete operations
        if any(kw in text_lower for kw in self.COMPLETE_KEYWORDS):
            return "complete_task"

        # List operations
        if any(kw in text_lower for kw in self.LIST_TASK_KEYWORDS):
            return "list_tasks"

        # Add operations (default for unclear input with potential task info)
        if any(kw in text_lower for kw in self.ADD_TASK_KEYWORDS):
            return "add_task"

        return "unknown"
```

---

## Parameter Extraction

### Extract from Natural Language

#### add_task Parameter Extraction

```python
class ParameterExtractor:
    """Extract parameters from natural language input."""

    async def extract_add_task_params(self, user_input: str, context: dict) -> dict:
        """
        Extract title and optional description for add_task.

        Examples:
        - "Add task: buy groceries" → {"title": "Buy groceries"}
        - "Create 'Fix bug' with description 'Authentication module'" → {"title": "Fix bug", "description": "Authentication module"}
        - "I need to call my mom" → {"title": "Call my mom"}

        Args:
            user_input: User's message
            context: Conversation history and user context

        Returns:
            {"title": str, "description": str | None}
        """
        # Use LLM to extract structured parameters
        extraction_prompt = f"""
        Extract the task title and optional description from this user input:
        "{user_input}"

        Return JSON with:
        {{
            "title": "extracted title (1-200 chars)",
            "description": "optional description (null if not provided)"
        }}
        """

        response = await self.llm.call(extraction_prompt)
        params = json.loads(response)

        # Validation
        if not params.get("title") or len(params["title"]) > 200:
            return None  # Trigger validation error

        return {
            "title": params["title"].strip(),
            "description": params.get("description", None)
        }

    async def extract_list_tasks_params(self, user_input: str, context: dict) -> dict:
        """
        Extract status filter for list_tasks.

        Examples:
        - "Show my tasks" → {"status": "all"}
        - "Show only pending tasks" → {"status": "pending"}
        - "What's completed?" → {"status": "completed"}

        Returns:
            {"status": "all" | "pending" | "completed"}
        """
        text_lower = user_input.lower()

        if any(word in text_lower for word in ["complete", "done", "finished"]):
            return {"status": "completed"}
        elif any(word in text_lower for word in ["pending", "todo", "not done", "outstanding"]):
            return {"status": "pending"}
        else:
            return {"status": "all"}

    async def extract_complete_task_params(self, user_input: str, context: dict) -> dict:
        """
        Extract task_id for complete_task.

        Examples:
        - "Mark task 1 complete" → {"task_id": "uuid_of_task_1"}
        - "Done with the first one" → {"task_id": "uuid_of_first_task"}
        - "I finished it" → {"task_id": "context_resolved_task_id"}

        Returns:
            {"task_id": UUID | None}
        """
        # Check for explicit task reference (number or name)
        task_ref = self._extract_task_reference(user_input)

        if task_ref:
            # Resolve reference to task from context
            task_id = self._resolve_task_reference(task_ref, context)
            return {"task_id": task_id} if task_id else None

        # Check for pronoun resolution (it, that, this)
        if self._contains_pronoun(user_input):
            task_id = self._resolve_pronoun(user_input, context)
            return {"task_id": task_id} if task_id else None

        return None  # Trigger clarification request
```

#### Complex Parameter Extraction Example

```python
def _extract_task_reference(self, user_input: str) -> str | None:
    """Extract task reference from input (number, name, or description)."""

    # Pattern 1: Task number (e.g., "task 1", "the first task")
    import re
    number_match = re.search(r'task\s+(\d+)', user_input.lower())
    if number_match:
        return f"task_{number_match.group(1)}"

    # Pattern 2: Task by name (e.g., "buy groceries", "the bug fix")
    task_name_match = re.search(r'(?:the\s+)?"([^"]+)"', user_input)
    if task_name_match:
        return f"name:{task_name_match.group(1)}"

    # Pattern 3: Ordinal references (first, second, last)
    if "first" in user_input.lower():
        return "position:0"
    elif "last" in user_input.lower():
        return "position:last"

    return None

def _resolve_pronoun(self, user_input: str, context: dict) -> str | None:
    """Resolve pronouns (it, that, this) to tasks from context."""

    if not context.get("recent_task_mentioned"):
        return None

    # For "it", "that", "this" - refer to most recently mentioned task
    if any(p in user_input.lower() for p in ["it", "that", "this"]):
        return context["recent_task_mentioned"]["task_id"]

    return None
```

---

## Tool Selection Logic

### Decision Tree

```
User Input
├── Is destructive (delete/update)?
│   ├── YES → Require confirmation first
│   └── NO → Continue
├── Parse intent from keywords
├── Extract parameters
├── Validate parameters
└── Invoke appropriate tool
```

### Multi-Tool Scenarios

```python
class ToolSelection:
    """Select appropriate MCP tools based on intent and context."""

    async def select_tools(
        self,
        intent: str,
        params: dict,
        context: dict
    ) -> list[str]:
        """
        Select which MCP tools to invoke.

        Some user inputs may require multiple tools in sequence.

        Example: "Show me all pending tasks and mark the first one complete"
        → Tools: ["list_tasks", "complete_task"]

        Args:
            intent: Primary detected intent
            params: Extracted parameters
            context: Conversation context

        Returns:
            List of tool names to invoke in order
        """
        tools = []

        # Single-tool intents
        if intent == "add_task":
            tools.append("add_task")
        elif intent == "list_tasks":
            tools.append("list_tasks")
        elif intent == "complete_task":
            tools.append("complete_task")
        elif intent == "delete_task":
            tools.append("delete_task")
        elif intent == "update_task":
            tools.append("update_task")

        # Multi-tool compound intents (future)
        # "Show me tasks and complete the first one"
        # → ["list_tasks", "complete_task"]

        return tools
```

---

## Confirmation Flows

### Destructive Operations (Delete & Update)

#### Delete Confirmation Flow

```python
class ConfirmationFlow:
    """Handle confirmation flows for destructive operations."""

    async def confirm_delete_task(
        self,
        task_id: str,
        task_details: dict,
        user_input: str
    ) -> bool:
        """
        Confirm task deletion with user.

        Flow:
        1. Identify task to be deleted
        2. Ask user explicitly for confirmation
        3. Wait for user response (yes/no)
        4. Proceed only on explicit confirmation

        Example:
        User: "Delete task 1"
        AI: "Are you sure you want to delete 'Buy groceries'? This action can't be undone. (yes/no)"
        User: "yes"
        [Delete tool invoked]

        Args:
            task_id: UUID of task to delete
            task_details: Task title and description
            user_input: User's original request

        Returns:
            True if confirmed, False if declined
        """
        # Generate confirmation message
        confirmation_msg = f"""I want to make sure - do you want to delete '{task_details['title']}'?
This action can't be undone. Please say 'yes' or 'no'."""

        agent_response = {
            "text": confirmation_msg,
            "requires_user_confirmation": True,
            "pending_tool": "delete_task",
            "pending_params": {"task_id": task_id}
        }

        # Return response to user (agent stops here and waits)
        return agent_response

    async def process_confirmation_response(
        self,
        user_response: str,
        pending_tool: str,
        pending_params: dict
    ) -> bool:
        """
        Process user's confirmation response.

        Args:
            user_response: User's yes/no response
            pending_tool: Tool waiting for confirmation
            pending_params: Parameters for the tool

        Returns:
            True if confirmed (proceed with tool invocation)
        """
        response_lower = user_response.lower().strip()

        # Explicit confirmation patterns
        if response_lower in ["yes", "y", "confirm", "confirmed", "go ahead", "delete", "proceed"]:
            return True

        # Explicit decline patterns
        if response_lower in ["no", "n", "cancel", "nevermind", "don't", "skip"]:
            return False

        # Ambiguous - ask for clarification
        return None  # Trigger "Please say yes or no" response
```

#### Update Confirmation Flow (Lighter)

```python
async def confirm_update_task(
    self,
    task_id: str,
    task_details: dict,
    new_values: dict
) -> dict:
    """
    Confirm task update (lighter than delete).

    Example:
    User: "Change task 1 to 'Buy groceries and cook dinner'"
    AI: "Updated! Changed 'Buy groceries' to 'Buy groceries and cook dinner'"
    [Tool invoked immediately, user can undo via conversation]

    For clarity, always show what changed.

    Args:
        task_id: UUID of task to update
        task_details: Current task details
        new_values: New title/description

    Returns:
        Confirmation message and proceed flag
    """
    changes = []
    if new_values.get("title"):
        changes.append(f"title: '{task_details['title']}' → '{new_values['title']}'")
    if new_values.get("description"):
        changes.append(f"description: updated")

    response = f"Updated! {', '.join(changes)}"

    return {
        "text": response,
        "proceed": True  # Invoke immediately
    }
```

---

## Multi-Turn Context Awareness

### Conversation History Management

```python
class ContextManager:
    """Manage conversation context for multi-turn interactions."""

    def __init__(self, max_history: int = 10):
        self.message_history = []
        self.max_history = max_history
        self.recent_tasks = []  # Recently mentioned tasks
        self.recent_operations = []  # Recently performed operations

    async def build_context(self, messages: list) -> dict:
        """
        Build rich context from conversation history.

        Args:
            messages: List of messages from database

        Returns:
            dict with:
            - conversation_topics: What the conversation is about
            - recent_tasks: Recently mentioned task IDs
            - pending_operations: Operations waiting for user response
            - user_preferences: Inferred user preferences (e.g., list completed tasks often)
        """
        context = {
            "conversation_topics": self._extract_topics(messages),
            "recent_tasks": self._extract_recent_tasks(messages),
            "recent_operations": self._extract_recent_operations(messages),
            "conversation_length": len(messages),
            "last_tool_used": self._get_last_tool_used(messages),
        }

        return context

    def _extract_recent_tasks(self, messages: list) -> list[dict]:
        """Extract task IDs mentioned in recent messages."""
        tasks = []

        # Look for tool call results containing task IDs
        for msg in messages[-5:]:  # Last 5 messages
            if msg.get("tool_calls"):
                for tool_call in msg["tool_calls"]:
                    if tool_call.get("result", {}).get("task_id"):
                        tasks.append({
                            "task_id": tool_call["result"]["task_id"],
                            "title": tool_call["result"].get("title"),
                            "message_index": messages.index(msg)
                        })

        return tasks

    def _extract_topics(self, messages: list) -> list[str]:
        """Extract conversation topics from messages."""
        topics = []

        for msg in messages[-10:]:  # Last 10 messages
            content = msg.get("content", "").lower()
            if "task" in content or "todo" in content:
                topics.append("task_management")
            if "complete" in content or "done" in content:
                topics.append("task_completion")
            if "delete" in content or "remove" in content:
                topics.append("task_deletion")

        return list(set(topics))
```

### Pronoun Resolution

```python
class PronounResolver:
    """Resolve pronouns (it, that, this) to actual tasks."""

    def resolve_pronoun(
        self,
        user_input: str,
        context: dict,
        recent_tasks: list
    ) -> str | None:
        """
        Resolve pronouns to tasks from context.

        Examples:
        1. User: "Create 'Fix bug'"
           AI: "Task created: 'Fix bug'"
           User: "Mark it complete"
           → "it" = "Fix bug" task

        2. User: "Show pending tasks"
           AI: "1. Buy milk, 2. Fix bug, 3. Call mom"
           User: "Delete the first one"
           → "the first one" = "Buy milk" task

        3. User: "When should I do that?"
           → "that" = most recently mentioned task or operation

        Args:
            user_input: User's message
            context: Conversation context
            recent_tasks: List of recently mentioned task IDs

        Returns:
            Task ID if pronoun resolved, None otherwise
        """
        input_lower = user_input.lower()

        # Pattern 1: Explicit pronoun references
        if "it" in input_lower or "that" in input_lower or "this" in input_lower:
            # Most recent task is the antecedent
            if recent_tasks:
                return recent_tasks[-1]["task_id"]

        # Pattern 2: Ordinal references ("the first", "the second", "the last")
        ordinal_match = self._extract_ordinal(user_input)
        if ordinal_match and context.get("last_list_result"):
            task_list = context["last_list_result"]
            if ordinal_match == 0:  # "first"
                return task_list[0]["task_id"] if task_list else None
            elif ordinal_match == -1:  # "last"
                return task_list[-1]["task_id"] if task_list else None
            elif ordinal_match < len(task_list):
                return task_list[ordinal_match]["task_id"]

        return None

    def _extract_ordinal(self, user_input: str) -> int | None:
        """Extract ordinal position from input ('first' → 0, 'last' → -1, etc)."""
        input_lower = user_input.lower()

        ordinals = {
            "first": 0, "second": 1, "third": 2, "fourth": 3, "fifth": 4,
            "last": -1, "previous": -1
        }

        for ordinal_word, position in ordinals.items():
            if ordinal_word in input_lower:
                return position

        return None
```

---

## Error Handling Strategy

### Error Recovery Flow

```python
class ErrorHandler:
    """Handle tool errors gracefully with user-friendly messages."""

    ERROR_MESSAGES = {
        "VALIDATION_ERROR": {
            "empty_title": "I couldn't create that task because the title is empty. Please tell me what the task is.",
            "title_too_long": "The task title is too long (max 200 characters). Could you make it shorter?",
            "description_too_long": "The description is too long (max 2000 characters). Could you shorten it?",
            "invalid_status": "I didn't understand that status. Did you mean 'pending', 'completed', or 'all'?"
        },
        "NOT_FOUND": {
            "task_not_found": "I couldn't find that task. Would you like to see all your tasks?",
            "conversation_not_found": "I couldn't find that conversation. Starting a new one."
        },
        "AUTHORIZATION_ERROR": {
            "access_denied": "I'm unable to access that task. Please make sure it's one of your tasks."
        },
        "INVALID_STATE": {
            "already_completed": "That task is already marked complete."
        },
        "SERVER_ERROR": {
            "generic": "Sorry, I had trouble with that operation. Please try again.",
            "database_error": "I'm experiencing technical difficulties. Please try again in a moment.",
            "timeout": "That took too long. Please try again with a simpler request."
        }
    }

    async def handle_tool_error(
        self,
        tool_name: str,
        error_code: str,
        error_details: dict
    ) -> str:
        """
        Convert tool error to user-friendly message.

        Args:
            tool_name: Name of tool that failed
            error_code: Error classification (VALIDATION_ERROR, NOT_FOUND, etc.)
            error_details: Additional error details

        Returns:
            User-friendly error message
        """
        # Look up user-friendly message
        category_messages = self.ERROR_MESSAGES.get(error_code, {})
        specific_key = error_details.get("message_key", "generic")
        user_message = category_messages.get(
            specific_key,
            self.ERROR_MESSAGES["SERVER_ERROR"]["generic"]
        )

        # Log error with full details for debugging
        logger.error(
            json.dumps({
                "timestamp": datetime.utcnow().isoformat(),
                "component": "error_handler",
                "tool": tool_name,
                "error_code": error_code,
                "details": str(error_details)
            })
        )

        return user_message

    async def suggest_recovery(
        self,
        tool_name: str,
        error_code: str,
        context: dict
    ) -> str:
        """
        Suggest next steps to user after error.

        Args:
            tool_name: Tool that failed
            error_code: Error type
            context: Conversation context

        Returns:
            Suggestion message
        """
        if error_code == "NOT_FOUND" and tool_name == "complete_task":
            return "Would you like to see all your pending tasks so you can choose one?"

        elif error_code == "VALIDATION_ERROR" and tool_name == "add_task":
            return "Try again with a shorter title (under 200 characters)."

        elif error_code == "SERVER_ERROR":
            return "Please try again in a moment, or let me know how else I can help."

        return "Is there anything else I can help you with?"
```

---

## Agent Response Format

### Response Structure

```python
class AgentResponse:
    """Structured response from agent."""

    text: str  # User-facing response message
    tool_calls: list[dict] = []  # Tools invoked and results
    confidence: float = 1.0  # Confidence in understanding (0.0-1.0)
    requires_clarification: bool = False  # Does user need to clarify?
    next_suggested_actions: list[str] = []  # What user could do next

    # Example response:
    response = {
        "text": "I've created a task: 'Buy groceries'. Would you like to add details like a description or due date?",
        "tool_calls": [
            {
                "name": "add_task",
                "parameters": {"title": "Buy groceries"},
                "result": {
                    "task_id": "uuid-123",
                    "title": "Buy groceries",
                    "status": "pending"
                }
            }
        ],
        "confidence": 0.95,
        "requires_clarification": False,
        "next_suggested_actions": [
            "Add a description to the task",
            "Set a due date",
            "Create another task"
        ]
    }
```

### Response Examples by Intent

#### add_task Response

```
User: "Add a task to buy groceries"

Agent Response:
"I've created a task: 'Buy groceries'. Would you like to add any details like a description or due date?"

Tool calls: [add_task result with task_id]
Next actions: ["Add description", "Create another task", "Show all tasks"]
```

#### list_tasks Response

```
User: "Show my pending tasks"

Agent Response:
"You have 3 pending tasks:
1. Buy groceries
2. Fix bug in dashboard
3. Call mom"

Tool calls: [list_tasks result with array of tasks]
Next actions: ["Complete a task", "Add new task", "Show completed tasks"]
```

#### complete_task Response

```
User: "Mark the first task complete"

Agent Response:
"Done! 'Buy groceries' is now marked complete. You have 2 pending tasks left."

Tool calls: [complete_task result]
Next actions: ["View remaining tasks", "Complete another task"]
```

#### delete_task Response

```
User: "Delete that task"

Agent Response (Step 1 - Confirmation):
"Are you sure you want to delete 'Fix bug in dashboard'? This action can't be undone. (yes/no)"

[Waits for user confirmation]

Agent Response (Step 2 - After confirmation):
"Task deleted. You now have 1 pending task left."

Tool calls: [delete_task result]
```

---

## Conversation Flow Diagram

```
User Message
    ↓
[Intent Detection]
    ├─→ add_task?
    ├─→ list_tasks?
    ├─→ complete_task?
    ├─→ delete_task? (needs confirmation)
    ├─→ update_task?
    └─→ unknown?
    ↓
[Parameter Extraction]
    ├─→ Extract from input
    ├─→ Resolve pronouns from context
    └─→ Validate parameters
    ↓
[Confirmation Check]
    ├─→ Is destructive operation?
    │   ├─→ YES: Request confirmation from user
    │   │        Wait for yes/no response
    │   │        Re-evaluate after confirmation
    │   └─→ NO: Proceed to tool invocation
    └─→ Parameters valid?
        ├─→ NO: Request clarification
        └─→ YES: Proceed to tool invocation
    ↓
[Tool Invocation]
    ├─→ Invoke MCP tool(s)
    ├─→ Handle tool response/error
    ├─→ Update context with results
    └─→ Log operation with trace_id
    ↓
[Response Generation]
    ├─→ Craft user-friendly response
    ├─→ Suggest next actions
    └─→ Return response to user
```

---

## Testing Patterns

### Unit Tests for Agent Behavior

```python
import pytest

class TestAgentBehavior:
    """Test agent behavior patterns."""

    async def test_add_task_intent_recognition(self):
        """Test agent recognizes add_task intent."""
        intents = [
            ("Add a task to buy milk", "add_task"),
            ("Create task: fix bug", "add_task"),
            ("I need to call my mom", "add_task"),
            ("Remember to take out trash", "add_task"),
        ]

        for user_input, expected_intent in intents:
            intent = agent.detect_intent(user_input)
            assert intent == expected_intent, f"Failed for: {user_input}"

    async def test_list_tasks_status_filter(self):
        """Test agent extracts status filter from natural language."""
        filters = [
            ("Show all my tasks", "all"),
            ("What tasks are pending?", "pending"),
            ("Show me completed tasks", "completed"),
            ("What's done?", "completed"),
        ]

        for user_input, expected_status in filters:
            params = await agent.extract_list_tasks_params(user_input, {})
            assert params["status"] == expected_status

    async def test_pronoun_resolution_in_context(self):
        """Test agent resolves pronouns correctly."""
        messages = [
            {"role": "user", "content": "Create task 'Buy milk'"},
            {"role": "assistant", "content": "Task created", "tool_calls": [
                {"name": "add_task", "result": {"task_id": "uuid-1", "title": "Buy milk"}}
            ]},
            {"role": "user", "content": "Mark it complete"},
        ]

        context = agent.build_context(messages)
        task_id = agent.resolve_pronoun("Mark it complete", context, context["recent_tasks"])
        assert task_id == "uuid-1"

    async def test_delete_confirmation_required(self):
        """Test agent requires confirmation before deleting."""
        messages = [
            {"role": "user", "content": "Delete task 1"},
        ]

        response = await agent.run(messages)
        assert response["requires_user_confirmation"] == True
        assert "sure" in response["text"].lower() or "confirm" in response["text"].lower()
        assert response["tool_calls"] == []  # No tool invoked yet

    async def test_error_recovery_on_invalid_input(self):
        """Test agent provides helpful error recovery."""
        user_input = "Add task " + "x" * 300  # Title too long

        try:
            response = await agent.run([{"role": "user", "content": user_input}])
        except Exception as e:
            response = agent.handle_error(e)

        # Should not expose technical error
        assert "character" not in str(response).lower() or "200" in str(response)
        assert "stack trace" not in str(response)
        assert "please" in str(response).lower()

    async def test_multi_tool_scenario(self):
        """Test agent handles compound intents (if implemented)."""
        # Future: "Show me tasks and complete the first one"
        # Should invoke ["list_tasks", "complete_task"]
        pass
```

---

## Edge Cases & Special Handling

### Ambiguous Input

```python
# Input: "Something with tasks"
Agent: "I'm not sure what you'd like to do. Would you like to:
1. See your tasks
2. Add a new task
3. Complete a task
4. Delete a task"

# Input: "Do something with the thing"
Agent: "I'm not sure which task you're referring to. Could you be more specific?
Your pending tasks are:
1. Buy groceries
2. Fix bug
3. Call mom"
```

### Ambiguous Task Reference

```python
# Multiple tasks matching description
User: "Complete the task"
Agent: "Which task would you like to complete? Here are your pending tasks:
1. Buy groceries
2. Buy milk
3. Buy eggs

Would you like to complete one of these, or did you mean something else?"
```

### Partial Confirmations

```python
User: "Delete task 1"
Agent: "Are you sure you want to delete 'Buy groceries'?"
User: "Yeah, do it"
Agent: [Interprets "Yeah, do it" as confirmation, proceeds with deletion]

User: "Delete task 1"
Agent: "Are you sure?"
User: "I'm not sure"
Agent: "No problem! We'll keep 'Buy groceries' for now. Is there something else I can help with?"
```

---

## Next Steps

1. Implement Agent behavior patterns in `backend/src/services/agent_service.py`
2. Test intent recognition with unit tests
3. Test parameter extraction accuracy
4. Validate pronoun resolution in multi-turn conversations
5. Verify error messages are user-friendly
6. Test confirmation flows with user scenarios

---

**Status**: ✅ Specification Complete
**Next**: Create Implementation Plan (plan.md)
