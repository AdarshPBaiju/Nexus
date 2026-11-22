"""
nexus.platform.authorization.models.fls_rule - Field-Level Security (FLS) Classification model.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class FieldSecurityRule(TenantScopedModel):
    """
    Column-level classification governing data visibility (READ, MASKED, WRITE, HIDDEN).
    """

    class Classification(models.TextChoices):
        READ = "READ", _("Full Read Access")
        MASKED = "MASKED", _("Masked Field (Partial Redaction)")
        WRITE = "WRITE", _("Read & Write Access")
        HIDDEN = "HIDDEN", _("Strictly Hidden / Excluded from Wire")

    entity_type = models.CharField(
        max_length=64,
        db_index=True,
        help_text=_("Entity type name (e.g. customer, staff_profile, payment_tender)."),
    )
    field_name = models.CharField(
        max_length=64,
        db_index=True,
        help_text=_("Model field name governed by this security classification."),
    )
    classification = models.CharField(
        max_length=16,
        choices=Classification.choices,
        default=Classification.READ,
        db_index=True,
    )
    role_code = models.CharField(
        max_length=64,
        default="DEFAULT",
        help_text=_("Role code to which this column security rule applies."),
    )

    class Meta:
        app_label = "authorization"
        db_table = "authz_field_security_rule"
        unique_together = [("tenant_id", "entity_type", "field_name", "role_code")]
        indexes = [
            models.Index(fields=["tenant_id", "entity_type"]),
        ]

    def __str__(self) -> str:
        return (
            f"FLS({self.entity_type}.{self.field_name} -> {self.classification} [{self.role_code}])"
        )
