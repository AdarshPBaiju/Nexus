"""
nexus.platform.tenancy.models.legal_entity - Statutory Legal Entity model.
"""

from __future__ import annotations

import re

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class LegalEntity(TenantScopedModel):
    """
    Statutory legal corporation or registered business entity within a Tenant.
    """

    legal_name = models.CharField(
        max_length=255,
        help_text=_("Registered corporate legal name."),
    )
    tax_id = models.CharField(
        max_length=64,
        db_index=True,
        help_text=_("Tax registration number (GSTIN, VAT, EIN, etc.)."),
    )
    jurisdiction_code = models.CharField(
        max_length=16,
        help_text=_("ISO 3166-2 statutory jurisdiction code (e.g. IN-KA, US-DE)."),
    )
    functional_currency = models.CharField(
        max_length=3,
        default="USD",
        help_text=_("ISO 4217 3-letter currency code for financial bookkeeping."),
    )

    class Meta:
        app_label = "tenancy"
        db_table = "tenancy_legal_entity"
        ordering = ["-created_at", "id"]
        indexes = [
            models.Index(fields=["tenant_id", "tax_id"]),
        ]

    def clean(self) -> None:
        super().clean()
        self._validate_currency()

    def _validate_currency(self) -> None:
        if not re.match(r"^[A-Z]{3}$", self.functional_currency):
            raise ValidationError(
                {"functional_currency": _("Functional currency must be 3 uppercase letters.")}
            )

    def __str__(self) -> str:
        return f"LegalEntity({self.legal_name}, jur={self.jurisdiction_code})"
