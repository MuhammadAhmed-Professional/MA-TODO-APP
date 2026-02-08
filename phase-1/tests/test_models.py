import pytest
from src.todo_app.models import Task

def test_task_creation_all_fields():
    # This test should fail initially because Task dataclass is not yet implemented
    task = Task(id=1, title="Test Task", description="A test description", completed=False)
    assert task.id == 1
    assert task.title == "Test Task"
    assert task.description == "A test description"
    assert task.completed is False
    assert task.created_at is not None # Assuming datetime.now() default

def test_task_creation_defaults():
    # This test should fail initially because Task dataclass is not yet implemented
    task = Task(id=2, title="Default Task")
    assert task.id == 2
    assert task.title == "Default Task"
    assert task.description == ""
    assert task.completed is False
    assert task.created_at is not None

def test_task_equality():
    # This test should fail initially because Task dataclass is not yet implemented
    task1 = Task(id=1, title="Task A")
    task2 = Task(id=1, title="Task A")
    task3 = Task(id=2, title="Task B")
    assert task1 == task2
    assert task1 != task3
