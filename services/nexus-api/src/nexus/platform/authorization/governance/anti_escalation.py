"""
nexus.platform.authorization.governance.anti_escalation - Anti-Privilege Escalation & Last Owner Guard.
"""
from __future__ import annotations

import uuid
from typing import Sequence

from django.core.exceptions import ValidationError

from nexus.platform.iam.models.staff_role_assignment import StaffRoleAssignment


class PrivilegeEscalationError(ValidationError):
    """Raised when an administrator attempts to grant permissions beyond their active scope."""


class PrivilegeEscalationGuard:
    """
    Enforces:
    1. Subset Grant Law: Administrators can only grant permissions they themselves actively hold.
    2. Last Owner Protection: Cannot delete, demote, or revoke the final remaining tenant_owner.
    """

    OWNER_ROLE = "tenant_owner"

    @classmethod
    def assert_subset_grant(
        cls,
        grantor_permissions: Sequence[str],
        requested_grants: Sequence[str],
    ) -> None:
        """Ensures granted permissions are a strict subset of grantor permissions."""
        grantor_set = set(grantor_permissions)
        for perm in requested_grants:
            if perm not in grantor_set:
                raise PrivilegeEscalationError(
                    f"Privilege Escalation Blocked: Cannot grant '{perm}' which you do not actively possess."
                )

    @classmethod
    def assert_not_last_owner(
        cls,
        tenant_id: uuid.UUID,
        target_staff_id: uuid.UUID,
    ) -> None:
        """Prevents revoking the last remaining active tenant_owner."""
        active_owners = StaffRoleAssignment.objects.filter(
            tenant_id=tenant_id,
            role_slug=cls.OWNER_ROLE,
            is_active=True,
        )
        if active_owners.count() <= 1 and active_owners.filter(staff_id=target_staff_id).exists():
            raise ValidationError(
                "Last Owner Invariant: Cannot revoke or demote the final remaining tenant_owner in workspace."
            )
