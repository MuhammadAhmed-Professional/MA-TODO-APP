"""
Conversation State Service

Manages conversation state for AI-powered features using Dapr state store.
Stores chat history, context, and user preferences for task assistance.

Use Cases:
- Chat history for AI task assistant
- Task suggestions based on context
- Natural language task creation
- Conversation-based task search
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel

from src.services.state_service import StateService, get_state_service

logger = logging.getLogger(__name__)


# ================== MODELS ==================


class ConversationMessage(BaseModel):
    """Single message in a conversation."""

    id: str
    role: str  # "user" or "assistant"
    content: str
    timestamp: str
    metadata: Dict[str, Any] = {}


class ConversationContext(BaseModel):
    """Conversation context for AI features."""

    conversation_id: str
    user_id: str
    messages: List[ConversationMessage]
    created_at: str
    updated_at: str
    metadata: Dict[str, Any] = {}


class ConversationState(BaseModel):
    """User conversation state and preferences."""

    user_id: str
    preferences: Dict[str, Any] = {}
    recent_tasks: List[str] = []  # Recent task IDs for context
    recent_categories: List[str] = []  # Recent category IDs
    metadata: Dict[str, Any] = {}


# ================== SERVICE ==================


class ConversationStateService:
    """
    Service for managing conversation state.

    Stores conversation history, context, and user preferences
    using Dapr state store for AI-powered features.
    """

    def __init__(self, state_service: Optional[StateService] = None):
        """
        Initialize conversation state service.

        Args:
            state_service: Optional StateService instance
        """
        self.state_service = state_service

    async def _get_state_service(self) -> StateService:
        """Get state service (lazy initialization)."""
        if self.state_service is None:
            self.state_service = await get_state_service()
        return self.state_service

    # ================== CONVERSATION MANAGEMENT ==================

    async def create_conversation(
        self,
        user_id: str,
        initial_metadata: Optional[Dict[str, Any]] = None,
    ) -> ConversationContext:
        """
        Create a new conversation context.

        Args:
            user_id: User ID
            initial_metadata: Optional initial metadata

        Returns:
            New conversation context
        """
        conversation_id = str(uuid4())
        now = datetime.utcnow().isoformat()

        context = ConversationContext(
            conversation_id=conversation_id,
            user_id=user_id,
            messages=[],
            created_at=now,
            updated_at=now,
            metadata=initial_metadata or {},
        )

        # Save to state store with 24-hour TTL
        await self._save_context(context, ttl_seconds=86400)
        logger.info(f"Created conversation {conversation_id} for user {user_id}")

        return context

    async def get_conversation(self, conversation_id: str) -> Optional[ConversationContext]:
        """
        Get a conversation context.

        Args:
            conversation_id: Conversation ID

        Returns:
            Conversation context or None
        """
        state_service = await self._get_state_service()
        data = await state_service.get(f"conversation:{conversation_id}")

        if data:
            return ConversationContext.model_validate(data)
        return None

    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[ConversationContext]:
        """
        Add a message to a conversation.

        Args:
            conversation_id: Conversation ID
            role: Message role ("user" or "assistant")
            content: Message content
            metadata: Optional message metadata

        Returns:
            Updated conversation context or None
        """
        context = await self.get_conversation(conversation_id)
        if not context:
            logger.warning(f"Conversation {conversation_id} not found")
            return None

        # Create message
        message = ConversationMessage(
            id=str(uuid4()),
            role=role,
            content=content,
            timestamp=datetime.utcnow().isoformat(),
            metadata=metadata or {},
        )

        # Add to context
        context.messages.append(message)
        context.updated_at = datetime.utcnow().isoformat()

        # Save updated context
        await self._save_context(context)
        logger.debug(f"Added {role} message to conversation {conversation_id}")

        return context

    async def get_messages(
        self,
        conversation_id: str,
        limit: Optional[int] = None,
    ) -> List[ConversationMessage]:
        """
        Get messages from a conversation.

        Args:
            conversation_id: Conversation ID
            limit: Optional limit on number of messages (most recent first)

        Returns:
            List of messages
        """
        context = await self.get_conversation(conversation_id)
        if not context:
            return []

        messages = context.messages
        if limit:
            messages = messages[-limit:]

        return messages

    async def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation context.

        Args:
            conversation_id: Conversation ID

        Returns:
            True if delete succeeded
        """
        state_service = await self._get_state_service()
        success = await state_service.delete(f"conversation:{conversation_id}")

        if success:
            logger.info(f"Deleted conversation {conversation_id}")

        return success

    async def _save_context(
        self,
        context: ConversationContext,
        ttl_seconds: int = 86400,
    ) -> bool:
        """
        Save conversation context to state store.

        Args:
            context: Conversation context
            ttl_seconds: TTL in seconds (default: 24 hours)

        Returns:
            True if save succeeded
        """
        state_service = await self._get_state_service()
        return await state_service.set_model(
            f"conversation:{context.conversation_id}",
            context,
            ttl_seconds=ttl_seconds,
        )

    # ================== USER PREFERENCES ==================

    async def get_user_state(self, user_id: str) -> ConversationState:
        """
        Get user conversation state (create if not exists).

        Args:
            user_id: User ID

        Returns:
            User conversation state
        """
        state_service = await self._get_state_service()
        data = await state_service.get(f"user_state:{user_id}")

        if data:
            return ConversationState.model_validate(data)

        # Create new state
        return ConversationState(user_id=user_id)

    async def update_user_state(
        self,
        user_id: str,
        preferences: Optional[Dict[str, Any]] = None,
        recent_tasks: Optional[List[str]] = None,
        recent_categories: Optional[List[str]] = None,
    ) -> bool:
        """
        Update user conversation state.

        Args:
            user_id: User ID
            preferences: Updated preferences
            recent_tasks: Recent task IDs
            recent_categories: Recent category IDs

        Returns:
            True if update succeeded
        """
        state = await self.get_user_state(user_id)

        if preferences:
            state.preferences.update(preferences)
        if recent_tasks is not None:
            state.recent_tasks = recent_tasks
        if recent_categories is not None:
            state.recent_categories = recent_categories

        state_service = await self._get_state_service()
        return await state_service.set_model(
            f"user_state:{user_id}",
            state,
            ttl_seconds=604800,  # 7 days
        )

    async def add_recent_task(self, user_id: str, task_id: str) -> bool:
        """
        Add a task to user's recent tasks.

        Args:
            user_id: User ID
            task_id: Task ID

        Returns:
            True if update succeeded
        """
        state = await self.get_user_state(user_id)

        # Add to front, keep only last 10
        if task_id in state.recent_tasks:
            state.recent_tasks.remove(task_id)
        state.recent_tasks.insert(0, task_id)
        state.recent_tasks = state.recent_tasks[:10]

        state_service = await self._get_state_service()
        return await state_service.set_model(
            f"user_state:{user_id}",
            state,
            ttl_seconds=604800,
        )

    # ================== CONTEXT FOR AI ==================

    async def get_conversation_context_for_ai(
        self,
        conversation_id: str,
        user_id: str,
    ) -> Dict[str, Any]:
        """
        Get full context for AI assistant.

        Combines conversation messages with user state and recent activity.

        Args:
            conversation_id: Conversation ID
            user_id: User ID

        Returns:
            Context dictionary for AI
        """
        # Get conversation
        conversation = await self.get_conversation(conversation_id)

        # Get user state
        user_state = await self.get_user_state(user_id)

        # Build context
        context = {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "messages": [m.model_dump() for m in (conversation.messages if conversation else [])],
            "user_preferences": user_state.preferences,
            "recent_tasks": user_state.recent_tasks,
            "recent_categories": user_state.recent_categories,
        }

        return context


# Global instance
_conversation_service_instance: Optional[ConversationStateService] = None


async def get_conversation_service() -> ConversationStateService:
    """
    Get global conversation service instance (FastAPI dependency).

    Returns:
        Shared ConversationStateService instance
    """
    global _conversation_service_instance
    if _conversation_service_instance is None:
        _conversation_service_instance = ConversationStateService()
    return _conversation_service_instance
