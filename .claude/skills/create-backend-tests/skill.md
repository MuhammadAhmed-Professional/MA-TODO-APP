# Skill: Create Backend Tests

## Description
Generate comprehensive pytest unit and integration tests for FastAPI endpoints with proper test coverage, mocking, and assertion patterns.

## Inputs
- `model_file`: Path to the SQLModel model file (e.g., `backend/src/models/task.py`)
- `service_file`: Path to the service file (e.g., `backend/src/services/task_service.py`)
- `api_file`: Path to the API endpoint file (e.g., `backend/src/api/tasks.py`)
- `test_type`: Type of tests to generate (`unit` or `integration` or `both`)

## Process

### 1. Analyze Existing Code
- Read the model file to understand entity structure
- Read the service file to identify business logic methods
- Read the API file to identify endpoints and their behaviors

### 2. Generate Unit Tests
Create `backend/tests/unit/test_<module>_service.py`:
- Test each service method in isolation
- Mock database dependencies using `pytest` fixtures
- Test edge cases (empty inputs, invalid data, boundary conditions)
- Test error paths (e.g., duplicate records, not found, unauthorized)

**Pattern**:
```python
import pytest
from unittest.mock import Mock, patch
from src.services.task_service import TaskService
from src.models.task import Task

@pytest.fixture
def mock_db_session():
    return Mock()

def test_create_task_success(mock_db_session):
    # Arrange
    service = TaskService(mock_db_session)
    # Act & Assert
    ...
```

### 3. Generate Integration Tests
Create `backend/tests/integration/test_<module>_api.py`:
- Use FastAPI `TestClient` for HTTP requests
- Test with real database (Neon test instance or SQLite in-memory)
- Test authentication with JWT tokens
- Test all HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Test response codes (200, 201, 400, 401, 403, 404, 500)
- Test pagination, filtering, sorting
- Test ownership checks (user A cannot access user B's resources)

**Pattern**:
```python
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_create_task_authenticated():
    # Arrange: login to get token
    login_response = client.post("/api/auth/login", json={...})
    token = login_response.cookies.get("auth_token")

    # Act: create task
    response = client.post("/api/tasks", json={...}, cookies={"auth_token": token})

    # Assert
    assert response.status_code == 201
    assert "id" in response.json()
```

### 4. Ensure Test Coverage
- Cover all success paths (happy paths)
- Cover all error paths (validation errors, unauthorized access)
- Cover edge cases (empty lists, null values, max length strings)
- Aim for 80%+ code coverage

## Example Usage

**Scenario**: Generate tests for Task CRUD operations

```bash
# Context: Tasks T061 and T062 from tasks.md
# T061: Write backend unit tests in backend/tests/unit/test_task_service.py
# T062: Write backend integration tests in backend/tests/integration/test_tasks_api.py
```

**Agent invocation**:
```
Create backend tests for task management:
- Model: backend/src/models/task.py
- Service: backend/src/services/task_service.py
- API: backend/src/api/tasks.py
- Test type: both

Expected tests:
- Unit: test_create_task, test_get_user_tasks, test_update_task, test_delete_task, test_ownership_validation
- Integration: test_list_tasks_authenticated, test_create_task_201, test_update_task_404, test_delete_task_ownership_403
```

## Constitution Compliance
- **Principle III**: TDD - Tests generated before or alongside implementation
- **Principle IV**: Database-first - Integration tests use real database connections
- **Principle II**: Clean code - Tests follow pytest conventions, clear arrange-act-assert pattern

## Output
- `backend/tests/unit/test_<module>_service.py` (unit tests)
- `backend/tests/integration/test_<module>_api.py` (integration tests)
- Coverage report showing >80% coverage for tested module
