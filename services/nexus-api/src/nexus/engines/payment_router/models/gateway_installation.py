"""
nexus.engines.payment_router.models.gateway_installation - Tenant Gateway Plugin Installation Model.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class GatewayInstallation(TenantScopedModel):
    """
    Tenant/Branch enabled payment gateway plugin with encrypted credentials.
    """

    class Gateway(models.TextChoices):
        STRIPE = "STRIPE", _("Stripe Payment Intents")
        RAZORPAY = "RAZORPAY", _("Razorpay Payment Gateway")
        ADYEN = "ADYEN", _("Adyen Global Payments")
        DIRECT_UPI = "DIRECT_UPI", _("Direct NPCI UPI QR")
        EDC_LOCAL = "EDC_LOCAL", _("Local Card EDC Machine")

    gateway_code = models.CharField(
        max_length=32,
        choices=Gateway.choices,
        db_index=True,
        help_text=_("Standard payment gateway identifier."),
    )
    name = models.CharField(
        max_length=128,
        help_text=_("Human-readable label for this gateway configuration."),
    )
    encrypted_credentials = models.TextField(
        help_text=_("KMS envelope-encrypted credential JSON payload."),
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_("Active routing eligibility flag."),
    )

    class Meta:
        app_label = "payment_router"
        db_table = "pay_gateway_installation"
        unique_together = [("tenant_id", "gateway_code")]
        ordering = ["gateway_code", "id"]

    def __str__(self) -> str:
        return f"GatewayInstallation({self.gateway_code} [active={self.is_active}])"
