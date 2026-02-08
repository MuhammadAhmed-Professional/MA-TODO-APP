# Skill: Enhance API Documentation

## Description
Add comprehensive docstrings, OpenAPI examples, and response models to FastAPI endpoints to generate high-quality auto-generated API documentation at /docs.

## Inputs
- `api_file`: Path to the FastAPI endpoint file (e.g., `backend/src/api/tasks.py`)
- `model_file`: Path to the Pydantic model file (e.g., `backend/src/models/task.py`)

## Process

### 1. Analyze Existing Endpoints
- Read the API file to identify all endpoints (GET, POST, PUT, PATCH, DELETE)
- Read the model file to understand request/response schemas
- Identify authentication requirements
- Identify error responses (400, 401, 403, 404, 500)

### 2. Add Comprehensive Docstrings
Use triple-quoted strings for endpoint documentation:

```python
@router.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TaskResponse:
    """
    Create a new task for the authenticated user.

    This endpoint allows authenticated users to create a new todo task with
    a title (required) and optional description. The task is automatically
    associated with the current user's account.

    **Authentication**: Requires valid JWT token in auth_token cookie.

    **Request Body**:
    - `title` (string, required): Task title (1-200 characters)
    - `description` (string, optional): Task description (max 2000 characters)

    **Response** (201 Created):
    - Returns the created task with generated UUID
    - `Location` header contains the task's URL

    **Error Responses**:
    - `400 Bad Request`: Invalid input (empty title, too long)
    - `401 Unauthorized`: Missing or invalid authentication token
    - `500 Internal Server Error`: Database or server error

    **Example Request**:
    ```json
    {
      "title": "Buy groceries",
      "description": "Milk, eggs, bread"
    }
    ```

    **Example Response**:
    ```json
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "is_complete": false,
      "user_id": "789e4567-e89b-12d3-a456-426614174999",
      "created_at": "2025-12-06T10:30:00Z",
      "updated_at": "2025-12-06T10:30:00Z"
    }
    ```
    """
    # Implementation...
```

### 3. Add Example Values to Pydantic Models
Use `Field(example=...)` for better OpenAPI schema generation:

```python
from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
        example="Buy groceries",
        description="Task title (required, 1-200 characters)"
    )
    description: str | None = Field(
        None,
        max_length=2000,
        example="Milk, eggs, bread, coffee",
        description="Optional task description (max 2000 characters)"
    )

class TaskResponse(BaseModel):
    id: str = Field(example="123e4567-e89b-12d3-a456-426614174000")
    title: str = Field(example="Buy groceries")
    description: str | None = Field(example="Milk, eggs, bread, coffee")
    is_complete: bool = Field(example=False)
    user_id: str = Field(example="789e4567-e89b-12d3-a456-426614174999")
    created_at: str = Field(example="2025-12-06T10:30:00Z")
    updated_at: str = Field(example="2025-12-06T10:30:00Z")
```

### 4. Add Response Models and Status Codes
Explicitly declare response models and status codes:

```python
from fastapi import status

@router.get(
    "/tasks",
    response_model=list[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="List all tasks for authenticated user",
    tags=["Tasks"]
)
```

### 5. Add Error Response Examples
Document error responses using `responses` parameter:

```python
@router.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=201,
    responses={
        201: {
            "description": "Task created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "title": "Buy groceries",
                        "is_complete": False
                    }
                }
            }
        },
        400: {
            "description": "Invalid input",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Title is required and must be 1-200 characters"
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid or expired authentication token"
                    }
                }
            }
        }
    }
)
```

### 6. Configure FastAPI App Metadata
In `backend/src/main.py`, add custom OpenAPI metadata:

```python
from fastapi import FastAPI

app = FastAPI(
    title="TaskMaster API",
    description="RESTful API for todo task management with user authentication",
    version="1.0.0",
    contact={
        "name": "TaskMaster Support",
        "email": "support@taskmaster.example.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "User signup, login, logout operations"
        },
        {
            "name": "Tasks",
            "description": "CRUD operations for todo tasks"
        }
    ]
)
```

### 7. Test Documentation
- Start backend: `cd backend && uv run uvicorn src.main:app --reload`
- Navigate to `http://localhost:8000/docs`
- Verify all endpoints are listed
- Verify schemas show example values
- Click "Try it out" and execute requests
- Verify error responses are documented

## Example Usage

**Scenario**: Enhance API documentation for task endpoints

```bash
# Context: Tasks T087-T091 from tasks.md
# T087: Add docstrings to all endpoints
# T088: Add response_model and status_code to all routes
# T089: Add example values to Pydantic models
# T090: Configure FastAPI app with custom metadata
# T091: Add error response examples
```

**Agent invocation**:
```
Enhance API documentation for task management:
- API file: backend/src/api/tasks.py
- Model file: backend/src/models/task.py
- Requirements:
  - Add comprehensive docstrings to all 6 endpoints (list, create, get, update, toggle, delete)
  - Add Field(example=...) to all Pydantic models (TaskCreate, TaskUpdate, TaskResponse)
  - Add responses={400: ..., 401: ..., 403: ..., 404: ...} to all endpoints
  - Configure FastAPI app metadata in backend/src/main.py
```

## Constitution Compliance
- **Principle II**: Clean code - Comprehensive documentation improves maintainability
- **Principle VIII**: API security - Documents authentication requirements clearly
- **Principle X**: Validated outputs - Documents all response formats and error codes

## Output
- Updated API file with comprehensive docstrings
- Updated model file with example values
- Updated main.py with OpenAPI metadata
- Verified /docs shows complete, accurate documentation
