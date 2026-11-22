"""
nexus.platform.iam.models.workspace_membership - User Workspace Membership model.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.ids import new_uuid7
from nexus.platform.iam.models.user import User
from nexus.platform.tenancy.models.tenant import Tenant


class UserWorkspaceMembership(models.Model):
    """
    Connects a global User identity to a specific Tenant workspace.
    """

    class MembershipStatus(models.TextChoices):
        INVITED = "INVITED", _("Invited")
        ACTIVE = "ACTIVE", _("Active")
        SUSPENDED = "SUSPENDED", _("Suspended")

    id = models.UUIDField(
        primary_key=True,
        default=new_uuid7,
        editable=False,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="workspace_memberships",
        help_text=_("Global user identity."),
    )
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="user_memberships",
        help_text=_("Tenant organization workspace."),
    )
    status = models.CharField(
        max_length=32,
        choices=MembershipStatus.choices,
        default=MembershipStatus.ACTIVE,
        db_index=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        app_label = "iam"
        db_table = "iam_workspace_membership"
        unique_together = [("user", "tenant")]
        ordering = ["-created_at", "id"]

    @property
    def is_operational(self) -> bool:
        """Assert membership and tenant are both operational."""
        return self.status == self.MembershipStatus.ACTIVE and self.tenant.is_operational

    def __str__(self) -> str:
        return f"Membership({self.user_id} @ {self.tenant_id}, status={self.status})"
