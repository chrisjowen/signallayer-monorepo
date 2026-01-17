# Decorators and Activity Proxies

This project uses custom decorators to simplify Temporal workflow and activity registration, and to provide a cleaner developer experience for calling activities from workflows.

## Workflow Decorator: `@workflow_api`

The `@workflow_api` decorator is used to mark a class as a Temporal workflow and register it with the internal `WorkflowRegistry`.

### Usage

```python
from src.worker.lib.decorators import workflow_api
from pydantic import BaseModel
from temporalio import workflow

class MyInput(BaseModel):
    name: str

class MyOutput(BaseModel):
    greeting: str

@workflow_api(name="my-custom-workflow", version="v1")
@workflow.defn
class MyWorkflow:
    @workflow.run
    async def run(self, input: MyInput) -> MyOutput:
        return MyOutput(greeting=f"Hello, {input.name}!")
```

### Features
- **Automatic Registration**: Automatically registers the workflow in the `WorkflowRegistry`.
- **Metadata Extraction**: Uses `src.worker.lib.type_utils` to extract Pydantic models for input and output, which are then used by the web layer to generate REST endpoints.
- **Kebab-case Names**: If no `name` is provided, it converts the class name (e.g., `MyWorkflow`) to kebab-case (`my-workflow`).
- **Versioning**: Supports explicit versioning for side-by-side deployment of different workflow versions.

---

## Activity Decorator: `@configured_activity`

The `@configured_activity` decorator simplifies activity definition and allows for "Proxy Calls" using the `.execute()` method.

### Usage

```python
from datetime import timedelta
from src.worker.lib.decorators import configured_activity

@configured_activity(
    name="send_welcome_email",
    start_to_close_timeout=timedelta(seconds=10),
    max_retries=3
)
async def send_email(email: str) -> bool:
    # ... logic ...
    return True
```

### Activity Proxy: The `.execute()` Pattern

One of the key features of this project is the removal of boilerplate when calling activities from workflows. Instead of using `workflow.execute_activity`, you can call the activity directly using its `.execute()` method.

#### Traditional Way (Temporal Default)
```python
from temporalio import workflow

@workflow.defn
class MyWorkflow:
    @workflow.run
    async def run(self, email: str):
        # Requires re-specifying timeouts or using a proxy object
        return await workflow.execute_activity(
            send_email,
            email,
            start_to_close_timeout=timedelta(seconds=10)
        )
```

#### The Proxy Way (Using `.execute()`)
```python
@workflow.defn
class MyWorkflow:
    @workflow.run
    async def run(self, email: str):
        # Uses the defaults configured in the @configured_activity decorator
        return await send_email.execute(email)
```

### Key Benefits of `.execute()`:
1.  **Encapsulation**: Timeouts, retry policies, and task queues are defined once on the activity itself.
2.  **Type Safety**: The `.execute()` method maintains the type hints of the original function, giving you better IDE support inside the workflow.
3.  **Overrides**: You can still override any configuration if needed:
    ```python
    await send_email.execute(email, start_to_close_timeout=timedelta(seconds=60))
    ```
