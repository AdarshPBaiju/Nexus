"""
nexus.libs.models.tenant_scoped - Base abstract model for tenant-isolated entities.
"""

from __future__ import annotations

import uuid
from typing import ClassVar

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.ids import new_uuid7


class TenantScopedModel(models.Model):
    """
    Abstract model enforcing tenant isolation via tenant_id.
    All subclasses automatically require Forced Row-Level Security (RLS).
    """

    id = models.UUIDField(
        primary_key=True,
        default=new_uuid7,
        editable=False,
    )
    tenant_id = models.UUIDField(
        db_index=True,
        editable=False,
        help_text=_("Foreign key reference to Tenant. Enforces Forced RLS isolation."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        abstract = True
        indexes: ClassVar[list[models.Index]] = [
            models.Index(fields=["tenant_id", "created_at"]),
        ]

    def clean(self) -> None:
        super().clean()
        self._validate_tenant_id()

    def _validate_tenant_id(self) -> None:
        if not self.tenant_id:
            raise ValidationError({"tenant_id": _("tenant_id is required and cannot be null.")})
        if not isinstance(self.tenant_id, uuid.UUID):
            try:
                self.tenant_id = uuid.UUID(str(self.tenant_id))
            except (ValueError, TypeError) as err:
                raise ValidationError({"tenant_id": _("tenant_id must be a valid UUID.")}) from err
