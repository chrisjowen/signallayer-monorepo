# Development Practices

## Overview
This document outlines the development practices and workflows for this project.

## Version Control
- Use meaningful commit messages following conventional commits format
- Branch naming conventions: `feature/`, `bugfix/`, `hotfix/`
- Keep commits atomic and focused
- Rebase before merging to maintain clean history

## Code Style
- Follow PEP 8 style guide strictly
- Use `ruff` for linting and formatting (or `black` + `isort`)
- Apply `mypy` for static type checking with strict mode
- Use type hints for all function signatures
- Follow Pydantic best practices for data validation
- Use snake_case for variables and functions
- Use PascalCase for classes and Pydantic models
- Keep functions focused and concise (max 50 lines)
- Prefer composition over inheritance

## Development Workflow
1. Create feature branch from main/develop
2. Implement changes with tests
3. Run local test suite
4. Submit pull request with description
5. Address review feedback
6. Merge after approval

## Dependency Management
- Use `uv` for fast Python package management
- Use `uvx` for running Python tools without installation
- Maintain `pyproject.toml` for project dependencies
- Use `uv.lock` for reproducible builds
- Pin major versions, allow minor/patch updates
- Document why external libraries are needed
- Audit dependencies with `pip-audit` or `safety`
- Keep Temporal SDK version current
- Regularly update FastAPI and Pydantic versions

## Error Handling
- Use Python exceptions with specific exception types
- Leverage FastAPI's `HTTPException` for API errors
- Handle Temporal workflow failures and retries properly
- Use Pydantic's `ValidationError` for data validation
- Provide meaningful error messages with context
- Log errors with structured logging (use `structlog`)
- Use custom exception classes when appropriate
- Handle edge cases gracefully with proper status codes

## Performance Considerations
- Profile code before optimizing
- Use appropriate data structures
- Consider memory usage and scalability
- Document performance requirements
