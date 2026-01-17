# Testing Practices

## Overview
This document defines testing standards and practices for ensuring code quality and reliability.

## Testing Pyramid
- **Unit Tests**: Test individual functions and methods in isolation
- **Integration Tests**: Test interactions between components
- **End-to-End Tests**: Test complete user workflows

## Unit Testing
- Write tests for all public APIs and functions using `pytest`
- Use `pytest` fixtures for setup and teardown
- Follow AAA pattern: Arrange, Act, Assert
- Test edge cases and boundary conditions
- Use `pytest-asyncio` for async test support
- Mock external dependencies with `pytest-mock` or `unittest.mock`
- Use `pytest-cov` for coverage reporting
- Aim for high code coverage (target: >80%)
- Test Pydantic model validation thoroughly

## Test Organization
- Mirror source code structure in test directories
- Name test files with `test_*.py` prefix
- Group related tests using pytest classes or modules
- Use descriptive test names: `test_<function>_<scenario>_<expected>`
- Organize tests into:
  - `tests/unit/` - Unit tests
  - `tests/integration/` - Integration tests
  - `tests/workflows/` - Temporal workflow tests
  - `tests/api/` - FastAPI endpoint tests

## Test Quality
- Tests should be independent and idempotent
- Avoid test interdependencies
- Keep tests fast and focused
- Use fixtures and factories for test data
- Clean up resources after tests

## Integration Testing
- Test FastAPI endpoints using `TestClient`
- Test Temporal workflows with `WorkflowEnvironment.start_time_skipping()`
- Test Temporal activities in isolation and integration
- Test database interactions with test database
- Test Pydantic Settings with test environment variables
- Use pytest fixtures for FastAPI app and Temporal client setup
- Mock external service integrations appropriately
- Implement proper async setup and teardown

## Temporal Workflow Testing
- Use `temporalio.testing.WorkflowEnvironment` for workflow tests
- Test workflows with time-skipping for fast execution
- Test activity retries and failure scenarios
- Test workflow signals and queries
- Mock activities when testing workflow logic
- Test workflow history replay for compatibility

## Continuous Testing
- Run tests automatically on commit/push with GitHub Actions
- Run `pytest` with coverage in CI/CD pipeline
- Run `mypy` type checking in CI/CD
- Run `ruff check` linting in CI/CD
- Monitor test execution time
- Fix failing tests immediately
- Don't commit broken tests

## Test-Driven Development (TDD)
When appropriate:
1. Write failing test first
2. Implement minimal code to pass
3. Refactor while keeping tests green
