"""
nexus.libs.models.versioned - Versioned aggregate model for optimistic concurrency locking.
"""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class VersionedAggregateModel(models.Model):
    """
    Abstract model providing optimistic concurrency control via integer version.
    Enforces RFC 9110 If-Match preconditions.
    """

    version = models.PositiveIntegerField(
        default=1,
        db_index=True,
        help_text=_("Monotonically increasing version counter for optimistic concurrency."),
    )

    class Meta:
        abstract = True

    def increment_version(self) -> int:
        """Increment and return the next version counter."""
        self.version += 1
        return self.version

    def verify_version(self, expected_version: int) -> None:
        """Verify the current entity version matches the expected precondition."""
        if self.version != expected_version:
            raise ValidationError(
                _("Concurrency conflict: current version %(curr)d does not match expected %(exp)d")
                % {"curr": self.version, "exp": expected_version}
            )
