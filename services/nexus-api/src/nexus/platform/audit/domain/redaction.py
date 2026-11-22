"""
nexus.platform.audit.domain.redaction - PII & secret redaction and delta computation.
"""

from __future__ import annotations

from typing import Any, Mapping

ALWAYS_SCRUB_KEYS = frozenset(
    {
        "password",
        "secret",
        "pin",
        "cashier_pin",
        "card_number",
        "cvv",
        "auth_token",
        "private_key",
        "dek",
        "access_token",
        "refresh_token",
    }
)

IGNORED_KEYS = frozenset({"updated_at"})


class PiiRedactionDiffEngine:
    """Engine for scrubbing sensitive values and generating minimal change deltas."""

    @classmethod
    def scrub_dict(cls, data: Mapping[str, Any]) -> dict[str, Any]:
        """Scrub known secret and sensitive fields recursively."""
        scrubbed: dict[str, Any] = {}
        for key, value in data.items():
            lower_k = key.lower()
            if any(secret in lower_k for secret in ALWAYS_SCRUB_KEYS):
                scrubbed[key] = "[REDACTED_SECRET]"
            elif isinstance(value, dict):
                scrubbed[key] = cls.scrub_dict(value)
            else:
                scrubbed[key] = value
        return scrubbed

    @classmethod
    def compute_diff(
        cls, before: Mapping[str, Any], after: Mapping[str, Any]
    ) -> tuple[dict[str, Any], list[str]]:
        """
        Compute minimal difference between before and after states.
        Skips ignored metadata keys (such as updated_at) to avoid no-op bloat.
        """
        clean_before = cls.scrub_dict(before)
        clean_after = cls.scrub_dict(after)

        all_keys = set(clean_before.keys()) | set(clean_after.keys())
        diff: dict[str, Any] = {}
        changed_keys: list[str] = []

        for key in sorted(all_keys):
            if key in IGNORED_KEYS:
                continue
            val_b = clean_before.get(key)
            val_a = clean_after.get(key)
            if val_b != val_a:
                diff[key] = {"before": val_b, "after": val_a}
                changed_keys.append(key)

        return diff, changed_keys
