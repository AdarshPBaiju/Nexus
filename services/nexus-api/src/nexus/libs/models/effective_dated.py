"""
nexus.libs.models.effective_dated - Effective dated model for temporal business records.
"""

from __future__ import annotations

import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class EffectiveDatedModel(models.Model):
    """
    Abstract model providing valid_from and valid_until temporal validity bounds.
    """

    valid_from = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        help_text=_("Beginning of validity window (inclusive)."),
    )
    valid_until = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        help_text=_("End of validity window (inclusive)."),
    )

    class Meta:
        abstract = True

    def is_effective(self, as_of: datetime.date | None = None) -> bool:
        """Check if record is active on a given date (defaults to today)."""
        target_date = as_of or timezone.now().date()
        if self.valid_from and target_date < self.valid_from:
            return False
        return not (self.valid_until and target_date > self.valid_until)

    def clean(self) -> None:
        super().clean()
        if self.valid_from and self.valid_until and self.valid_from > self.valid_until:
            raise ValidationError({"valid_until": _("valid_until must be on or after valid_from.")})
