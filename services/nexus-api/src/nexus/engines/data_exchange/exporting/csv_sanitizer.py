"""
nexus.engines.data_exchange.exporting.csv_sanitizer - CSV formula-injection defense.
"""

from __future__ import annotations

from typing import Any

DANGEROUS_PREFIXES = ("=", "+", "-", "@", "|", "%", "\t", "\r")


class CsvFormulaSanitizer:
    """Sanitizes field values to prevent CSV and Excel formula injection exploits."""

    @classmethod
    def sanitize_value(cls, value: Any) -> Any:
        """Escape value if it begins with a formula trigger character."""
        if not isinstance(value, str):
            return value

        stripped = value.lstrip()
        if stripped and any(stripped.startswith(prefix) for prefix in DANGEROUS_PREFIXES):
            # Prepend single apostrophe to force Excel to treat as plain literal text
            return f"'{value}"

        return value

    @classmethod
    def sanitize_row(cls, row: dict[str, Any]) -> dict[str, Any]:
        """Sanitize an entire row dictionary for export."""
        return {k: cls.sanitize_value(v) for k, v in row.items()}
