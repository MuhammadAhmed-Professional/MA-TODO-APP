"""
State Management Service

Wrapper around Dapr state API for caching and state storage.
Provides type-safe methods for common state operations.

State Store Usage:
- Task data caching (reduce database queries)
- Conversation state (chat history for AI features)
- User session state
- Rate limiting counters
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, TypeVar

from pydantic import BaseModel
from src.services.dapr_client import DaprClient, get_dapr_client

logger = logging.getLogger(__name__)

# Dapr state store component name
STATE_STORE_NAME = "postgres-statestore"

# Type variable for generic methods
T = TypeVar("T", bound=BaseModel)


class StateService:
    """
    Service for managing application state via Dapr.

    Provides caching, session management, and temporary storage
    using Dapr's state management building block.
    """

    def __init__(self, dapr_client: Optional[DaprClient] = None):
        """
        Initialize state service.

        Args:
            dapr_client: Optional DaprClient instance
        """
        self.dapr_client = dapr_client

    async def _get_client(self) -> DaprClient:
        """Get Dapr client (lazy initialization)."""
        if self.dapr_client is None:
            self.dapr_client = await get_dapr_client()
        return self.dapr_client

    # ================== BASIC STATE OPERATIONS ==================

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from state store.

        Args:
            key: State key

        Returns:
            Value or None if not found
        """
        try:
            client = await self._get_client()
            value = await client.get_state(STATE_STORE_NAME, key)
            return value
        except Exception as e:
            logger.error(f"Error getting state for key {key}: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
        etag: Optional[str] = None,
    ) -> bool:
        """
        Set a value in state store.

        Args:
            key: State key
            value: Value to store (JSON-serializable)
            ttl_seconds: Optional time-to-live in seconds
            etag: Optional entity tag for optimistic concurrency

        Returns:
            True if set succeeded
        """
        try:
            client = await self._get_client()
            metadata = {}
            if ttl_seconds:
                metadata["ttlInSeconds"] = str(ttl_seconds)
            if etag:
                metadata["etag"] = etag

            return await client.save_state(
                STATE_STORE_NAME,
                key,
                value,
                metadata=metadata if metadata else None,
            )
        except Exception as e:
            logger.error(f"Error setting state for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete a value from state store.

        Args:
            key: State key to delete

        Returns:
            True if delete succeeded
        """
        try:
            client = await self._get_client()
            return await client.delete_state(STATE_STORE_NAME, key)
        except Exception as e:
            logger.error(f"Error deleting state for key {key}: {e}")
            return False

    # ================== TYPE-SAFE OPERATIONS ==================

    async def get_model(self, key: str, model_class: type[T]) -> Optional[T]:
        """
        Get a value and parse as Pydantic model.

        Args:
            key: State key
            model_class: Pydantic model class to parse into

        Returns:
            Parsed model instance or None
        """
        value = await self.get(key)
        if value is None:
            return None
        try:
            return model_class.model_validate(value)
        except Exception as e:
            logger.error(f"Error parsing model for key {key}: {e}")
            return None

    async def set_model(
        self,
        key: str,
        model: BaseModel,
        ttl_seconds: Optional[int] = None,
    ) -> bool:
        """
        Store a Pydantic model in state store.

        Args:
            key: State key
            model: Pydantic model instance
            ttl_seconds: Optional TTL

        Returns:
            True if set succeeded
        """
        return await self.set(key, model.model_dump(), ttl_seconds=ttl_seconds)

    # ================== BULK OPERATIONS ==================

    async def get_multiple(self, keys: List[str]) -> Dict[str, Any]:
        """
        Get multiple values from state store.

        Args:
            keys: List of state keys

        Returns:
            Dictionary mapping keys to values
        """
        results = {}
        for key in keys:
            value = await self.get(key)
            if value is not None:
                results[key] = value
        return results

    async def set_multiple(
        self,
        items: Dict[str, Any],
        ttl_seconds: Optional[int] = None,
    ) -> bool:
        """
        Set multiple values in state store.

        Args:
            items: Dictionary of key-value pairs
            ttl_seconds: Optional TTL for all items

        Returns:
            True if all sets succeeded
        """
        all_success = True
        for key, value in items.items():
            success = await self.set(key, value, ttl_seconds=ttl_seconds)
            if not success:
                all_success = False
        return all_success

    # ================== TASK CACHING ==================

    async def cache_task(self, task_id: str, task_data: Dict[str, Any], ttl: int = 3600) -> bool:
        """
        Cache task data in state store.

        Args:
            task_id: Task ID
            task_data: Task data dictionary
            ttl: Cache TTL in seconds (default: 1 hour)

        Returns:
            True if cache succeeded
        """
        return await self.set(
            f"task:{task_id}",
            task_data,
            ttl_seconds=ttl,
        )

    async def get_cached_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached task data.

        Args:
            task_id: Task ID

        Returns:
            Cached task data or None
        """
        return await self.get(f"task:{task_id}")

    async def invalidate_task_cache(self, task_id: str) -> bool:
        """
        Invalidate cached task data.

        Args:
            task_id: Task ID

        Returns:
            True if invalidation succeeded
        """
        return await self.delete(f"task:{task_id}")

    # ================== RATE LIMITING ==================

    async def increment_counter(
        self,
        key: str,
        window_seconds: int = 60,
    ) -> int:
        """
        Increment a rate limit counter.

        Args:
            key: Counter key (e.g., "rate_limit:user:123")
            window_seconds: Time window in seconds

        Returns:
            Current counter value
        """
        # Get current value
        current = await self.get(key)
        if current is None:
            current = 0
        else:
            current = int(current)

        # Increment and save with TTL
        new_value = current + 1
        await self.set(key, new_value, ttl_seconds=window_seconds)

        return new_value

    async def check_rate_limit(
        self,
        key: str,
        limit: int,
        window_seconds: int = 60,
    ) -> bool:
        """
        Check if rate limit is exceeded.

        Args:
            key: Rate limit key
            limit: Maximum requests allowed
            window_seconds: Time window in seconds

        Returns:
            True if under limit, False if exceeded
        """
        current = await self.increment_counter(key, window_seconds)
        return current <= limit

    # ================== SESSION STATE ==================

    async def set_session(
        self,
        session_id: str,
        user_id: str,
        data: Dict[str, Any],
        ttl_seconds: int = 3600,
    ) -> bool:
        """
        Store user session data.

        Args:
            session_id: Session ID
            user_id: User ID
            data: Session data
            ttl_seconds: Session TTL (default: 1 hour)

        Returns:
            True if set succeeded
        """
        session_data = {
            "user_id": user_id,
            "data": data,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(seconds=ttl_seconds)).isoformat(),
        }
        return await self.set(f"session:{session_id}", session_data, ttl_seconds=ttl_seconds)

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user session data.

        Args:
            session_id: Session ID

        Returns:
            Session data or None
        """
        return await self.get(f"session:{session_id}")

    async def delete_session(self, session_id: str) -> bool:
        """
        Delete user session.

        Args:
            session_id: Session ID

        Returns:
            True if delete succeeded
        """
        return await self.delete(f"session:{session_id}")


# Global state service instance
_state_service_instance: Optional[StateService] = None


async def get_state_service() -> StateService:
    """
    Get global state service instance (FastAPI dependency).

    Returns:
        Shared StateService instance
    """
    global _state_service_instance
    if _state_service_instance is None:
        _state_service_instance = StateService()
    return _state_service_instance
