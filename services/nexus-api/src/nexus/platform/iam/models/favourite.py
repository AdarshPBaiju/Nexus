"""
nexus.platform.iam.models.favourite - Universal User Favourite Entity model.
"""
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class UserFavourite(TenantScopedModel):
    """
    Universal polymorphic user favourite record for records, views, and filter presets.
    Covered by idx_fav_member_lookup for zero-N+1 EXISTS annotations.
    """

    user_id = models.UUIDField(
        db_index=True,
        help_text=_("Staff or user identity who favorited the entity."),
    )
    entity_type = models.CharField(
        max_length=64,
        db_index=True,
        help_text=_("Polymorphic entity type (e.g. order, folio, customer, report)."),
    )
    entity_id = models.UUIDField(
        db_index=True,
        help_text=_("UUID of the favorited record."),
    )

    class Meta:
        app_label = "iam"
        db_table = "platform_user_favourite"
        unique_together = [("tenant_id", "user_id", "entity_type", "entity_id")]
        indexes = [
            models.Index(
                fields=["tenant_id", "user_id", "entity_type", "entity_id"],
                name="idx_fav_member_lookup",
            ),
        ]

    def __str__(self) -> str:
        return f"Fav({self.user_id} -> {self.entity_type}:{self.entity_id})"
