"""
nexus.platform.iam.models.staff_role_assignment - Role assignment for staff profiles.
"""

from __future__ import annotations

import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel
from nexus.platform.iam.models.staff_profile import StaffProfile


class StaffRoleAssignment(TenantScopedModel):
    """
    Connects a StaffProfile to a role slug within a specific branch or global scope.
    """

    staff = models.ForeignKey(
        StaffProfile,
        on_delete=models.CASCADE,
        related_name="role_assignments",
        help_text=_("Staff profile holding this role assignment."),
    )
    role_slug = models.SlugField(
        max_length=64,
        db_index=True,
        help_text=_("Standard role identifier (e.g. cashier, manager, barista)."),
    )
    branch_scope_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        help_text=_("Optional branch scoping UUID (null denotes all branches)."),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Designates whether this role assignment is currently active."),
    )

    class Meta:
        app_label = "iam"
        db_table = "iam_staff_role_assignment"
        ordering = ["staff", "role_slug", "id"]
        indexes = [
            models.Index(fields=["tenant_id", "role_slug"]),
        ]

    def applies_to_branch(self, branch_id: uuid.UUID) -> bool:
        """Check if role applies globally or to the specified branch."""
        if not self.is_active:
            return False
        return self.branch_scope_id is None or self.branch_scope_id == branch_id

    def __str__(self) -> str:
        return f"RoleAssignment({self.staff_id}: {self.role_slug})"
