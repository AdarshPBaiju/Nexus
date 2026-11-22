"""
nexus.engines.discounts.models.coupon - Coupon pools and voucher redemption models.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.engines.discounts.models.campaign import DiscountCampaign
from nexus.libs.models.tenant_scoped import TenantScopedModel


class DiscountCouponPool(TenantScopedModel):
    """
    Collection of single-use or multi-use coupon vouchers for a campaign.
    """

    campaign = models.ForeignKey(
        DiscountCampaign,
        on_delete=models.CASCADE,
        related_name="coupon_pools",
    )
    pool_code = models.CharField(max_length=64, db_index=True)
    max_redemptions_total = models.PositiveIntegerField(
        default=0,
        help_text=_("0 denotes unlimited redemptions up to campaign budget."),
    )
    max_redemptions_per_customer = models.PositiveIntegerField(default=1)
    redemptions_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        app_label = "discounts"
        db_table = "disc_coupon_pool"
        ordering = ["pool_code", "id"]

    def __str__(self) -> str:
        return (
            f"CouponPool({self.pool_code} [{self.redemptions_count}/{self.max_redemptions_total}])"
        )


class DiscountCouponCode(TenantScopedModel):
    """
    Individual encrypted/hashed coupon voucher with usage counters.
    """

    pool = models.ForeignKey(
        DiscountCouponPool,
        on_delete=models.CASCADE,
        related_name="codes",
    )
    code_hash = models.CharField(
        max_length=64,
        db_index=True,
        help_text=_("Cryptographic HMAC-SHA256 blind index hash of coupon code."),
    )
    max_uses = models.PositiveIntegerField(default=1)
    uses_count = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        app_label = "discounts"
        db_table = "disc_coupon_code"
        unique_together = [("tenant_id", "code_hash")]
        ordering = ["-id"]

    def __str__(self) -> str:
        return f"CouponCode(hash={self.code_hash[:8]}... [{self.uses_count}/{self.max_uses}])"
