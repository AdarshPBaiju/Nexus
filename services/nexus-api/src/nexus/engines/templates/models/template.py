"""
nexus.engines.templates.models.template - Template Definition Model.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class TemplateDefinition(TenantScopedModel):
    """
    Sandboxed AST IR template definition compiling to all 13 physical and digital targets.
    """

    code = models.CharField(
        max_length=64,
        db_index=True,
        help_text=_("Unique identifier (e.g. INVOICE_A4_STANDARD, RECEIPT_80MM_THERMAL)."),
    )
    name = models.CharField(
        max_length=128,
        help_text=_("Human-readable template display name."),
    )
    category = models.CharField(
        max_length=32,
        db_index=True,
        default="TRANSACTIONAL",
        help_text=_("Category (TRANSACTIONAL, POS_RECEIPT, MARKETING, STATUTORY)."),
    )
    supported_targets = models.JSONField(
        default=list,
        help_text=_("List of supported output targets among the 13 canonical targets."),
    )
    ast_definition = models.JSONField(
        default=dict,
        help_text=_("Canonical Sandboxed AST Intermediate Representation (IR)."),
    )
    is_system_locked = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_("Whether HQ compliance slots are locked from tenant editing."),
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_("Whether template is active for resolution."),
    )
    version = models.IntegerField(
        default=1,
        help_text=_("Monotonically increasing template revision number."),
    )

    class Meta:
        app_label = "templates"
        db_table = "tpl_definition"
        unique_together = [("tenant_id", "code")]
        ordering = ["code", "id"]

    def __str__(self) -> str:
        return f"Template({self.code} [{self.category}] v{self.version})"
