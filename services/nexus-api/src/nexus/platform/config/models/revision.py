"""
nexus.platform.config.models.revision - Dynamic Config Change Revision model.
"""

from __future__ import annotations

import hashlib
import json

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.ids import new_uuid7
from nexus.platform.config.models.node import DynamicConfigNode


class DynamicConfigRevision(models.Model):
    """
    Versioned change proposal supporting pre-publish simulation and rollback.
    """

    class RevisionStatus(models.TextChoices):
        DRAFT = "DRAFT", _("Draft")
        SIMULATED = "SIMULATED", _("Simulated Dry-Run")
        PUBLISHED = "PUBLISHED", _("Published & Active")

    id = models.UUIDField(
        primary_key=True,
        default=new_uuid7,
        editable=False,
    )
    node = models.ForeignKey(
        DynamicConfigNode,
        on_delete=models.CASCADE,
        related_name="revisions",
        help_text=_("Config node targeted by this revision."),
    )
    author_id = models.UUIDField(
        help_text=_("Staff member authoring this configuration revision."),
    )
    change_summary = models.CharField(
        max_length=255,
        help_text=_("Business reason for configuration update."),
    )
    patch_json = models.JSONField(
        default=dict,
        help_text=_("RFC 7396 JSON merge patch representing proposed delta."),
    )
    status = models.CharField(
        max_length=32,
        choices=RevisionStatus.choices,
        default=RevisionStatus.DRAFT,
        db_index=True,
    )
    etag = models.CharField(
        max_length=64,
        db_index=True,
        help_text=_("Computed Weak ETag for cache invalidation."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        app_label = "dynamic_config"
        db_table = "config_dynamic_revision"
        ordering = ["-created_at", "id"]

    def compute_etag(self) -> str:
        canonical = json.dumps(self.patch_json, sort_keys=True)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]

    def save(self, *args, **kwargs) -> None:
        if not self.etag:
            self.etag = self.compute_etag()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"ConfigRevision({self.id}, status={self.status}, etag={self.etag})"
