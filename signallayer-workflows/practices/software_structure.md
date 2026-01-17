# Software Structure

## Overview
This document describes the architectural patterns and structural organization of the codebase.

## Project Organization
- Organize code by feature or module, not by type
- Keep related functionality together
- Use clear directory hierarchy
- Separate business logic from infrastructure code

## Project Directory Structure
```
src/
├── api/                    # FastAPI application
│   ├── routes/            # API route handlers
│   ├── dependencies.py    # FastAPI dependencies
│   └── main.py           # FastAPI app setup
├── workflows/             # Temporal workflows
│   ├── __init__.py
│   └── *.py              # Individual workflows
├── activities/            # Temporal activities
│   ├── __init__.py
│   └── *.py              # Activity implementations
├── models/                # Pydantic models
│   ├── domain.py         # Domain models
│   ├── requests.py       # API request models
│   └── responses.py      # API response models
├── services/              # Business logic services
├── repositories/          # Data access layer
├── config.py             # Pydantic Settings configuration
└── utils/                # Utility functions
tests/
├── unit/                 # Unit tests
├── integration/          # Integration tests
├── workflows/            # Temporal workflow tests
├── api/                  # FastAPI endpoint tests
├── conftest.py          # Pytest fixtures
└── fixtures/            # Test data
pyproject.toml           # Project metadata and dependencies
uv.lock                  # Locked dependencies
.python-version          # Python version
```

## Architectural Principles
- **Separation of Concerns**: Keep different aspects of the application separate
- **Single Responsibility**: Each module/class should have one reason to change
- **Dependency Inversion**: Depend on abstractions, not concretions
- **DRY (Don't Repeat Yourself)**: Avoid code duplication
- **KISS (Keep It Simple)**: Favor simple solutions over complex ones

## Layered Architecture
- **Presentation Layer**: UI/API interfaces
- **Application Layer**: Business logic and workflows
- **Domain Layer**: Core domain models and rules
- **Infrastructure Layer**: Database, external services, frameworks

## Module Design
- Define clear public interfaces with type hints
- Use Pydantic models for data validation at boundaries
- Hide implementation details using private modules (`_*.py`)
- Minimize coupling between modules
- Use FastAPI's dependency injection system
- Use Pydantic Settings for configuration injection
- Document module boundaries and contracts with docstrings
- Keep Temporal workflows and activities decoupled

## FastAPI Patterns
- Organize routes by resource in separate modules
- Use APIRouter for modular route organization
- Leverage Depends() for dependency injection
- Use Pydantic models for request/response validation
- Implement middleware for cross-cutting concerns
- Use background tasks for non-blocking operations

## Temporal Patterns
- One workflow class per file
- Group related activities in modules
- Use dataclasses or Pydantic for workflow inputs
- Implement workflows as pure functions when possible
- Use signals and queries for workflow interaction
- Handle activity failures with appropriate retry policies

## Code Organization Patterns
- Use namespaces/packages appropriately
- Group related functions and classes
- Keep file sizes manageable
- Use meaningful names for files and directories
- Apply consistent naming conventions

## Configuration Management
- Use Pydantic Settings for type-safe configuration
- Load config from environment variables and `.env` files
- Use `BaseSettings` with validation
- Implement env_prefix for namespacing
- Use `Field` with descriptions for all settings
- Don't commit `.env` files with secrets
- Provide `.env.example` template
- Document all configuration options in docstrings
- Use different settings classes for different environments
