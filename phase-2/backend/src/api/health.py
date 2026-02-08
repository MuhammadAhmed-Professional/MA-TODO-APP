"""
Health Check API Endpoints

Provides system health status including database connectivity.
Used by monitoring systems and load balancers.
"""

from fastapi import APIRouter, status
from pydantic import BaseModel

from src.db.session import check_connection

router = APIRouter(prefix="/api/health", tags=["health"])


class HealthResponse(BaseModel):
    """Health check response model"""

    status: str
    database: str
    version: str = "0.1.0"


@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="System Health Check",
    description="Returns overall system health including database connectivity status",
)
async def health_check() -> HealthResponse:
    """
    Comprehensive health check endpoint.

    Checks:
    - API service status (if this returns, API is running)
    - Database connectivity (attempts connection and query)

    Returns:
        HealthResponse: Health status with database connection state

    Example Response:
        {
            "status": "healthy",
            "database": "connected",
            "version": "0.1.0"
        }

    Status Codes:
        200: System healthy, database connected
        503: System degraded (would require additional logic)
    """
    db_status = "connected" if check_connection() else "disconnected"
    overall_status = "healthy" if db_status == "connected" else "degraded"

    return HealthResponse(
        status=overall_status,
        database=db_status,
        version="0.1.0",
    )


@router.get(
    "/ping",
    status_code=status.HTTP_200_OK,
    summary="Simple Ping",
    description="Lightweight ping endpoint for basic availability checks",
)
async def ping() -> dict[str, str]:
    """
    Lightweight ping endpoint.

    Returns immediately without database checks.
    Use this for basic load balancer health checks.

    Returns:
        dict: Simple pong response

    Example Response:
        {"ping": "pong"}
    """
    return {"ping": "pong"}
