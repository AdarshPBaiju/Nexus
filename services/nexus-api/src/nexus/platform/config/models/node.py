"""
nexus.platform.config.models.node - 6-Level Dynamic Config Node model.
"""

from __future__ import annotations

import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class DynamicConfigNode(TenantScopedModel):
    """
    Configuration storage node at one of the 6 inheritance levels.
    """

    PLATFORM_TENANT_ID = uuid.UUID(int=0)

    class ScopeLevel(models.TextChoices):
        PLATFORM = "PLATFORM", _("Level 0: Platform Global")
        TENANT = "TENANT", _("Level 1: Tenant Workspace")
        BRAND = "BRAND", _("Level 2: Commercial Brand")
        BRANCH = "BRANCH", _("Level 3: Physical Branch")
        ZONE = "ZONE", _("Level 4: Physical Zone")
        WORKSTATION = "WORKSTATION", _("Level 5: POS/KDS Station")

    scope_level = models.CharField(
        max_length=32,
        choices=ScopeLevel.choices,
        db_index=True,
        help_text=_("Level in the 6-tier inheritance hierarchy."),
    )
    scope_id = models.UUIDField(
        db_index=True,
        help_text=_("UUID of the target entity (Tenant ID, Branch ID, etc.)."),
    )
    config_json = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Configuration key-value pairs stored at this level."),
    )

    class Meta:
        app_label = "dynamic_config"
        db_table = "config_dynamic_node"
        unique_together = [("scope_level", "scope_id")]
        indexes = [
            models.Index(fields=["tenant_id", "scope_level"]),
        ]

    def clean(self) -> None:
        if self.scope_level == self.ScopeLevel.PLATFORM and not self.tenant_id:
            self.tenant_id = self.PLATFORM_TENANT_ID
        super().clean()

    def __str__(self) -> str:
        return f"ConfigNode({self.scope_level} : {self.scope_id})"
