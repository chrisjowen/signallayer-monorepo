# Architecture & Dependency Injection

This project is built with a focus on **Separation of Concerns** and **Testability**. It leverages `python-inject` for dependency management and follows a modular structure.

## Core Principles

### 1. Separation of Execution and Discovery
- **`TemporalWorker`**: Located in `src/worker/lib/worker.py`, this class is a pure executor. It does not know about registries or how to "find" workflows. It simply takes a list of classes and functions and runs them.
- **`main.py`**: The entry point is responsible for discovery. It retrieves the registries, pulls the registered workflows/activities, and "injects" them into the worker.

### 2. Dependency Injection (DI)
We use the `inject` library to manage shared resources and services.

- **Initialization**: DI is configured in `src/common/injection.py`.
- **Registry Injection**: The `WorkflowRegistry` and `ActivityRegistry` are singletons managed by the DI container.
- **Service Injection**: Business logic services (like `DummyService`) are injected into activities using `@inject.params`.

#### Injection in Activities
```python
@configured_activity(...)
@inject.params(db=DatabaseService)
async def my_activity(id: str, db: DatabaseService):
    return await db.get_user(id)
```

## Directory Structure

- `src/common/`: Shared code, DI configuration, and base exceptions.
- `src/worker/lib/`: Core framework code (decorators, registries, worker wrappers).
- `src/worker/workflows/`: Business logic workflows and their related activities.
- `src/web/`: FastAPI application and dynamic route generation.

## Testability

The decoupling of the worker and the use of DI makes testing straightforward:

### Registry Mocking
In tests, we use a clean registry for every test case. This is handled by a global `autouse` fixture in `tests/worker/conftest.py`:

```python
@pytest.fixture(autouse=True)
def clear_registries(workflow_registry, activity_registry):
    workflow_registry.clear()
    activity_registry.clear()
    yield
    # ... cleanup ...
```

### Dependency Overrides
Because we use DI, we can easily swap out real services for mocks during integration tests using `binder.bind()`.

## Deployment to Fly.io

The project is configured for deployment to Fly.io using a multi-process strategy.

### Process Groups
The `fly.toml` defines two distinct process groups:
- **`web`**: Runs the FastAPI application with Uvicorn.
- **`worker`**: Runs the Temporal worker.

### Scaling
You can scale each process group independently to meet your requirements. For example, to run 2 web instances and 4 workers:

```bash
fly scale count web=2 worker=4 --process-groups
```

### Health Checks
The `web` process includes a standard `/health` check that verifies the Temporal client connection and the availability of registered workflows.
