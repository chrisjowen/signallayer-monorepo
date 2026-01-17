# Dynamic API Generation

The web layer in this project automatically generates REST endpoints for any Temporal workflow registered with the `@workflow_api` decorator.

## How it Works

1.  **Registration**: When the application starts, it imports the workflows. The `@workflow_api` decorator registers metadata about the workflow (name, version, input/output Pydantic models) in the `WorkflowRegistry`.
2.  **Route Discovery**: The FastAPI app, during its `lifespan` startup, calls `generate_workflow_routes(workflow_registry)`.
3.  **Dynamic Mounting**: For each workflow in the registry, a `POST` route is added to the `APIRouter`.

## Endpoint Structure

Endpoints are followed by the pattern:
`POST /api/v1/workflow/{workflow-name}-{version}`

### Example
If you have a workflow named `user-signup` with version `v2`, the endpoint will be:
`POST /api/v1/workflow/user-signup-v2`

## Execution Modes

The generated endpoints support two execution modes via the `async` query parameter.

### 1. Synchronous Execution (Default)
The API waits for the workflow to complete and returns the result directly.
```bash
curl -X POST "http://localhost:8000/api/v1/workflow/my-workflow-v2" \
     -H "Content-Type: application/json" \
     -d '{"name": "World"}'
```

**Response**:
```json
{
  "greeting": "Hello, World!"
}
```

### 2. Asynchronous Execution (`async=true`)
The API starts the workflow and immediately returns a handle (Workflow ID and Run ID).
```bash
curl -X POST "http://localhost:8000/api/v1/workflow/my-workflow-v2?async=true" \
     -H "Content-Type: application/json" \
     -d '{"name": "World"}'
```

**Response**:
```json
{
  "workflow_id": "my-workflow-20251229-123456",
  "run_id": "abc-789-xyz",
  "status_url": "/api/v1/workflow/my-workflow-v2/status/my-workflow-20251229-123456"
}
```

## Features
- **Validation**: FastAPI automatically uses the Pydantic models extracted from the workflow's `run` method to validate incoming requests.
- **OpenAPI/Swagger**: All dynamically generated routes appear in the `/docs` or `/redoc` interactive documentation, complete with request/response schemas.
- **Task Queue Isolation**: Routes respect the `task_queue` configured in the `@workflow_api` decorator or fall back to the global setting.
