# Skill: Create FastAPI Endpoint

## Description
Generates a complete FastAPI endpoint (route handler) with request/response models, validation, authentication, error handling, and docstrings following the project's thin-controller pattern.

## Inputs
- **endpoint_name**: Name of the endpoint (e.g., "create_task", "login")
- **http_method**: HTTP method (GET, POST, PUT, PATCH, DELETE)
- **route_path**: API route path (e.g., "/api/tasks", "/api/auth/login")
- **request_model**: Pydantic model for request body (or None for GET/DELETE)
- **response_model**: SQLModel/Pydantic model for response
- **service_method**: Service layer method to call (e.g., "task_service.create_task")
- **requires_auth**: Boolean - does endpoint require authentication?
- **status_code**: HTTP status code for success (200, 201, 204, etc.)
- **file_path**: Where to add endpoint (e.g., "backend/src/api/tasks.py")

## Process

1. **Analyze Requirements**
   - Review service method signature and input/output types
   - Check for authentication/authorization needs
   - Determine request/response schema compatibility

2. **Generate Endpoint**
   ```python
   @router.{http_method}(
       "{route_path}",
       response_model=ResponseModel,
       status_code={status_code},
       responses={
           400: {"description": "Bad request"},
           401: {"description": "Unauthorized"},
           404: {"description": "Not found"},
       }
   )
   async def {endpoint_name}(
       request_model: RequestModel,
       current_user: User = Depends(get_current_user),  # if requires_auth
       db: Session = Depends(get_db),
   ) -> ResponseModel:
       """
       [Description of what endpoint does]

       Args:
           request_model: Request payload
           current_user: Authenticated user (injected by dependency)
           db: Database session

       Returns:
           ResponseModel with created/updated resource

       Raises:
           HTTPException: If validation fails or resource not found
       """
       # Thin controller pattern: validate, call service, return result
       result = await service_method(db, current_user.id, request_model)
       return ResponseModel.from_orm(result)
   ```

3. **Add Error Handling**
   - 400 Bad Request for validation errors
   - 401 Unauthorized for missing/invalid auth
   - 403 Forbidden for ownership violations
   - 404 Not Found for missing resources
   - 500 Internal Server Error (global handler)

4. **Add Docstring**
   - Description of endpoint purpose
   - Args with types and descriptions
   - Returns with response type
   - Raises with error scenarios

5. **Validate Against Service**
   - Ensure input/output types match service signature
   - Verify error handling for all service exceptions

## Example Usage
```
/skill create-fastapi-endpoint \
  --endpoint_name create_task \
  --http_method POST \
  --route_path /api/tasks \
  --request_model TaskCreate \
  --response_model TaskResponse \
  --service_method task_service.create_task \
  --requires_auth true \
  --status_code 201 \
  --file_path backend/src/api/tasks.py
```

## Output
- Complete FastAPI endpoint function ready to integrate
- Includes type hints, docstrings, error handling
- Ready for testing with pytest/httpx
