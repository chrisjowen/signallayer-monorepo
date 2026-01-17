# Definition of Done

## Overview
This document outlines the criteria that must be met before a task, user story, or feature can be considered complete.

## Code Quality
- [ ] Code follows PEP 8 style guidelines
- [ ] Code is formatted with `ruff format` (or `black`)
- [ ] Code passes `ruff check` linting
- [ ] Code passes `mypy` type checking
- [ ] No static analysis warnings from CodeQL
- [ ] Code complexity is reasonable (checked with `radon`)
- [ ] All Pydantic models have proper type annotations

## Testing
- [ ] Unit tests written with `pytest` and passing
- [ ] Integration tests written and passing (where applicable)
- [ ] Temporal workflow and activity tests written
- [ ] FastAPI endpoint tests written with `TestClient`
- [ ] Test coverage meets project standards (>80%)
- [ ] Edge cases and error scenarios covered
- [ ] All async code properly tested

## Documentation
- [ ] Docstrings follow Google or NumPy style
- [ ] FastAPI endpoints have proper descriptions and response models
- [ ] Pydantic models have field descriptions
- [ ] Temporal workflow and activity docstrings complete
- [ ] README updated if public interfaces changed
- [ ] Type hints present on all functions

## Code Review
- [ ] Code has been peer reviewed
- [ ] All review comments addressed
- [ ] No blocking issues remain

## Deployment
- [ ] Changes merged to appropriate branch
- [ ] Build pipeline passes
- [ ] Deployment verified in target environment

## Verification
- [ ] Acceptance criteria met
- [ ] Functionality verified by stakeholder/QA
- [ ] No regression in existing features
