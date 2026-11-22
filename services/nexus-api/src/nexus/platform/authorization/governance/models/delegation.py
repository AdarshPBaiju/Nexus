"""
nexus.platform.authorization.governance.models.delegation - Vacation Delegation model.
"""

from __future__ import annotations

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class VacationDelegation(TenantScopedModel):
    """
    Time-bounded peer delegation allowing a staff member to delegate roles during planned absences.
    """

    delegator_id = models.UUIDField(
        db_index=True,
        help_text=_("Staff member delegating their authority."),
    )
    delegatee_id = models.UUIDField(
        db_index=True,
        help_text=_("Peer staff member receiving delegated permissions."),
    )
    delegated_permissions = models.JSONField(
        default=list,
        help_text=_("List of permission codes delegated (must be subset of delegator grants)."),
    )
    valid_from = models.DateTimeField(
        db_index=True,
    )
    valid_to = models.DateTimeField(
        db_index=True,
    )
    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        app_label = "authorization"
        db_table = "authz_vacation_delegation"
        ordering = ["-valid_from", "id"]

    @property
    def is_currently_active(self) -> bool:
        now = timezone.now()
        return self.is_active and (self.valid_from <= now <= self.valid_to)

    def __str__(self) -> str:
        return f"Delegation({self.delegator_id} -> {self.delegatee_id} [{self.valid_from} - {self.valid_to}])"
