"""
nexus.platform.iam.models.oauth_grant - Tenant-scoped OAuth 2.0 consent grant model.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel
from nexus.platform.iam.models.oauth_client import OAuthClientApp


class OAuthConsentGrant(TenantScopedModel):
    """
    Tenant administrator consent granting specific scopes to an OAuthClientApp.
    """

    client_app = models.ForeignKey(
        OAuthClientApp,
        on_delete=models.CASCADE,
        related_name="consent_grants",
        help_text=_("OAuth client receiving granted scopes."),
    )
    granted_scopes = models.JSONField(
        default=list,
        help_text=_("List of scopes granted by the tenant administrator."),
    )
    is_revoked = models.BooleanField(
        default=False,
        help_text=_("Designates whether this tenant grant was administratively revoked."),
    )

    class Meta:
        app_label = "iam"
        db_table = "iam_oauth_consent_grant"
        unique_together = [("tenant_id", "client_app")]
        ordering = ["-created_at", "id"]

    @property
    def is_valid(self) -> bool:
        """Assert grant is active and client app is operational."""
        return not self.is_revoked and self.client_app.is_active

    def has_scope(self, scope: str) -> bool:
        """Check if scope is granted and unrevoked."""
        return self.is_valid and scope in self.granted_scopes

    def __str__(self) -> str:
        return f"OAuthGrant({self.client_app_id} @ {self.tenant_id}, revoked={self.is_revoked})"
