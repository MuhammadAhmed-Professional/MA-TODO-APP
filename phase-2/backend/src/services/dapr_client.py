"""
Dapr Client Service

Wrapper for Dapr sidecar HTTP API:
- Publish/subscribe to Kafka topics via Dapr pub/sub
- State management with PostgreSQL state store
- Secret retrieval from Kubernetes secret store
- Service-to-service invocation
"""

import json
import logging
import os
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)


class DaprClient:
    """
    Client for interacting with Dapr sidecar via HTTP API.

    Dapr sidecar runs alongside the application and provides:
    - Pub/sub abstraction over Kafka
    - State store abstraction over PostgreSQL
    - Secret management via Kubernetes secrets
    - Service invocation with retries and circuit breakers
    """

    def __init__(
        self,
        dapr_http_port: int = 3500,
        app_id: str = "todo-backend",
    ):
        """
        Initialize Dapr client.

        Args:
            dapr_http_port: Port where Dapr sidecar HTTP API is exposed (default: 3500)
            app_id: Application identifier for Dapr
        """
        self.dapr_http_port = int(os.getenv("DAPR_HTTP_PORT", dapr_http_port))
        self.app_id = app_id
        self.base_url = f"http://localhost:{self.dapr_http_port}"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

    # ================== PUB/SUB ==================

    async def publish_event(
        self,
        pubsub_name: str,
        topic: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None,
    ) -> bool:
        """
        Publish an event to a Kafka topic via Dapr pub/sub.

        Args:
            pubsub_name: Pub/sub component name (e.g., 'kafka-pubsub')
            topic: Topic name (e.g., 'task-events')
            data: Event payload (JSON-serializable)
            metadata: Optional metadata (headers, etc.)

        Returns:
            True if publish succeeded, False otherwise
        """
        url = f"{self.base_url}/v1.0/publish/{pubsub_name}/{topic}"

        try:
            response = await self.client.post(
                url,
                json=data,
                headers={"Content-Type": "application/json"},
                params=metadata or {},
            )

            if response.status_code == 204:
                logger.debug(f"Published event to {topic} via Dapr")
                return True
            else:
                logger.error(
                    f"Failed to publish event: {response.status_code} {response.text}"
                )
                return False

        except httpx.HTTPError as e:
            logger.error(f"HTTP error publishing event: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error publishing event: {e}", exc_info=True)
            return False

    async def subscribe_to_topic(
        self,
        pubsub_name: str,
        topic: str,
        route: str,
    ) -> Dict[str, Any]:
        """
        Register subscription configuration (for Dapr runtime).

        Note: This method returns subscription metadata.
        Actual message handling is done via FastAPI endpoints that Dapr calls.

        Args:
            pubsub_name: Pub/sub component name
            topic: Topic to subscribe to
            route: Route in your app where Dapr will POST messages

        Returns:
            Subscription configuration
        """
        return {
            "pubsubname": pubsub_name,
            "topic": topic,
            "route": route,
        }

    # ================== STATE STORE ==================

    async def get_state(
        self,
        store_name: str,
        key: str,
    ) -> Optional[Any]:
        """
        Get a value from the state store.

        Args:
            store_name: State store component name (e.g., 'postgres-statestore')
            key: State key

        Returns:
            State value (deserialized from JSON), or None if not found
        """
        url = f"{self.base_url}/v1.0/state/{store_name}/{key}"

        try:
            response = await self.client.get(url)

            if response.status_code == 204:
                # Key not found
                return None
            elif response.status_code == 200:
                # Key found - parse JSON value
                return response.json() if response.text else None
            else:
                logger.error(
                    f"Failed to get state: {response.status_code} {response.text}"
                )
                return None

        except httpx.HTTPError as e:
            logger.error(f"HTTP error getting state: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting state: {e}", exc_info=True)
            return None

    async def save_state(
        self,
        store_name: str,
        key: str,
        value: Any,
        metadata: Optional[Dict[str, str]] = None,
    ) -> bool:
        """
        Save a value to the state store.

        Args:
            store_name: State store component name
            key: State key
            value: Value to store (JSON-serializable)
            metadata: Optional metadata (TTL, consistency, etc.)

        Returns:
            True if save succeeded, False otherwise
        """
        url = f"{self.base_url}/v1.0/state/{store_name}"

        payload = [
            {
                "key": key,
                "value": value,
                "metadata": metadata or {},
            }
        ]

        try:
            response = await self.client.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 204:
                logger.debug(f"Saved state: {key}")
                return True
            else:
                logger.error(
                    f"Failed to save state: {response.status_code} {response.text}"
                )
                return False

        except httpx.HTTPError as e:
            logger.error(f"HTTP error saving state: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error saving state: {e}", exc_info=True)
            return False

    async def delete_state(
        self,
        store_name: str,
        key: str,
    ) -> bool:
        """
        Delete a state entry.

        Args:
            store_name: State store component name
            key: State key to delete

        Returns:
            True if delete succeeded, False otherwise
        """
        url = f"{self.base_url}/v1.0/state/{store_name}/{key}"

        try:
            response = await self.client.delete(url)

            if response.status_code == 204:
                logger.debug(f"Deleted state: {key}")
                return True
            else:
                logger.error(
                    f"Failed to delete state: {response.status_code} {response.text}"
                )
                return False

        except httpx.HTTPError as e:
            logger.error(f"HTTP error deleting state: {e}")
            return False

    # ================== SECRET STORE ==================

    async def get_secret(
        self,
        store_name: str,
        key: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Optional[Dict[str, str]]:
        """
        Get a secret from the secret store.

        Args:
            store_name: Secret store component name (e.g., 'kubernetes-secrets')
            key: Secret name
            metadata: Optional metadata

        Returns:
            Secret value as dictionary, or None if not found
        """
        url = f"{self.base_url}/v1.0/secrets/{store_name}/{key}"

        try:
            response = await self.client.get(
                url,
                params=metadata or {},
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(
                    f"Failed to get secret: {response.status_code} {response.text}"
                )
                return None

        except httpx.HTTPError as e:
            logger.error(f"HTTP error getting secret: {e}")
            return None

    # ================== SERVICE INVOCATION ==================

    async def invoke_service(
        self,
        app_id: str,
        method: str,
        http_verb: str = "POST",
        data: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Invoke another service via Dapr service invocation.

        Args:
            app_id: Target service app ID
            method: HTTP method/route on target service
            http_verb: HTTP verb (GET, POST, etc.)
            data: Request payload

        Returns:
            Response data, or None if invocation failed
        """
        url = f"{self.base_url}/v1.0/invoke/{app_id}/method/{method}"

        try:
            if http_verb.upper() == "GET":
                response = await self.client.get(url)
            elif http_verb.upper() == "POST":
                response = await self.client.post(url, json=data or {})
            elif http_verb.upper() == "PUT":
                response = await self.client.put(url, json=data or {})
            elif http_verb.upper() == "DELETE":
                response = await self.client.delete(url)
            else:
                logger.error(f"Unsupported HTTP verb: {http_verb}")
                return None

            if response.status_code < 400:
                return response.json() if response.text else {}
            else:
                logger.error(
                    f"Service invocation failed: {response.status_code} {response.text}"
                )
                return None

        except httpx.HTTPError as e:
            logger.error(f"HTTP error invoking service: {e}")
            return None


# Global Dapr client instance
_dapr_client_instance: Optional[DaprClient] = None


async def get_dapr_client() -> DaprClient:
    """
    Get global Dapr client instance (FastAPI dependency).

    Returns:
        Shared DaprClient instance
    """
    global _dapr_client_instance
    if _dapr_client_instance is None:
        _dapr_client_instance = DaprClient()
    return _dapr_client_instance


async def shutdown_dapr_client():
    """Shutdown global Dapr client (call on app shutdown)."""
    global _dapr_client_instance
    if _dapr_client_instance:
        await _dapr_client_instance.close()
        _dapr_client_instance = None
