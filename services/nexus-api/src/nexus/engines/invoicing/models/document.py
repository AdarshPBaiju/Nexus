"""
nexus.engines.invoicing.models.document - Master Fiscal Invoice Document Model.
"""

from __future__ import annotations

import hashlib
import json

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class InvoiceDocument(TenantScopedModel):
    """
    Immutable master fiscal invoice document preserving frozen snapshot and WORM hash.
    """

    class Status(models.TextChoices):
        ISSUED = "ISSUED", _("Issued (Finalized)")
        PAID = "PAID", _("Paid in Full")
        CANCELLED = "CANCELLED", _("Cancelled (Credit Note Issued)")

    folio_id = models.UUIDField(
        db_index=True,
        help_text=_("Parent CommerceFolio UUID."),
    )
    customer_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        help_text=_("Customer UUID if named billing."),
    )
    document_number = models.CharField(
        max_length=64,
        db_index=True,
        help_text=_("Gapless allocated fiscal number (e.g. INV-2026-000042)."),
    )
    document_type = models.CharField(
        max_length=32,
        db_index=True,
        default="TAX_INVOICE",
        help_text=_("Document type (TAX_INVOICE, RECEIPT, CREDIT_NOTE)."),
    )
    financial_snapshot = models.JSONField(
        default=dict,
        help_text=_("Frozen immutable snapshot: lines, taxes, totals, tenders, and signatures."),
    )
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.ISSUED,
        db_index=True,
        help_text=_("Document state."),
    )
    worm_sha256 = models.CharField(
        max_length=64,
        db_index=True,
        help_text=_("Tamper-evident SHA-256 hash ensuring 8-year WORM compliance."),
    )

    class Meta:
        app_label = "invoicing"
        db_table = "inv_document"
        unique_together = [("tenant_id", "document_number")]
        ordering = ["-created_at", "id"]

    @classmethod
    def compute_worm_hash(cls, snapshot: dict) -> str:
        """Computes deterministic SHA-256 digest over normalized financial snapshot."""
        serialized = json.dumps(snapshot, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def __str__(self) -> str:
        return f"Invoice({self.document_number} [{self.document_type}]: {self.status})"
