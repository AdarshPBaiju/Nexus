"""
nexus.platform.authorization.models.grant - Multi-Dimensional Scoped Resource Grant model.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class ResourceGrant(TenantScopedModel):
    """
    Fine-grained authorization grant binding a user membership to a permission at a specific scope.
    """

    class ScopeLevel(models.TextChoices):
        TENANT = "TENANT", _("Tenant Workspace Level")
        BRAND = "BRAND", _("Brand Level")
        BRANCH = "BRANCH", _("Physical Branch Level")
        ZONE = "ZONE", _("Physical Zone Level")

    class GrantEffect(models.TextChoices):
        ALLOW = "ALLOW", _("Explicit Grant")
        DENY = "DENY", _("Explicit Deny (Overrides all allows)")

    membership_id = models.UUIDField(
        db_index=True,
        help_text=_("User workspace membership holding this grant."),
    )
    permission_code = models.CharField(
        max_length=128,
        db_index=True,
        help_text=_("Namespaced permission code granted or denied."),
    )
    scope_level = models.CharField(
        max_length=32,
        choices=ScopeLevel.choices,
        default=ScopeLevel.TENANT,
        db_index=True,
    )
    scope_id = models.UUIDField(
        db_index=True,
        help_text=_("UUID of the target scope entity (Branch ID, Zone ID, etc.)."),
    )
    effect = models.CharField(
        max_length=16,
        choices=GrantEffect.choices,
        default=GrantEffect.ALLOW,
        db_index=True,
    )

    class Meta:
        app_label = "authorization"
        db_table = "authz_resource_grant"
        indexes = [
            models.Index(fields=["tenant_id", "membership_id", "permission_code"]),
            models.Index(fields=["tenant_id", "scope_level", "scope_id"]),
        ]

    def __str__(self) -> str:
        return f"Grant({self.membership_id}: {self.permission_code} @ {self.scope_level} -> {self.effect})"
