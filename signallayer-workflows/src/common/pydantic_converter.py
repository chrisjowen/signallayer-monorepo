"""Custom Temporal data converter for Pydantic models."""

from typing import Any

from pydantic import BaseModel
from temporalio.api.common.v1 import Payload
from temporalio.converter import (
    CompositePayloadConverter,
    DataConverter,
    DefaultPayloadConverter,
    JSONPlainPayloadConverter,
)


class PydanticJSONPayloadConverter(JSONPlainPayloadConverter):
    """Custom JSON payload converter that handles Pydantic models."""

    def to_payload(self, value: Any) -> Payload | None:
        """Convert a Pydantic model to a Temporal payload.

        Args:
            value: Value to convert (may be a Pydantic model)

        Returns:
            Temporal payload or None if not handled
        """
        # If it's a Pydantic model, serialize it to dict first
        if isinstance(value, BaseModel):
            # Use model_dump() to convert to dict with proper serialization
            value = value.model_dump(mode="json")

        # Let the parent class handle the JSON serialization
        return super().to_payload(value)

    def from_payload(self, payload: Payload, type_hint: type | None = None) -> Any:
        """Convert a Temporal payload to a Python value.

        Args:
            payload: Temporal payload to convert
            type_hint: Expected type hint (may be a Pydantic model class, list of models, etc.)

        Returns:
            Deserialized value (Pydantic-validated instance if possible)
        """
        # First deserialize from JSON to basic types (dict, list, int, etc.)
        value = super().from_payload(payload, type_hint=None)

        # If we have a type hint, attempt to use Pydantic to validate/instantiate it
        if type_hint is not None:
            try:
                from pydantic import TypeAdapter

                return TypeAdapter(type_hint).validate_python(value)
            except Exception:
                # If validation fails or TypeAdapter can't handle it, return the value as-is
                pass

        return value


class PydanticPayloadConverter(CompositePayloadConverter):
    """Payload converter that uses PydanticJSONPayloadConverter for JSON encoding."""

    def __init__(self) -> None:
        """Initialize with Pydantic-aware JSON converter."""
        # Get the default converters and replace JSON with our custom one
        default_converters = list(DefaultPayloadConverter.default_encoding_payload_converters)

        # Replace JSONPlainPayloadConverter with our Pydantic version
        converters = [
            PydanticJSONPayloadConverter() if isinstance(c, JSONPlainPayloadConverter) else c
            for c in default_converters
        ]

        super().__init__(*converters)


# Create a default data converter instance with Pydantic support
pydantic_data_converter = DataConverter(
    payload_converter_class=PydanticPayloadConverter,
)
