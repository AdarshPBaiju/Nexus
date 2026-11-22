"""
nexus.engines.invoicing.models.routing - Multi-Printer Split Routing Rule Model.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.engines.invoicing.models.printer import PrinterDevice
from nexus.libs.models.tenant_scoped import TenantScopedModel


class PrintRouteRule(TenantScopedModel):
    """
    Routing rule dispatching specific document types to designated physical printer endpoints.
    """

    class DocumentType(models.TextChoices):
        RECEIPT = "RECEIPT", _("Customer POS Receipt")
        TAX_INVOICE = "TAX_INVOICE", _("A4 Statutory Tax Invoice")
        KOT_BARISTA = "KOT_BARISTA", _("Barista Drink Ticket")
        KOT_KITCHEN = "KOT_KITCHEN", _("Kitchen Food Ticket")
        CUP_LABEL = "CUP_LABEL", _("Adhesive Cup / Item Label")

    document_type = models.CharField(
        max_length=32,
        choices=DocumentType.choices,
        db_index=True,
        help_text=_("Document category triggering this route rule."),
    )
    target_printer = models.ForeignKey(
        PrinterDevice,
        on_delete=models.CASCADE,
        related_name="routing_rules",
        help_text=_("Destination hardware printer device."),
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_("Active status."),
    )

    class Meta:
        app_label = "invoicing"
        db_table = "inv_print_route_rule"
        ordering = ["document_type", "id"]

    def __str__(self) -> str:
        return f"PrintRoute({self.document_type} -> {self.target_printer.name})"
