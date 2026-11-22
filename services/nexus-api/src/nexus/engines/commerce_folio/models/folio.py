"""
nexus.engines.commerce_folio.models.folio - Polymorphic Commerce Folio Master model.
"""

from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class CommerceFolio(TenantScopedModel):
    """
    Unified master folio capturing all transactional charges across POS, Café, Gaming, and Rooms.
    Supports RFC 9110 If-Match optimistic locking via version integer.
    """

    class FolioStatus(models.TextChoices):
        OPEN = "OPEN", _("Open for Ordering")
        LOCKED_FOR_PAYMENT = "LOCKED_FOR_PAYMENT", _("Locked for Payment Tender")
        SETTLED = "SETTLED", _("Settled & Fully Paid")
        CLOSED = "CLOSED", _("Closed & Archived")

    folio_number = models.CharField(
        max_length=64,
        db_index=True,
        help_text=_("Unique human-readable folio number (e.g. FOL-2026-00001)."),
    )
    branch_id = models.UUIDField(
        db_index=True,
        help_text=_("Physical branch location where this folio was opened."),
    )
    customer_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        help_text=_("Optional customer identity linked to this folio."),
    )
    status = models.CharField(
        max_length=32,
        choices=FolioStatus.choices,
        default=FolioStatus.OPEN,
        db_index=True,
    )
    version = models.PositiveIntegerField(
        default=1,
        help_text=_("Optimistic concurrency locking sequence integer."),
    )
    currency = models.CharField(
        max_length=3,
        default="USD",
        help_text=_("Transaction currency code (ISO 4217)."),
    )
    subtotal_amount = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal("0.0000"),
    )
    tax_amount = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal("0.0000"),
    )
    total_amount = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal("0.0000"),
    )

    class Meta:
        app_label = "commerce_folio"
        db_table = "com_commerce_folio"
        unique_together = [("tenant_id", "folio_number")]
        ordering = ["-created_at", "id"]

    def __str__(self) -> str:
        return f"Folio({self.folio_number} [{self.status}] v{self.version})"
