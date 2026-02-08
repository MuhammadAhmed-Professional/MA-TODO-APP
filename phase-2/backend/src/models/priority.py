"""
Priority Enum Model

Defines task priority levels with sorting weights and display properties.
"""

from enum import IntEnum


class Priority(IntEnum):
    """
    Task priority levels.

    Higher numeric value = higher priority. This enum can be used
    for sorting tasks by priority (high priority tasks sort first).

    Values:
        LOW (1): Low priority tasks
        MEDIUM (2): Medium priority tasks (default)
        HIGH (3): High priority tasks

    Example:
        task = Task(priority=Priority.HIGH)
        assert task.priority == 3
        assert task.priority.name == "HIGH"

        # Sorting tasks by priority (highest first)
        sorted_tasks = sorted(tasks, key=lambda t: t.priority, reverse=True)
    """

    LOW = 1
    MEDIUM = 2
    HIGH = 3

    @classmethod
    def from_string(cls, value: str) -> "Priority":
        """
        Convert string to Priority enum.

        Args:
            value: String value ("low", "medium", "high", case-insensitive)

        Returns:
            Priority enum value

        Raises:
            ValueError: If value is not a valid priority

        Example:
            priority = Priority.from_string("high")
            assert priority == Priority.HIGH
        """
        try:
            return cls[value.upper()]
        except KeyError:
            valid = ", ".join([p.name.lower() for p in cls])
            raise ValueError(
                f"Invalid priority '{value}'. Valid values: {valid}"
            )

    @property
    def label(self) -> str:
        """
        Human-readable label for the priority.

        Returns:
            Title-cased priority name

        Example:
            Priority.HIGH.label  # "High"
        """
        return self.name.capitalize()

    @property
    def color(self) -> str:
        """
        Hex color code for UI display.

        Returns:
            Hex color string

        Example:
            Priority.HIGH.color  # "#ef4444" (red)
        """
        colors = {
            Priority.LOW: "#22c55e",    # green
            Priority.MEDIUM: "#eab308",  # yellow
            Priority.HIGH: "#ef4444",    # red
        }
        return colors[self]

    def __str__(self) -> str:
        """String representation (lowercase name)."""
        return self.name.lower()
