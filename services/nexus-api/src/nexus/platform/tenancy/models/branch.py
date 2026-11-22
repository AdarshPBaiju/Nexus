"""
nexus.platform.tenancy.models.branch - Physical branch operational location model.
"""

from __future__ import annotations

import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel
from nexus.platform.tenancy.models.brand import Brand
from nexus.platform.tenancy.models.legal_entity import LegalEntity


class Branch(TenantScopedModel):
    """
    Physical branch or store operational location.
    """

    legal_entity = models.ForeignKey(
        LegalEntity,
        on_delete=models.PROTECT,
        related_name="branches",
        help_text=_("Statutory legal entity owning this operational branch."),
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.PROTECT,
        related_name="branches",
        help_text=_("Commercial brand trade name for this branch."),
    )
    name = models.CharField(
        max_length=128,
        help_text=_("Operational name (e.g. Nexus Café - Indiranagar)."),
    )
    code = models.CharField(
        max_length=32,
        help_text=_("Unique branch code within tenant (e.g. BLR-01)."),
    )
    iana_timezone = models.CharField(
        max_length=64,
        default="UTC",
        help_text=_("IANA timezone string (e.g. Asia/Kolkata)."),
    )
    business_day_cutoff = models.TimeField(
        default=datetime.time(4, 0, 0),
        help_text=_("Time of day when the business operational day closes (e.g. 04:00:00)."),
    )

    class Meta:
        app_label = "tenancy"
        db_table = "tenancy_branch"
        ordering = ["code", "id"]
        unique_together = [("tenant_id", "code")]
        indexes = [
            models.Index(fields=["tenant_id", "code"]),
        ]

    def clean(self) -> None:
        super().clean()
        self._validate_parent_tenants()

    def _validate_parent_tenants(self) -> None:
        if self.legal_entity_id and self.legal_entity.tenant_id != self.tenant_id:
            raise ValidationError(
                {"legal_entity": _("Legal entity tenant does not match branch tenant.")}
            )
        if self.brand_id and self.brand.tenant_id != self.tenant_id:
            raise ValidationError({"brand": _("Brand tenant does not match branch tenant.")})

    def __str__(self) -> str:
        return f"Branch({self.code} - {self.name})"
