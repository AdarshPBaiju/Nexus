"""
nexus.libs.models.archivable - Soft archivable model for non-destructive lifecycle management.
"""

from __future__ import annotations

import uuid
from typing import Self

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class SoftArchivableModel(models.Model):
    """
    Abstract model enabling soft archival rather than destructive deletion.
    """

    is_archived = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_("Designates whether this record is archived rather than deleted."),
    )
    archived_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Timestamp when record was archived."),
    )
    archived_by_id = models.UUIDField(
        null=True,
        blank=True,
        help_text=_("UUID of the staff actor who archived this record."),
    )

    class Meta:
        abstract = True

    def archive(self, actor_id: uuid.UUID | None = None) -> Self:
        """Soft-archive this entity."""
        self.is_archived = True
        self.archived_at = timezone.now()
        self.archived_by_id = actor_id
        return self

    def restore(self) -> Self:
        """Restore this entity from archived state."""
        self.is_archived = False
        self.archived_at = None
        self.archived_by_id = None
        return self
