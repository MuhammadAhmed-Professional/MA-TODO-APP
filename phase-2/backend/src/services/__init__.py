"""
Business Logic Services Package

Contains all service modules with business logic (fat services).
Controllers remain thin and delegate to these services.
"""

from src.services.auth_service import AuthService
from src.services.task_service import TaskService

__all__ = ["AuthService", "TaskService"]
