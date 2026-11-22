"""
nexus.platform.tenancy.models.brand - Brand and commercial trade identity model.
"""

from __future__ import annotations

import re

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class Brand(TenantScopedModel):
    """
    Brand trade identity under which one or more branches operate.
    """

    name = models.CharField(
        max_length=128,
        help_text=_("Public commercial brand name (e.g. Nexus Café)."),
    )
    slug = models.SlugField(
        max_length=64,
        db_index=True,
        help_text=_("URL-safe slug for brand-scoped routing."),
    )
    logo_url = models.URLField(
        max_length=512,
        blank=True,
        default="",
        help_text=_("Public URL to brand vector/raster logo asset."),
    )
    theme_tokens_json = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("JSON dictionary of brand-specific design tokens."),
    )

    class Meta:
        app_label = "tenancy"
        db_table = "tenancy_brand"
        ordering = ["name", "id"]
        unique_together = [("tenant_id", "slug")]

    def clean(self) -> None:
        super().clean()
        self._validate_slug()

    def _validate_slug(self) -> None:
        if not self.slug:
            raise ValidationError({"slug": _("Brand slug is required.")})
        if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", self.slug):
            raise ValidationError(
                {"slug": _("Slug must be lowercase alphanumeric with single hyphens.")}
            )

    def __str__(self) -> str:
        return f"Brand({self.name}, slug={self.slug})"
