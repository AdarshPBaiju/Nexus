"""
nexus.engines.discounts.models.campaign - Marketing campaign, rules, and stacking groups.
"""

from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class DiscountStackingGroup(TenantScopedModel):
    """
    Defines mutual exclusivity and stacking rules between discount categories.
    """

    class StackingMode(models.TextChoices):
        EXCLUSIVE = "EXCLUSIVE", _("Exclusive (cannot stack)")
        STACKABLE = "STACKABLE", _("Stackable with other groups")
        CASCADE = "CASCADE", _("Priority Cascade (highest rank wins)")

    code = models.CharField(
        max_length=32,
        db_index=True,
        help_text=_("Stacking group identifier (e.g. ITEM_PROMO, CART_PROMO, COUPON)."),
    )
    name = models.CharField(max_length=128)
    stacking_mode = models.CharField(
        max_length=32,
        choices=StackingMode.choices,
        default=StackingMode.STACKABLE,
    )

    class Meta:
        app_label = "discounts"
        db_table = "disc_stacking_group"
        ordering = ["code", "id"]

    def __str__(self) -> str:
        return f"StackingGroup({self.code} [{self.stacking_mode}])"


class DiscountCampaign(TenantScopedModel):
    """
    Marketing campaign container with funding budget and temporal limits.
    """

    class SponsorType(models.TextChoices):
        INTERNAL = "INTERNAL", _("Internal Merchant Funded")
        BANK_PARTNER = "BANK_PARTNER", _("Bank / Payment Partner Co-Funded")
        BRAND = "BRAND", _("Brand / Supplier Funded")

    code = models.CharField(max_length=64, db_index=True)
    name = models.CharField(max_length=255)
    sponsor_type = models.CharField(
        max_length=32,
        choices=SponsorType.choices,
        default=SponsorType.INTERNAL,
    )
    budget_total = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal("0.0000"),
    )
    budget_consumed = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal("0.0000"),
    )
    start_at = models.DateTimeField(default=timezone.now)
    end_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        app_label = "discounts"
        db_table = "disc_campaign"
        ordering = ["-start_at", "id"]

    def __str__(self) -> str:
        return f"Campaign({self.code} - {self.name})"


class DiscountRuleDefinition(TenantScopedModel):
    """
    Condition-driven discount rule holding condition_ast, action_ast, and guardrails.
    """

    campaign = models.ForeignKey(
        DiscountCampaign,
        on_delete=models.CASCADE,
        related_name="rules",
    )
    stacking_group = models.ForeignKey(
        DiscountStackingGroup,
        on_delete=models.PROTECT,
        related_name="rules",
        null=True,
        blank=True,
    )
    rule_code = models.CharField(max_length=64, db_index=True)
    name = models.CharField(max_length=255)
    priority = models.PositiveIntegerField(default=100, db_index=True)
    condition_ast_json = models.JSONField(
        default=dict,
        help_text=_("Declarative condition AST evaluating order/item eligibility."),
    )
    action_ast_json = models.JSONField(
        default=dict,
        help_text=_("Declarative benefit archetype AST (PERCENTAGE, FIXED, OVERRIDE)."),
    )
    guardrail_policy_json = models.JSONField(
        default=dict,
        help_text=_("Revenue guardrails: max cap, margin floor, staff pin."),
    )
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        app_label = "discounts"
        db_table = "disc_rule_definition"
        ordering = ["priority", "id"]

    def __str__(self) -> str:
        return f"DiscountRule({self.rule_code} - P{self.priority})"
