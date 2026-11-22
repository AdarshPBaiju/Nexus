"""
nexus.extensions.base.docs_basic.models.document_template - Document template model.
"""

from __future__ import annotations

import uuid
from typing import Any, Self

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class DocumentTemplate(TenantScopedModel):
    """
    Template layout definition for thermal receipts, tax invoices, and kitchen slips.
    """

    class TemplateType(models.TextChoices):
        RECEIPT_THERMAL = "RECEIPT_THERMAL", _("Thermal Receipt Slip")
        INVOICE_TAX_A4 = "INVOICE_TAX_A4", _("Tax Invoice A4 Document")
        KOT_SLIP = "KOT_SLIP", _("Kitchen Order Ticket Slip")

    class WidthType(models.TextChoices):
        WIDTH_80MM = "80MM", _("80mm Thermal Paper")
        WIDTH_58MM = "58MM", _("58mm Thermal Paper")
        A4 = "A4", _("Standard A4 Sheet")

    name = models.CharField(
        max_length=120,
        help_text=_("Template display label."),
    )
    template_type = models.CharField(
        max_length=32,
        choices=TemplateType.choices,
        default=TemplateType.RECEIPT_THERMAL,
        db_index=True,
        help_text=_("Functional output document category."),
    )
    width_type = models.CharField(
        max_length=16,
        choices=WidthType.choices,
        default=WidthType.WIDTH_80MM,
        help_text=_("Physical print target width."),
    )
    header_logo_url = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text=_("Monochrome or raster bitmap asset URL for printer header."),
    )
    footer_text_json = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Configurable footer text (Wi-Fi password, greeting, return terms)."),
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_("Template active status flag."),
    )

    class Meta:
        db_table = "docs_document_template"
        ordering = ["template_type", "name"]
        indexes = [
            models.Index(fields=["tenant_id", "template_type", "is_active"]),
        ]
        unique_together = ("tenant_id", "name")

    @classmethod
    def create_template(
        cls,
        tenant_id: uuid.UUID,
        name: str,
        template_type: str = "RECEIPT_THERMAL",
        width_type: str = "80MM",
    ) -> Self:
        return cls.objects.create(
            tenant_id=tenant_id,
            name=name,
            template_type=template_type,
            width_type=width_type,
            header_logo_url="",
            footer_text_json={"wifi": "GuestWifi", "thanks": "Thank you for your visit!"},
            is_active=True,
        )

    def get_footer_text(self, key: str, default: str = "") -> str:
        data: dict[str, Any] = self.footer_text_json or {}
        return str(data.get(key, default))

    def __str__(self) -> str:
        return f"DocumentTemplate({self.name}, type={self.template_type}, width={self.width_type})"
