# Project Context

## Purpose
A dynamic Temporal Workflow system designed to handle complex tasks, possibly related to capture, processing, and management of information (Second Brain).

## Tech Stack
- Python 3.11+
- FastAPI (Web API)
- Temporal (Workflow engine)
- Pydantic v2 (Data validation)
- structlog (Logging)
- inject (Dependency injection)
- httpx (HTTP client)
- openai-agents (Agent framework)

## Project Conventions

### Code Style
- Ruff for linting and formatting.
- Mypy for strict type checking.
- Docstrings for functions and classes.
- Async/await for I/O operations.

### Architecture Patterns
- Layered architecture:
  - `src/web`: FastAPI endpoints.
  - `src/worker`: Temporal worker and workflow/activity registration.
  - `src/agent`: Logic for AI agents.
  - `src/contexts`: Context-specific business logic.
  - `src/common`: Shared utilities and base classes.

### Testing Strategy
- Pytest with `pytest-asyncio`.
- Coverage reporting with `pytest-cov`.
- Tests located in `tests/`.

### Git Workflow
- Standard Git workflow.

## Domain Context
- Focus on automation and workflow orchestration using Temporal.
- Integration with AI agents for intelligent processing.

## Important Constraints
- Strict typing and linting requirements.
- Modular design to allow swapping components.

## External Dependencies
- Temporal Server.
- OpenAI API (implied by `openai-agents`).
- PostgreSQL (mentioned in conversation history for storage, though not yet in `pyproject.toml` dependencies).
- ScrapingBee, BeautifulSoup (for data capture).
