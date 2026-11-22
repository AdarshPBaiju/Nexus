"""
nexus.extensions.commerce.cafe_qsr.models.modifier_group - Modifier group domain model.
"""

from __future__ import annotations

import uuid
from typing import Self

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class MenuModifierGroup(TenantScopedModel):
    """
    Modifier choice group (e.g. Milk Choice, Sweetener Level, Shot Count, Size).
    """

    name = models.CharField(
        max_length=100,
        help_text=_("Modifier group title displayed to cashier/customer."),
    )
    min_selection = models.PositiveIntegerField(
        default=0,
        help_text=_("Minimum selections required (e.g. 1 for mandatory size/milk)."),
    )
    max_selection = models.PositiveIntegerField(
        default=1,
        help_text=_("Maximum allowed selections (e.g. 1 for single choice, 5 for syrups)."),
    )
    is_required = models.BooleanField(
        default=False,
        help_text=_("Fast flag indicating customer must pick at least min_selection options."),
    )
    sort_order = models.IntegerField(
        default=0,
        db_index=True,
        help_text=_("Display sequence in modifier customization modal."),
    )

    class Meta:
        db_table = "cafe_modifier_group"
        ordering = ["sort_order", "name"]
        indexes = [
            models.Index(fields=["tenant_id", "sort_order"]),
        ]

    @classmethod
    def create_group(
        cls,
        tenant_id: uuid.UUID,
        name: str,
        min_selection: int = 0,
        max_selection: int = 1,
    ) -> Self:
        return cls.objects.create(
            tenant_id=tenant_id,
            name=name,
            min_selection=min_selection,
            max_selection=max_selection,
            is_required=(min_selection > 0),
            sort_order=0,
        )

    def validate_selection_count(self, count: int) -> bool:
        return self.min_selection <= count <= self.max_selection

    def __str__(self) -> str:
        req = "REQUIRED" if self.is_required else "OPTIONAL"
        return (
            f"MenuModifierGroup({self.name}, [{self.min_selection}..{self.max_selection}], {req})"
        )
