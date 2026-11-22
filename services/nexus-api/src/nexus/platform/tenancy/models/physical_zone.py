"""
nexus.platform.tenancy.models.physical_zone - Physical zone operational area model.
"""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel
from nexus.platform.tenancy.models.branch import Branch


class PhysicalZone(TenantScopedModel):
    """
    Physical operational zone within a branch (Counter, Floor, Kitchen, Bar, VIP).
    """

    class ZoneType(models.TextChoices):
        COUNTER = "COUNTER", _("Counter POS Station")
        FLOOR = "FLOOR", _("Dining / Floor Area")
        KITCHEN = "KITCHEN", _("Kitchen / Prep Station")
        BAR = "BAR", _("Bar / Beverage Counter")
        VIP = "VIP", _("VIP / Private Gaming Room")

    branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT,
        related_name="zones",
        help_text=_("Branch containing this physical zone."),
    )
    name = models.CharField(
        max_length=128,
        help_text=_("Zone name (e.g. Counter 1, Kitchen Display Main)."),
    )
    zone_type = models.CharField(
        max_length=32,
        choices=ZoneType.choices,
        default=ZoneType.COUNTER,
        db_index=True,
    )

    class Meta:
        app_label = "tenancy"
        db_table = "tenancy_physical_zone"
        ordering = ["branch", "name", "id"]
        indexes = [
            models.Index(fields=["tenant_id", "zone_type"]),
        ]

    def clean(self) -> None:
        super().clean()
        self._validate_branch_tenant()

    def _validate_branch_tenant(self) -> None:
        if self.branch_id and self.branch.tenant_id != self.tenant_id:
            raise ValidationError({"branch": _("Branch tenant does not match zone tenant.")})

    def __str__(self) -> str:
        return f"PhysicalZone({self.name}, type={self.zone_type})"
