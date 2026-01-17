"""A dummy service to demonstrate dependency injection."""

class DummyService:
    """Mock service."""

    def get_greeting(self, name: str) -> str:
        """Return a greeting."""
        return f"Hello from DummyService, {name}!"
