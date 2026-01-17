# Project Documentation

Welcome to the **SignalLayer Workflows** documentation. This project provides a high-level framework on top of Temporal for building scalable, type-safe, and REST-accessible workflows.

## Quick Links

- **[Decorators & Proxies](decorators.md)**: Learn about `@workflow_api`, `@configured_activity`, and the `.execute()` calling pattern.
- **[Dynamic API](api.md)**: Understand how REST endpoints are automatically generated for your workflows.
- **[Architecture & DI](architecture.md)**: Explore the project structure and how dependency injection is used.

## Getting Started

### 1. Define a Workflow
Use the `@workflow_api` decorator and define a `run` method with Pydantic models.

### 2. Define Activities
Use `@configured_activity` to set default timeouts and enable the proxy calling pattern.

### 3. Start the Worker
Run the worker to start listening for tasks:
```bash
python -m src.worker.main
```

### 4. Use the API
Access the auto-generated Swagger UI at `http://localhost:8000/docs` to see your workflows in action.
