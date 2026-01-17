"""Common exceptions for the application."""

class NoRetryException(Exception):
    """Exception that should not be retried by Temporal."""
    pass
