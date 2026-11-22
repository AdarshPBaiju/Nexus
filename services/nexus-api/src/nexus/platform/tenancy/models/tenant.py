"""
nexus.platform.tenancy.models.tenant - Root cell isolation Tenant model.
"""

from __future__ import annotations

import re

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.ids import new_uuid7


class Tenant(models.Model):
    """
    Root multi-tenant boundary. Every entity in Project Nexus isolates under a Tenant.
    """

    class Status(models.TextChoices):
        PROVISIONING = "PROVISIONING", _("Provisioning")
        ACTIVE = "ACTIVE", _("Active")
        SUSPENDED = "SUSPENDED", _("Suspended")
        DRAINING = "DRAINING", _("Draining")

    id = models.UUIDField(
        primary_key=True,
        default=new_uuid7,
        editable=False,
    )
    slug = models.SlugField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text=_("Unique URL-safe identifier for tenant workspace routing."),
    )
    legal_name = models.CharField(
        max_length=255,
        help_text=_("Statutory registered legal name of the organization."),
    )
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.PROVISIONING,
        db_index=True,
    )
    home_region = models.CharField(
        max_length=32,
        default="ap-south-1",
        help_text=_("Data residency home cloud region (e.g. ap-south-1, us-east-1)."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        app_label = "tenancy"
        db_table = "tenancy_tenant"
        ordering = ["-created_at", "id"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
        ]

    @property
    def is_operational(self) -> bool:
        """Check if tenant is eligible to process business transactions."""
        return self.status == self.Status.ACTIVE

    def clean(self) -> None:
        super().clean()
        self._validate_slug()

    def _validate_slug(self) -> None:
        if not self.slug:
            raise ValidationError({"slug": _("Tenant slug is required.")})
        if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", self.slug):
            raise ValidationError(
                {"slug": _("Slug must be lowercase alphanumeric with single hyphens.")}
            )

    def __str__(self) -> str:
        return f"Tenant({self.slug}, status={self.status})"
