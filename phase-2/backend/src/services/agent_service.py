"""
Agent Service for AI-Powered Todo Assistant

Implements the core AI agent using OpenAI Agents SDK with MCP tool integration.
Handles natural language understanding, intent parsing, multi-turn context management,
and confirmation flows for destructive operations.

Based on Phase III Agent Behavior Specification.
"""

import json
import logging
import re
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

import os

from agents import Agent, ModelProvider, OpenAIChatCompletionsModel, RunConfig, RunContextWrapper, Runner, function_tool
from openai import AsyncOpenAI
from sqlmodel import Session

from src.models.conversation import Message
from src.services.mcp_tools import MCPToolsService

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# CONTEXT DATA CLASS
# ============================================================================

@dataclass
class AgentContext:
    """Context object passed to agent tools containing database session and user info."""
    session: Session
    user_id: str
    recent_tasks: list[dict]
    last_list_result: Optional[list]
    pending_confirmation: Optional[dict]


# ============================================================================
# FUNCTION TOOLS (OpenAI Agents SDK)
# ============================================================================

@function_tool
async def add_task(
    ctx: RunContextWrapper[AgentContext],
    title: str,
    description: Optional[str] = None,
) -> str:
    """
    Add a new task for the user.

    Args:
        title: Task title (required, 1-200 characters)
        description: Optional task description (max 2000 characters)
    """
    mcp_service = MCPToolsService(ctx.context.session)
    result = mcp_service.add_task(
        user_id=ctx.context.user_id,
        title=title,
        description=description,
    )

    if result["success"]:
        task = result["task"]
        return json.dumps({
            "success": True,
            "message": f"I've created a task: '{task['title']}'. Would you like to add any details like a description?",
            "task": task,
        })
    else:
        return json.dumps({
            "success": False,
            "error": result.get("error", "Failed to create task"),
        })


@function_tool
async def list_tasks(
    ctx: RunContextWrapper[AgentContext],
    is_complete: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0,
) -> str:
    """
    List all tasks for a user with optional filtering.

    Args:
        is_complete: Optional filter: true for completed tasks, false for incomplete, null for all
        limit: Maximum number of tasks to return (1-100, default 50)
        offset: Number of tasks to skip (default 0)
    """
    mcp_service = MCPToolsService(ctx.context.session)
    result = mcp_service.list_tasks(
        user_id=ctx.context.user_id,
        is_complete=is_complete,
        limit=limit,
        offset=offset,
    )

    if result["success"]:
        tasks = result["tasks"]
        total = result["total"]

        if not tasks:
            return json.dumps({
                "success": True,
                "message": "You don't have any tasks yet. Would you like to create one?",
                "tasks": [],
                "total": 0,
            })

        return json.dumps({
            "success": True,
            "message": f"You have {total} task{'s' if total != 1 else ''}. Would you like to complete, update, or delete any of these?",
            "tasks": tasks,
            "total": total,
        })
    else:
        return json.dumps({
            "success": False,
            "error": result.get("error", "Failed to list tasks"),
        })


@function_tool
async def complete_task(
    ctx: RunContextWrapper[AgentContext],
    task_id: str,
) -> str:
    """
    Mark a task as complete.

    Args:
        task_id: UUID of the task to mark complete
    """
    mcp_service = MCPToolsService(ctx.context.session)
    task_id_uuid = uuid.UUID(task_id)

    result = mcp_service.complete_task(
        user_id=ctx.context.user_id,
        task_id=task_id_uuid,
    )

    if result["success"]:
        task = result["task"]
        return json.dumps({
            "success": True,
            "message": f"Done! '{task['title']}' is now marked complete.",
            "task": task,
        })
    else:
        return json.dumps({
            "success": False,
            "error": result.get("error", "Failed to complete task"),
        })


@function_tool
async def delete_task(
    ctx: RunContextWrapper[AgentContext],
    task_id: str,
) -> str:
    """
    Delete a task.

    Args:
        task_id: UUID of the task to delete
    """
    mcp_service = MCPToolsService(ctx.context.session)
    task_id_uuid = uuid.UUID(task_id)

    result = mcp_service.delete_task(
        user_id=ctx.context.user_id,
        task_id=task_id_uuid,
    )

    if result["success"]:
        return json.dumps({
            "success": True,
            "message": result.get("message", "Task deleted successfully"),
        })
    else:
        return json.dumps({
            "success": False,
            "error": result.get("error", "Failed to delete task"),
        })


@function_tool
async def update_task(
    ctx: RunContextWrapper[AgentContext],
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    is_complete: Optional[bool] = None,
) -> str:
    """
    Update task details (title, description, or completion status).

    Args:
        task_id: UUID of the task to update
        title: Optional new title (1-200 characters)
        description: Optional new description (max 2000 characters)
        is_complete: Optional new completion status
    """
    mcp_service = MCPToolsService(ctx.context.session)
    task_id_uuid = uuid.UUID(task_id)

    result = mcp_service.update_task(
        user_id=ctx.context.user_id,
        task_id=task_id_uuid,
        title=title,
        description=description,
        is_complete=is_complete,
    )

    if result["success"]:
        task = result["task"]
        return json.dumps({
            "success": True,
            "message": f"Updated! Task '{task['title']}' has been modified.",
            "task": task,
        })
    else:
        return json.dumps({
            "success": False,
            "error": result.get("error", "Failed to update task"),
        })


# ============================================================================
# INTENT DETECTION AND PARAMETER EXTRACTION
# ============================================================================

class IntentDetector:
    """
    Detect user intent from natural language input.

    Analyzes user messages to determine which operation they want to perform
    on their todo tasks (add, list, complete, delete, update).
    """

    # Keyword sets for intent detection
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

    @classmethod
    def detect_intent(cls, user_input: str) -> str:
        """
        Detect primary intent from user input.

        Args:
            user_input: User's message text

        Returns:
            Intent name: 'add_task', 'list_tasks', 'complete_task',
            'delete_task', 'update_task', or 'unknown'
        """
        text_lower = user_input.lower()

        # Destructive operations take priority (delete before update)
        if any(kw in text_lower for kw in cls.DELETE_KEYWORDS):
            return "delete_task"

        # Update operations
        if any(kw in text_lower for kw in cls.UPDATE_KEYWORDS):
            return "update_task"

        # Complete operations
        if any(kw in text_lower for kw in cls.COMPLETE_KEYWORDS):
            return "complete_task"

        # List operations
        if any(kw in text_lower for kw in cls.LIST_TASK_KEYWORDS):
            return "list_tasks"

        # Add operations (default for unclear input)
        if any(kw in text_lower for kw in cls.ADD_TASK_KEYWORDS):
            return "add_task"

        return "unknown"


class ParameterExtractor:
    """
    Extract parameters from natural language input for tool execution.

    Uses regex patterns and LLM-based extraction to parse task titles,
    descriptions, status filters, and task references.
    """

    @staticmethod
    def extract_task_reference(user_input: str) -> Optional[str]:
        """
        Extract task reference from input (number, name, or ordinal).

        Args:
            user_input: User's message

        Returns:
            Task reference string or None
        """
        # Pattern 1: Task number (e.g., "task 1", "the first task")
        number_match = re.search(r'task\s+(\d+)', user_input.lower())
        if number_match:
            return f"task_{number_match.group(1)}"

        # Pattern 2: Task by name in quotes (e.g., "buy groceries")
        task_name_match = re.search(r'(?:the\s+)?"([^"]+)"', user_input)
        if task_name_match:
            return f"name:{task_name_match.group(1)}"

        # Pattern 3: Ordinal references (first, second, last)
        if "first" in user_input.lower():
            return "position:0"
        elif "second" in user_input.lower():
            return "position:1"
        elif "third" in user_input.lower():
            return "position:2"
        elif "last" in user_input.lower():
            return "position:last"

        return None

    @staticmethod
    def contains_pronoun(user_input: str) -> bool:
        """
        Check if input contains pronouns that need resolution.

        Args:
            user_input: User's message

        Returns:
            True if pronouns detected
        """
        pronouns = {"it", "that", "this", "one", "the one"}
        text_lower = user_input.lower()
        return any(p in text_lower for p in pronouns)

    @staticmethod
    def extract_ordinal_position(user_input: str) -> Optional[int]:
        """
        Extract ordinal position from input.

        Args:
            user_input: User's message

        Returns:
            Position index (0-based) or -1 for last, or None
        """
        ordinals = {
            "first": 0,
            "second": 1,
            "third": 2,
            "fourth": 3,
            "fifth": 4,
            "last": -1,
            "previous": -1
        }

        input_lower = user_input.lower()
        for ordinal_word, position in ordinals.items():
            if ordinal_word in input_lower:
                return position

        return None


# ============================================================================
# PRONOUN RESOLUTION
# ============================================================================

class PronounResolver:
    """
    Resolve pronouns (it, that, this) to actual tasks from conversation context.

    Enables natural multi-turn conversations like:
    - User: "Create 'Buy milk'"
    - AI: "Task created"
    - User: "Mark it complete"  <- "it" refers to 'Buy milk' task
    """

    @staticmethod
    def resolve_pronoun(
        user_input: str,
        recent_tasks: list[dict],
        last_list_result: Optional[list] = None
    ) -> Optional[str]:
        """
        Resolve pronouns to tasks from context.

        Args:
            user_input: User's message
            recent_tasks: List of recently mentioned tasks
            last_list_result: Last task list result (for ordinal references)

        Returns:
            Task ID if resolved, None otherwise
        """
        input_lower = user_input.lower()

        # Check for explicit pronouns
        if any(p in input_lower for p in ["it", "that", "this"]):
            # Most recent task is the antecedent
            if recent_tasks:
                return recent_tasks[-1]["task_id"]

        # Check for ordinal references ("the first", "the second", "the last")
        ordinal = ParameterExtractor.extract_ordinal_position(user_input)
        if ordinal is not None and last_list_result:
            if ordinal == -1:  # "last"
                return last_list_result[-1]["task_id"] if last_list_result else None
            elif 0 <= ordinal < len(last_list_result):
                return last_list_result[ordinal]["task_id"]

        return None


# ============================================================================
# CONFIRMATION FLOW
# ============================================================================

class ConfirmationFlow:
    """
    Handle confirmation flows for destructive operations.

    For delete operations, requires explicit user confirmation before execution.
    """

    @staticmethod
    def requires_confirmation(intent: str) -> bool:
        """
        Check if intent requires user confirmation.

        Args:
            intent: Detected user intent

        Returns:
            True if confirmation required
        """
        return intent == "delete_task"

    @staticmethod
    def format_confirmation_message(task_title: str) -> str:
        """
        Generate confirmation message for delete operation.

        Args:
            task_title: Title of task to be deleted

        Returns:
            Confirmation message text
        """
        return (
            f"I want to make sure - do you want to delete '{task_title}'? "
            f"This action can't be undone. Please say 'yes' or 'no'."
        )

    @staticmethod
    def parse_confirmation(user_response: str) -> Optional[bool]:
        """
        Parse user's confirmation response.

        Args:
            user_response: User's yes/no response

        Returns:
            True if confirmed, False if declined, None if ambiguous
        """
        response_lower = user_response.lower().strip()

        # Explicit confirmation patterns
        if response_lower in ["yes", "y", "confirm", "confirmed", "go ahead", "delete", "proceed"]:
            return True

        # Explicit decline patterns
        if response_lower in ["no", "n", "cancel", "nevermind", "don't", "skip"]:
            return False

        # Ambiguous - requires clarification
        return None


# ============================================================================
# ERROR HANDLER
# ============================================================================

class ErrorHandler:
    """
    Convert tool errors to user-friendly messages.

    Never exposes technical errors to users - always provides helpful,
    actionable guidance for recovery.
    """

    ERROR_MESSAGES = {
        "VALIDATION_ERROR": {
            "empty_title": (
                "I couldn't create that task because the title is empty. "
                "Please tell me what the task is."
            ),
            "title_too_long": (
                "The task title is too long (max 200 characters). "
                "Could you make it shorter?"
            ),
            "description_too_long": (
                "The description is too long (max 2000 characters). "
                "Could you shorten it?"
            ),
            "invalid_status": (
                "I didn't understand that status. "
                "Did you mean 'pending', 'completed', or 'all'?"
            ),
        },
        "NOT_FOUND": {
            "task_not_found": (
                "I couldn't find that task. "
                "Would you like to see all your tasks?"
            ),
            "conversation_not_found": (
                "I couldn't find that conversation. Starting a new one."
            ),
        },
        "AUTHORIZATION_ERROR": {
            "access_denied": (
                "I'm unable to access that task. "
                "Please make sure it's one of your tasks."
            ),
        },
        "INVALID_STATE": {
            "already_completed": "That task is already marked complete.",
        },
        "SERVER_ERROR": {
            "generic": "Sorry, I had trouble with that operation. Please try again.",
            "database_error": (
                "I'm experiencing technical difficulties. "
                "Please try again in a moment."
            ),
            "timeout": "That took too long. Please try again with a simpler request.",
        },
    }

    @classmethod
    def handle_tool_error(
        cls,
        tool_result: dict[str, Any]
    ) -> str:
        """
        Convert tool error to user-friendly message.

        Args:
            tool_result: Result dict from tool execution

        Returns:
            User-friendly error message
        """
        # Log full error for debugging
        logger.error(
            f"Tool execution failed",
            extra={
                "timestamp": datetime.utcnow().isoformat(),
                "result": tool_result,
            },
        )

        # Extract error information
        error_msg = tool_result.get("error", "Unknown error")
        error_type = cls._classify_error(error_msg)

        # Get user-friendly message
        category_messages = cls.ERROR_MESSAGES.get(error_type, {})
        specific_key = cls._get_error_key(error_msg)
        user_message = category_messages.get(
            specific_key,
            cls.ERROR_MESSAGES["SERVER_ERROR"]["generic"]
        )

        return user_message

    @staticmethod
    def _classify_error(error_msg: str) -> str:
        """Classify error type from message."""
        error_lower = error_msg.lower()

        if "empty" in error_lower or "title" in error_lower:
            return "VALIDATION_ERROR"
        if "not found" in error_lower:
            return "NOT_FOUND"
        if "authorized" in error_lower or "access" in error_lower:
            return "AUTHORIZATION_ERROR"
        if "already" in error_lower:
            return "INVALID_STATE"
        if "database" in error_lower:
            return "SERVER_ERROR"

        return "SERVER_ERROR"

    @staticmethod
    def _get_error_key(error_msg: str) -> str:
        """Get specific error key from message."""
        error_lower = error_msg.lower()

        if "empty" in error_lower:
            return "empty_title"
        if "too long" in error_lower and "title" in error_lower:
            return "title_too_long"
        if "too long" in error_lower and "description" in error_lower:
            return "description_too_long"
        if "not found" in error_lower:
            return "task_not_found"
        if "authorized" in error_lower:
            return "access_denied"
        if "already complete" in error_lower:
            return "already_completed"

        return "generic"


# ============================================================================
# AGENT SERVICE
# ============================================================================

class GeminiModelProvider(ModelProvider):
    """Custom model provider that routes to Google Gemini via its OpenAI-compatible API."""

    def __init__(self, model_override: str | None = None):
        api_key = os.environ.get("GEMINI_API_KEY", "")
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        self._model_override = model_override

    def get_model(self, model_name: str | None) -> OpenAIChatCompletionsModel:
        return OpenAIChatCompletionsModel(
            model=self._model_override or model_name or AgentService.MODEL,
            openai_client=self.client,
        )


class AgentService:
    """
    Service for managing OpenAI Agent interactions with MCP tools.

    Provides:
    - Intent detection from natural language
    - Parameter extraction for tool execution
    - Multi-turn conversation context management
    - Pronoun resolution
    - Confirmation flows for destructive operations
    - User-friendly error handling
    - Model rotation for reliability

    Based on Phase III Agent Behavior Specification.
    """

    # Model rotation — try these models in order until one works
    # OpenAI-compatible endpoint supports: gemini-2.0-flash, gemini-1.5-flash,
    # gemini-2.5-flash-preview, gemini-3-flash-preview
    # Different models have different rate limits on free tier
    MODELS = [
        "gemini-2.0-flash",         # Stable, good rate limits
        "gemini-2.5-flash-preview", # Newer, may have lower RPD
        "gemini-1.5-flash",         # Older but reliable
        "gemini-1.5-flash-8b",      # Lightweight, high RPD
    ]
    MODEL = MODELS[0]  # Default model
    TEMPERATURE = 0.7

    # System prompt for the agent
    SYSTEM_PROMPT = """You are a helpful AI assistant that helps users manage their todo tasks through natural conversation.

CRITICAL - CONVERSATION MEMORY:
You will receive conversation history in each message. You MUST:
1. READ and REMEMBER the conversation history provided
2. Use context from previous messages to understand what the user means
3. When user says "this task", "that", "it" - refer to the task mentioned in history
4. NEVER ask "which task?" if a task was just discussed in the history

You can help users with:
1. Add tasks: Create new tasks
2. List tasks: Show pending, completed, or all tasks
3. Complete tasks: Mark tasks as done
4. Delete tasks: Remove tasks (confirm first)
5. Update tasks: Change task details

IMPORTANT - Resolving task references:
- If user says "complete it" after you showed "Buy groceries" → complete "Buy groceries"
- If user says "delete this task" after listing one task → that's the task to delete
- If user mentions a task by name → find and use that task
- ALWAYS check the CONVERSATION HISTORY for context before asking clarifying questions

Guidelines:
- Be conversational and friendly
- Keep responses SHORT and direct
- When a tool succeeds, confirm briefly (e.g., "Done! Task completed.")
- NEVER re-list all tasks if you just showed them - use the history
- Resolve pronouns (it, that, this) from conversation history

Example flow with memory:
[ASSISTANT]: You have one pending task: "Buy groceries"
[USER]: complete it
→ You KNOW "it" = "Buy groceries" from history. Complete that task directly.

[ASSISTANT]: Here are your tasks: 1. Work, 2. Shopping
[USER]: delete the second one
→ You KNOW "second one" = "Shopping" from history. Confirm deletion of "Shopping".
"""

    def __init__(self, session: Session):
        """
        Initialize Agent Service.

        Args:
            session: SQLModel database session
        """
        self.session = session

        # Conversation context state
        self.recent_tasks: list[dict] = []  # Recently mentioned tasks
        self.last_list_result: Optional[list] = None  # Last task list
        self.pending_confirmation: Optional[dict] = None  # Pending destructive operation

    def initialize_agent(self) -> dict[str, Any]:
        """
        Initialize the agent with available tools.

        Returns:
            Dictionary with agent initialization status and available tools
        """
        tool_names = ["add_task", "list_tasks", "complete_task", "delete_task", "update_task"]
        return {
            "status": "initialized",
            "models": self.MODELS,
            "default_model": self.MODEL,
            "temperature": self.TEMPERATURE,
            "tools_count": len(tool_names),
            "tools": tool_names,
        }

    async def process_user_message(
        self,
        user_id: str,
        user_message: str,
        conversation_history: list[dict[str, str]],
    ) -> dict[str, Any]:
        """
        Process a user message through the AI agent with intent detection.

        Args:
            user_id: UUID of the user (string from Better Auth)
            user_message: The user's message text
            conversation_history: List of previous messages with role and content

        Returns:
            Dictionary with agent response, tool calls, and result
        """
        try:
            # Update context from conversation history
            self._update_context_from_history(conversation_history)

            # Check for pending confirmation response
            if self.pending_confirmation:
                return await self._handle_confirmation_response(user_id, user_message)

            # Detect intent
            intent = IntentDetector.detect_intent(user_message)

            # Check if confirmation required (for delete operations)
            if ConfirmationFlow.requires_confirmation(intent):
                return await self._handle_destructive_operation(
                    user_id, user_message, intent
                )

            # Process normal intent using OpenAI Agents SDK
            return await self._process_with_agent(user_id, user_message, conversation_history)

        except Exception as e:
            error_detail = f"{type(e).__name__}: {str(e)[:500]}"
            logger.error(f"Agent processing failed: {error_detail}", exc_info=True)

            # Try fallback for any error (not just rate limits) to provide better UX
            # Detect intent if not already done
            try:
                detected_intent = locals().get("intent") or IntentDetector.detect_intent(user_message)
            except Exception:
                detected_intent = "unknown"

            # Try fallback execution
            try:
                fallback_result = await self._fallback_direct_execution(user_id, user_message, detected_intent)
                if fallback_result:
                    return fallback_result
            except Exception as fallback_err:
                logger.error(f"Fallback also failed: {fallback_err}")

            # Return a user-friendly error, not technical details
            return {
                "success": True,  # Mark as success so frontend shows the message
                "assistant_message": "I'm sorry, I had trouble processing that request. Could you please try again or rephrase your request?",
                "tool_calls": [],
            }

    async def _fallback_direct_execution(
        self,
        user_id: str,
        user_message: str,
        intent: str,
    ) -> Optional[dict[str, Any]]:
        """
        Fallback to direct tool execution when rate limited.
        Bypasses the AI agent and executes tools directly based on intent.
        """
        try:
            mcp_service = MCPToolsService(self.session)

            if intent == "add_task":
                # Extract title from message (simple extraction)
                title = user_message
                for prefix in ["add a task to ", "add task to ", "add a task ", "add task ",
                               "create a task to ", "create task to ", "create a task ", "create task ",
                               "new task to ", "new task ", "remember to ", "remind me to "]:
                    if user_message.lower().startswith(prefix):
                        title = user_message[len(prefix):].strip()
                        break

                # Clean up the title
                title = title.strip('"\'').capitalize()
                if not title:
                    title = user_message

                result = mcp_service.add_task(user_id=user_id, title=title)
                if result.get("success"):
                    task = result["task"]
                    return {
                        "success": True,
                        "assistant_message": f"Done! I've added '{task['title']}' to your tasks.",
                        "tool_calls": [{"id": str(uuid.uuid4()), "name": "add_task", "result": result}],
                    }

            elif intent == "list_tasks":
                # Determine filter from message
                is_complete = None
                if "completed" in user_message.lower() or "done" in user_message.lower():
                    is_complete = True
                elif "pending" in user_message.lower() or "incomplete" in user_message.lower():
                    is_complete = False

                result = mcp_service.list_tasks(user_id=user_id, is_complete=is_complete)
                if result.get("success"):
                    tasks = result["tasks"]
                    if not tasks:
                        return {
                            "success": True,
                            "assistant_message": "You don't have any tasks yet. Would you like to create one?",
                            "tool_calls": [{"id": str(uuid.uuid4()), "name": "list_tasks", "result": result}],
                        }

                    task_list = "\n".join([f"• {t['title']}" + (" ✓" if t['is_complete'] else "") for t in tasks[:10]])
                    return {
                        "success": True,
                        "assistant_message": f"Here are your tasks ({len(tasks)} total):\n{task_list}",
                        "tool_calls": [{"id": str(uuid.uuid4()), "name": "list_tasks", "result": result}],
                    }

            elif intent == "complete_task":
                # Try to find task by name in message
                result = mcp_service.list_tasks(user_id=user_id, is_complete=False)
                if result.get("success") and result["tasks"]:
                    # Find matching task
                    for task in result["tasks"]:
                        if task["title"].lower() in user_message.lower():
                            complete_result = mcp_service.complete_task(user_id=user_id, task_id=uuid.UUID(task["id"]))
                            if complete_result.get("success"):
                                return {
                                    "success": True,
                                    "assistant_message": f"Done! '{task['title']}' is now marked complete.",
                                    "tool_calls": [{"id": str(uuid.uuid4()), "name": "complete_task", "result": complete_result}],
                                }

            elif intent == "update_task":
                # Get all tasks to find the one to update
                result = mcp_service.list_tasks(user_id=user_id)
                if result.get("success") and result["tasks"]:
                    tasks = result["tasks"]
                    user_msg_lower = user_message.lower()

                    # Try to find which task to update by name
                    matched_task = None
                    for task in tasks:
                        if task["title"].lower() in user_msg_lower:
                            matched_task = task
                            break

                    # Also check recent_tasks for context
                    if not matched_task and self.recent_tasks:
                        recent_id = self.recent_tasks[-1].get("task_id")
                        for task in tasks:
                            if task["id"] == recent_id:
                                matched_task = task
                                break

                    if matched_task:
                        # Try to extract what to update from the message
                        new_title = None
                        new_description = None

                        # Extract new title patterns
                        title_patterns = [
                            r"(?:change|rename|update).*?(?:title|name|task)?\s*(?:to|as)\s+['\"]?([^'\"]+?)['\"]?(?:\s+(?:and|with|,)|$)",
                            r"(?:to|as)\s+['\"]?(.+?)['\"]?\s+task",
                            r"title\s*(?:to|:)\s*['\"]?([^'\"]+)['\"]?",
                        ]
                        for pattern in title_patterns:
                            match = re.search(pattern, user_message, re.IGNORECASE)
                            if match:
                                new_title = match.group(1).strip().strip('"\'')
                                break

                        # Extract description patterns
                        desc_patterns = [
                            r"description\s*(?:to|:)\s*['\"]?([^'\"]+)['\"]?",
                            r"(?:and\s+)?description\s+['\"]?([^'\"]+)['\"]?",
                        ]
                        for pattern in desc_patterns:
                            match = re.search(pattern, user_message, re.IGNORECASE)
                            if match:
                                new_description = match.group(1).strip().strip('"\'')
                                break

                        # If we found something to update, do it
                        if new_title or new_description:
                            update_result = mcp_service.update_task(
                                user_id=user_id,
                                task_id=uuid.UUID(matched_task["id"]),
                                title=new_title,
                                description=new_description,
                            )
                            if update_result.get("success"):
                                updated_task = update_result["task"]
                                changes = []
                                if new_title:
                                    changes.append(f"title to **\"{new_title}\"**")
                                if new_description:
                                    changes.append(f"description to \"{new_description}\"")
                                return {
                                    "success": True,
                                    "assistant_message": f"Done! I've updated the task:\n- Changed {' and '.join(changes)}\n\nAnything else you'd like to change?",
                                    "tool_calls": [{"id": str(uuid.uuid4()), "name": "update_task", "result": update_result}],
                                }

                        # Couldn't parse what to update, ask for clarification
                        return {
                            "success": True,
                            "assistant_message": f"I found **\"{matched_task['title']}\"**. What would you like to change?\n\nExamples:\n- \"Change title to Go to Gym\"\n- \"Update description to I need to exercise\"\n- \"Mark as complete\"",
                            "tool_calls": [{"id": str(uuid.uuid4()), "name": "list_tasks", "result": result}],
                        }
                    else:
                        # Show tasks and ask which one
                        task_list = "\n".join([f"• {t['title']}" for t in tasks[:5]])
                        return {
                            "success": True,
                            "assistant_message": f"Which task would you like to update?\n\n{task_list}\n\nTry: \"Change [task name] title to [new title]\"",
                            "tool_calls": [{"id": str(uuid.uuid4()), "name": "list_tasks", "result": result}],
                        }

            elif intent == "unknown":
                # For unknown intents, provide helpful response
                # Note: This is fallback mode, indicate reduced capability
                return {
                    "success": True,
                    "assistant_message": "I'm currently in basic mode. Here's what I can help with:\n\n• **Add**: \"Add task [name]\"\n• **List**: \"Show my tasks\"\n• **Complete**: \"Complete [task name]\"\n• **Delete**: \"Delete [task name]\"\n• **Update**: \"Change [task name] title to [new title]\"\n\nPlease use simple, direct commands.",
                    "tool_calls": [],
                }

            # Handle greetings and conversation in fallback
            greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
            if any(g in user_message.lower() for g in greetings):
                # Extract name if mentioned
                name_match = re.search(r"(?:my name is|i'm|i am)\s+([A-Za-z]+)", user_message, re.IGNORECASE)
                name = name_match.group(1) if name_match else ""
                greeting_response = f"Hello{' ' + name if name else ''}! " if name else "Hello! "
                return {
                    "success": True,
                    "assistant_message": f"{greeting_response}I'm your task assistant. I can help you add, view, complete, update, or delete tasks. What would you like to do?",
                    "tool_calls": [],
                }

            return None  # Fallback didn't handle it

        except Exception as fallback_error:
            logger.error(f"Fallback execution failed: {fallback_error}")
            return None

    def _update_context_from_history(
        self,
        conversation_history: list[dict[str, str]]
    ) -> None:
        """
        Update agent context from conversation history.

        Args:
            conversation_history: List of previous messages
        """
        # Reset context
        self.recent_tasks = []
        self.last_list_result = None
        self.pending_confirmation = None

        # Extract recent tasks from tool calls in history
        for msg in conversation_history[-10:]:  # Last 10 messages for better context
            if msg.get("tool_calls"):
                for tool_call in msg["tool_calls"]:
                    # Check for pending confirmation marker
                    tool_name = tool_call.get("name") or tool_call.get("function", {}).get("name", "")
                    if tool_name == "pending_delete_confirmation":
                        # Restore pending confirmation from history
                        result_data = tool_call.get("result") or tool_call.get("function", {}).get("result", {})
                        if isinstance(result_data, str):
                            try:
                                result_data = json.loads(result_data)
                            except json.JSONDecodeError:
                                continue
                        self.pending_confirmation = {
                            "tool": "delete_task",
                            "task_id": result_data.get("task_id"),
                            "task_title": result_data.get("task_title"),
                        }
                        continue

                    # Result can be in tool_call.result or tool_call.function.result
                    result_data = tool_call.get("result") or tool_call.get("function", {}).get("result", {})
                    if isinstance(result_data, str):
                        try:
                            result_data = json.loads(result_data)
                        except json.JSONDecodeError:
                            continue

                    if result_data.get("success"):
                        # Extract task info from successful tool calls
                        if "task" in result_data:
                            task = result_data["task"]
                            self.recent_tasks.append({
                                "task_id": task.get("id"),
                                "title": task.get("title"),
                            })

                        # Store list results for ordinal reference AND recent_tasks
                        if "tasks" in result_data:
                            self.last_list_result = result_data["tasks"]
                            # Add listed tasks to recent_tasks for pronoun resolution
                            # e.g., "delete this task" after showing 1 task
                            for listed_task in result_data["tasks"]:
                                self.recent_tasks.append({
                                    "task_id": listed_task.get("id"),
                                    "title": listed_task.get("title"),
                                })

    async def _handle_destructive_operation(
        self,
        user_id: str,
        user_message: str,
        intent: str
    ) -> dict[str, Any]:
        """
        Handle destructive operation with confirmation flow.

        Args:
            user_id: UUID of the user
            user_message: User's message
            intent: Detected intent (should be 'delete_task')

        Returns:
            Response requesting confirmation or executing deletion
        """
        # First, get user's tasks to find the one they want to delete
        mcp_service = MCPToolsService(self.session)
        tasks_result = mcp_service.list_tasks(user_id=user_id)

        if not tasks_result.get("success") or not tasks_result.get("tasks"):
            return {
                "success": True,
                "assistant_message": "You don't have any tasks to delete. Would you like to create one?",
                "tool_calls": [],
            }

        tasks = tasks_result["tasks"]
        user_msg_lower = user_message.lower()

        # Try to find the task by name match
        matched_task = None
        for task in tasks:
            task_title_lower = task["title"].lower()
            # Check if task title is mentioned in the message
            if task_title_lower in user_msg_lower:
                matched_task = task
                break

        # Also check recent_tasks for pronoun resolution ("this task", "that one")
        if not matched_task and self.recent_tasks:
            if any(p in user_msg_lower for p in ["this", "that", "it"]):
                # Use the most recently mentioned task
                recent_task_id = self.recent_tasks[-1].get("task_id")
                for task in tasks:
                    if task["id"] == recent_task_id:
                        matched_task = task
                        break

        if not matched_task:
            # Couldn't identify task, ask user to specify
            task_list = "\n".join([f"- **{t['title']}**" for t in tasks])
            return {
                "success": True,
                "assistant_message": f"Which task would you like to delete?\n\n{task_list}\n\nPlease tell me the task name.",
                "tool_calls": [],
            }

        # Found the task, ask for confirmation and store pending confirmation in tool_calls
        # This will be persisted to DB and restored on next message
        return {
            "success": True,
            "assistant_message": f"Are you sure you want to delete the task **\"{matched_task['title']}\"**? This cannot be undone. Reply 'yes' to confirm or 'no' to cancel.",
            "tool_calls": [{
                "id": str(uuid.uuid4()),
                "name": "pending_delete_confirmation",
                "result": {
                    "task_id": matched_task["id"],
                    "task_title": matched_task["title"],
                    "awaiting_confirmation": True,
                },
            }],
            "requires_confirmation": True,
        }

    async def _handle_confirmation_response(
        self,
        user_id: str,
        user_response: str
    ) -> dict[str, Any]:
        """
        Handle user's confirmation response for pending destructive operation.

        Args:
            user_id: UUID of the user
            user_response: User's yes/no response

        Returns:
            Response after executing or canceling pending operation
        """
        if not self.pending_confirmation:
            return {
                "success": False,
                "error": "No pending confirmation",
            }

        # Parse confirmation
        confirmed = ConfirmationFlow.parse_confirmation(user_response)

        if confirmed is None:
            # Ambiguous response - keep the pending confirmation and ask again
            task_title = self.pending_confirmation.get("task_title", "the task")
            return {
                "success": True,
                "assistant_message": f"I need a clear answer. Do you want to delete **\"{task_title}\"**? Please reply 'yes' or 'no'.",
                "tool_calls": [{
                    "id": str(uuid.uuid4()),
                    "name": "pending_delete_confirmation",
                    "result": {
                        "task_id": self.pending_confirmation.get("task_id"),
                        "task_title": task_title,
                        "awaiting_confirmation": True,
                    },
                }],
                "requires_confirmation": True,
            }

        if not confirmed:
            # User declined - clear pending
            return {
                "success": True,
                "assistant_message": "No problem! I've kept the task. Is there anything else I can help with?",
                "tool_calls": [],
            }

        # User confirmed - execute deletion directly using the stored task_id
        task_id = self.pending_confirmation.get("task_id")
        task_title = self.pending_confirmation.get("task_title", "the task")

        if not task_id:
            return {
                "success": True,
                "assistant_message": "Sorry, I lost track of which task to delete. Could you please tell me again?",
                "tool_calls": [],
            }

        # Execute the deletion
        mcp_service = MCPToolsService(self.session)
        try:
            result = mcp_service.delete_task(
                user_id=user_id,
                task_id=uuid.UUID(task_id),
            )

            if result.get("success"):
                return {
                    "success": True,
                    "assistant_message": f"Done! I've deleted **\"{task_title}\"**. Is there anything else you'd like me to help with?",
                    "tool_calls": [{
                        "id": str(uuid.uuid4()),
                        "name": "delete_task",
                        "result": result,
                    }],
                }
            else:
                return {
                    "success": True,
                    "assistant_message": f"Sorry, I couldn't delete the task: {result.get('error', 'Unknown error')}",
                    "tool_calls": [],
                }
        except Exception as e:
            logger.error(f"Failed to delete task: {e}")
            return {
                "success": True,
                "assistant_message": "Sorry, something went wrong while deleting the task. Please try again.",
                "tool_calls": [],
            }

    async def _process_with_agent(
        self,
        user_id: str,
        user_message: str,
        conversation_history: list[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """
        Process user message using OpenAI Agents SDK.

        Args:
            user_id: UUID of the user
            user_message: User's message
            conversation_history: Previous messages for context

        Returns:
            Agent response with tool calls
        """
        # Create context for this run
        context = AgentContext(
            session=self.session,
            user_id=user_id,
            recent_tasks=self.recent_tasks,
            last_list_result=self.last_list_result,
            pending_confirmation=self.pending_confirmation,
        )

        # Build comprehensive context from conversation history
        history_context = ""
        if conversation_history and len(conversation_history) > 1:
            # Get recent messages (excluding current message which is last)
            recent_history = conversation_history[:-1][-10:]  # Last 10, excluding current

            if recent_history:
                # Build a clear conversation transcript
                history_parts = []
                for msg in recent_history:
                    role = "USER" if msg["role"] == "user" else "ASSISTANT"
                    content = msg["content"]
                    history_parts.append(f"[{role}]: {content}")

                history_context = """=== CONVERSATION HISTORY (You MUST remember this context) ===
{}
=== END OF HISTORY ===

""".format("\n".join(history_parts))

        # Build task context - tasks that were recently mentioned or shown
        task_context = ""
        if self.recent_tasks:
            task_list = ", ".join([f"'{t['title']}'" for t in self.recent_tasks[-5:]])
            task_context = f"\n[CONTEXT: Recently discussed tasks: {task_list}]\n"

        if self.last_list_result:
            shown_tasks = ", ".join([f"'{t['title']}'" for t in self.last_list_result[:5]])
            task_context += f"[CONTEXT: Tasks shown to user: {shown_tasks}]\n"

        # Build the full input with all context
        full_input = f"""{history_context}{task_context}
Current user message: {user_message}

IMPORTANT: Use the conversation history above to understand what the user is referring to. If they say "this task", "that", "it", etc., refer to the task(s) mentioned in the history."""

        # Run the agent with model rotation — try each model until one works
        result = None
        last_error = None
        for model_name in self.MODELS:
            try:
                logger.info(f"Trying model: {model_name}")
                # Create agent and config for this specific model
                agent = Agent[AgentContext](
                    name="TodoAssistant",
                    instructions=self.SYSTEM_PROMPT,
                    tools=[add_task, list_tasks, complete_task, delete_task, update_task],
                    model=model_name,
                )
                run_config = RunConfig(
                    model_provider=GeminiModelProvider(model_override=model_name),
                )
                result = await Runner.run(
                    starting_agent=agent,
                    input=full_input,
                    context=context,
                    run_config=run_config,
                )
                logger.info(f"Model {model_name} succeeded")
                break  # Success, stop trying
            except Exception as model_err:
                err_str = str(model_err).lower()
                last_error = model_err
                # Retry on rate limit or model not found errors
                if any(keyword in err_str for keyword in [
                    "429", "rate limit", "resource exhausted",
                    "404", "not found", "does not exist",
                    "quota", "exceeded",
                ]):
                    logger.warning(f"Model {model_name} failed ({type(model_err).__name__}), trying next...")
                    continue
                else:
                    # Non-retryable error, propagate
                    raise

        if result is None:
            raise last_error or RuntimeError("All models failed")

        # Extract tool calls from the result
        tool_calls = []
        if hasattr(result, 'to_input_list'):
            # Convert result to input list to extract tool calls
            for item in result.to_input_list():
                if hasattr(item, 'content') and hasattr(item.content, 'text'):
                    # Check if this is a tool call response
                    try:
                        content_data = json.loads(item.content.text)
                        if content_data.get("success"):
                            tool_calls.append({
                                "id": str(uuid.uuid4()),
                                "name": "tool_call",
                                "result": content_data,
                            })
                            # Update context with successful tool result
                            if "task" in content_data:
                                self.recent_tasks.append({
                                    "task_id": content_data["task"]["id"],
                                    "title": content_data["task"]["title"],
                                })
                            elif "tasks" in content_data:
                                self.last_list_result = content_data["tasks"]
                    except (json.JSONDecodeError, AttributeError):
                        pass

        return {
            "success": True,
            "assistant_message": result.final_output,
            "tool_calls": tool_calls,
        }

    def format_tool_calls_for_storage(
        self,
        tool_calls: list[dict[str, Any]],
    ) -> Optional[dict[str, Any]]:
        """
        Format tool calls for storage in database (Message.tool_calls).

        Args:
            tool_calls: List of tool call results

        Returns:
            Dictionary suitable for JSON storage, or None if no tool calls
        """
        if not tool_calls:
            return None

        return {
            "tool_calls": [
                {
                    "id": tc["id"],
                    "type": "function",
                    "function": {
                        "name": tc["name"],
                        "result": json.dumps(tc["result"]) if isinstance(tc["result"], dict) else tc["result"],
                    },
                }
                for tc in tool_calls
            ]
        }


def create_agent_service(session: Session) -> AgentService:
    """
    Factory function to create AgentService instance.

    Args:
        session: SQLModel database session

    Returns:
        Initialized AgentService instance
    """
    return AgentService(session)
