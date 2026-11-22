"""
nexus.extensions.commerce.cafe_qsr.models.item_modifier_assignment - Menu item modifier link.
"""

from __future__ import annotations

import uuid
from typing import Self

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class MenuItemModifierAssignment(TenantScopedModel):
    """
    Associative relationship linking a MenuItem to an eligible MenuModifierGroup.
    """

    item = models.ForeignKey(
        "nexus_cafe_qsr_commerce.MenuItem",
        on_delete=models.CASCADE,
        related_name="modifier_assignments",
        help_text=_("Associated menu item."),
    )
    modifier_group = models.ForeignKey(
        "nexus_cafe_qsr_commerce.MenuModifierGroup",
        on_delete=models.CASCADE,
        related_name="item_assignments",
        help_text=_("Associated modifier choice group."),
    )
    sort_order = models.IntegerField(
        default=0,
        db_index=True,
        help_text=_("Order in which modifier group is presented on item customization."),
    )

    class Meta:
        db_table = "cafe_item_modifier_assignment"
        ordering = ["item", "sort_order"]
        indexes = [
            models.Index(fields=["tenant_id", "item_id", "sort_order"]),
        ]
        unique_together = ("tenant_id", "item_id", "modifier_group_id")

    @classmethod
    def assign_group_to_item(
        cls,
        tenant_id: uuid.UUID,
        item_id: uuid.UUID,
        modifier_group_id: uuid.UUID,
        sort_order: int = 0,
    ) -> Self:
        return cls.objects.create(
            tenant_id=tenant_id,
            item_id=item_id,
            modifier_group_id=modifier_group_id,
            sort_order=sort_order,
        )

    def __str__(self) -> str:
        return f"MenuItemModifierAssignment(item={self.item_id}, group={self.modifier_group_id})"
