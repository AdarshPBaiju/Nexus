"""
nexus.extensions.commerce.cafe_qsr.models.menu_category - Menu category model.
"""

from __future__ import annotations

import uuid
from typing import Any, Self

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class MenuCategory(TenantScopedModel):
    """
    Categorical taxonomy node for café and QSR food and beverage menus.
    """

    name = models.CharField(
        max_length=120,
        help_text=_("Human-readable category label (e.g. Espresso Bar, Artisan Pastries)."),
    )
    slug = models.SlugField(
        max_length=120,
        help_text=_("URL and API slug identifier."),
    )
    sort_order = models.IntegerField(
        default=0,
        db_index=True,
        help_text=_("Display sort sequence on counter POS and digital menus."),
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_("Controls whether category items appear on operational POS screens."),
    )
    available_times_json = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("JSON configuration for category operating day/time windows."),
    )

    class Meta:
        db_table = "cafe_menu_category"
        ordering = ["sort_order", "name"]
        indexes = [
            models.Index(fields=["tenant_id", "is_active", "sort_order"]),
        ]
        unique_together = ("tenant_id", "slug")

    @classmethod
    def create_category(
        cls,
        tenant_id: uuid.UUID,
        name: str,
        slug: str,
        sort_order: int = 0,
    ) -> Self:
        return cls.objects.create(
            tenant_id=tenant_id,
            name=name,
            slug=slug,
            sort_order=sort_order,
            is_active=True,
            available_times_json={"all_day": True},
        )

    def is_available(self, current_hour_minute: str | None = None) -> bool:
        if not self.is_active:
            return False
        config: dict[str, Any] = self.available_times_json or {}
        if config.get("all_day", True):
            return True
        start: str | None = config.get("start_time")
        end: str | None = config.get("end_time")
        if start and end and current_hour_minute:
            return start <= current_hour_minute <= end
        return True

    def __str__(self) -> str:
        return f"MenuCategory({self.name}, sort={self.sort_order})"
