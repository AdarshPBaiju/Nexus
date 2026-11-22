"""
nexus.engines.notifications.models.credential - Encrypted Provider BYO Credentials.
"""
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class TenantChannelCredential(TenantScopedModel):
    """
    Tenant BYO channel provider credentials encrypted at rest with AES-256-GCM.
    """

    channel = models.CharField(
        max_length=16,
        db_index=True,
        help_text=_("Channel code (EMAIL, WHATSAPP, SMS, PUSH)."),
    )
    provider_code = models.CharField(
        max_length=32,
        db_index=True,
        help_text=_("Target provider code (e.g. RESEND, META_WHATSAPP, MSG91, FCM)."),
    )
    encrypted_config = models.TextField(
        help_text=_("Ciphertext payload encrypted with TenantEnvelopeCipher."),
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_("Active validity flag for this credential."),
    )

    class Meta:
        app_label = "notifications"
        db_table = "notif_channel_credential"
        unique_together = [("tenant_id", "channel", "provider_code")]
        ordering = ["channel", "provider_code", "id"]

    def __str__(self) -> str:
        return f"ChannelCred({self.channel}:{self.provider_code} [active={self.is_active}])"
