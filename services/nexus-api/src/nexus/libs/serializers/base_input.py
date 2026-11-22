"""
nexus.libs.serializers.base_input - Strict input serializer kernel.
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from rest_framework import serializers

from nexus.libs.serializers.sentinels import UNSET

TDto = TypeVar("TDto")


class BaseNexusInputSerializer(serializers.Serializer, Generic[TDto]):
    """
    Base input serializer enforcing unknown-field rejection and typed Command DTO emission.
    """

    extra_fields = "reject"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data: Any) -> dict[str, Any]:
        if not isinstance(data, dict):
            raise serializers.ValidationError("Expected a dictionary of key-value pairs.")
        self._validate_no_unknown_fields(data)
        ret = super().to_internal_value(data)
        if getattr(self, "partial", False):
            self._fill_unset_keys(ret, data)
        return ret

    def _validate_no_unknown_fields(self, data: dict[str, Any]) -> None:
        if self.extra_fields == "reject":
            allowed = set(self.fields.keys())
            provided = set(data.keys())
            unknown = provided - allowed
            if unknown:
                raise serializers.ValidationError(
                    {key: ["Unknown parameter is not accepted."] for key in sorted(unknown)}
                )

    def _fill_unset_keys(self, ret: dict[str, Any], data: dict[str, Any]) -> None:
        for field_name in self.fields:
            if field_name not in data:
                ret[field_name] = UNSET

    def to_command_dto(self) -> TDto:
        """Transform validated data into an immutable, strongly-typed Command DTO."""
        if not hasattr(self, "_validated_data"):
            raise RuntimeError("Must call is_valid() before emitting command DTO.")
        return self.create_command_dto(self.validated_data)

    def create_command_dto(self, validated_data: dict[str, Any]) -> TDto:
        """Subclasses must implement this method to instantiate the frozen DTO."""
        raise NotImplementedError("Subclasses must implement create_command_dto()")
