# SignalLayer Workflows

**AI Coding Agent Orchestration Platform** - Orchestrates coding agents using GitHub projects as the "brain". Uses Temporal workflows to coordinate AI agents (Planner, Researcher, Reporter, Orchestrator) that process GitHub issues, conduct research, and manage development tasks. Built with FastAPI for automatic REST API generation.

## Features

- **Automatic Route Generation**: REST endpoints created dynamically from workflow definitions.
- **Activity Proxies**: Clean `.execute()` syntax for calling activities from workflows with pre-configured defaults.
- **Type-Safe**: Pydantic models extracted from workflow type hints for validation and documentation.
- **Modular Architecture**: Clear separation between execution, discovery, and web layers.

## Quick Start

### Installation

```bash
uv sync --all-extras
```

### Running

Start both web application and worker (recommended for dev):
```bash
uv run honcho start
```

Or start them individually:

**Web API**:
```bash
uvicorn src.web.main:app --reload
```

**Worker**:
```bash
python -m src.worker.main
```

## Development

Run tests:
```bash
pytest
```

## Documentation

Detailed documentation is available in the [docs/](docs/README.md) directory:

- [Architecture & DI](docs/architecture.md)
- [Decorators & Activity Proxies](docs/decorators.md)
- [Dynamic API Generation](docs/api.md)
