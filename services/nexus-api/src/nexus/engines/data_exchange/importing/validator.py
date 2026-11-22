"""
nexus.engines.data_exchange.importing.validator - Dry-run validation engine for staged rows.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from nexus.engines.data_exchange.importing.models import (
    ImportBatchSession,
)


class DryRunBatchValidator:
    """Executes multi-tier dry-run validations on staged import rows."""

    @classmethod
    def validate_session(
        cls,
        session: ImportBatchSession,
        mandatory_fields: Sequence[str],
        type_checks: Mapping[str, type] | None = None,
    ) -> tuple[int, int]:
        """Validate all staged rows for a session without mutating domain entities."""
        rows = list(session.staged_rows.all())
        valid_count = 0
        error_count = 0

        for staged in rows:
            errors = cls._validate_single_row(staged.raw_data, mandatory_fields, type_checks or {})
            staged.is_valid = len(errors) == 0
            staged.validation_errors = errors
            staged.save(update_fields=["is_valid", "validation_errors", "updated_at"])

            if staged.is_valid:
                valid_count += 1
            else:
                error_count += 1

        session.total_rows = len(rows)
        session.valid_rows = valid_count
        session.error_rows = error_count
        session.status = (
            ImportBatchSession.Status.READY
            if error_count == 0
            else ImportBatchSession.Status.STAGED
        )
        session.save(
            update_fields=["total_rows", "valid_rows", "error_rows", "status", "updated_at"]
        )
        return valid_count, error_count

    @staticmethod
    def _validate_single_row(
        data: Mapping[str, Any],
        mandatory_fields: Sequence[str],
        type_checks: Mapping[str, type],
    ) -> list[str]:
        errors: list[str] = []
        for field in mandatory_fields:
            if field not in data or data[field] is None or data[field] == "":
                errors.append(f"Missing mandatory field: {field}")

        for field, expected_type in type_checks.items():
            if (
                field in data
                and data[field] is not None
                and not isinstance(data[field], expected_type)
            ):
                errors.append(
                    f"Field '{field}' expected {expected_type.__name__}, got {type(data[field]).__name__}"
                )
        return errors
