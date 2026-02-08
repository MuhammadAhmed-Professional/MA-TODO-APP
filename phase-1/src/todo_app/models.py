from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Task:
    """Represents a todo task with metadata."""

    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now, compare=False)

    def __post_init__(self) -> None:
        """Validate field constraints after initialization."""
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")
        if len(self.title) > 200:
            raise ValueError("Title must be between 1-200 characters")
        if len(self.description) > 1000:
            raise ValueError("Description cannot exceed 1000 characters")
