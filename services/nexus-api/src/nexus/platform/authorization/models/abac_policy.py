"""
nexus.platform.authorization.models.abac_policy - Attribute-Based Access Control (ABAC) Policy model.
"""
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class AbacPolicyRule(TenantScopedModel):
    """
    Dynamic attribute guardrail rule evaluating contextual constraints (e.g. shift_open, max_amount).
    """

    class Effect(models.TextChoices):
        ALLOW = "ALLOW", _("Allow Access")
        DENY = "DENY", _("Deny Access (Explicit Deny)")

    permission_code = models.CharField(
        max_length=128,
        db_index=True,
        help_text=_("Permission code governed by this ABAC policy."),
    )
    rule_name = models.CharField(
        max_length=128,
        help_text=_("Descriptive rule title (e.g. Max Cashier Discount 20%)."),
    )
    expression_json = models.JSONField(
        default=dict,
        help_text=_("AST JSON expression specifying attribute predicates."),
    )
    effect = models.CharField(
        max_length=16,
        choices=Effect.choices,
        default=Effect.ALLOW,
        db_index=True,
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )

    class Meta:
        app_label = "authorization"
        db_table = "authz_abac_policy"
        indexes = [
            models.Index(fields=["tenant_id", "permission_code", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"ABAC({self.rule_name} -> {self.effect})"
