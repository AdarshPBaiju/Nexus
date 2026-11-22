"""
nexus.engines.resource_scheduler.models.allocation - Non-Overlapping Resource Allocation model.
"""
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.engines.commerce_folio.models.folio import CommerceFolio
from nexus.engines.resource_scheduler.models.resource import VenueResource
from nexus.libs.models.tenant_scoped import TenantScopedModel


class ResourceAllocation(TenantScopedModel):
    """
    Time-bound reservation or active session allocation for a VenueResource.
    Enforces non-overlapping time constraints.
    """

    class AllocationStatus(models.TextChoices):
        CONFIRMED = "CONFIRMED", _("Confirmed Reservation")
        ACTIVE = "ACTIVE", _("Active Live Session")
        HOLD_LOCKED = "HOLD_LOCKED", _("Temporary Checkout Hold")
        RELEASED = "RELEASED", _("Released / Completed")
        CANCELLED = "CANCELLED", _("Cancelled")

    resource = models.ForeignKey(
        VenueResource,
        on_delete=models.PROTECT,
        related_name="allocations",
        help_text=_("Venue resource allocated."),
    )
    folio = models.ForeignKey(
        CommerceFolio,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="allocations",
        help_text=_("Commerce folio billed for this allocation."),
    )
    start_time = models.DateTimeField(
        db_index=True,
    )
    end_time = models.DateTimeField(
        db_index=True,
    )
    status = models.CharField(
        max_length=32,
        choices=AllocationStatus.choices,
        default=AllocationStatus.CONFIRMED,
        db_index=True,
    )

    class Meta:
        app_label = "resource_scheduler"
        db_table = "res_resource_allocation"
        ordering = ["start_time", "id"]
        indexes = [
            models.Index(fields=["resource", "start_time", "end_time"]),
            models.Index(fields=["tenant_id", "status"]),
        ]

    def __str__(self) -> str:
        return f"Allocation({self.resource.code}: {self.start_time} - {self.end_time} [{self.status}])"
