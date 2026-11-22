"""
nexus.platform.iam.models.oauth_client - Third-party OAuth 2.0 application model.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.ids import new_uuid7


class OAuthClientApp(models.Model):
    """
    Registered third-party OAuth 2.0 application client.
    """

    id = models.UUIDField(
        primary_key=True,
        default=new_uuid7,
        editable=False,
    )
    client_id = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text=_("Public OAuth 2.0 client identifier."),
    )
    client_secret_hash = models.CharField(
        max_length=128,
        help_text=_("Hashed client secret for confidential clients."),
    )
    name = models.CharField(
        max_length=128,
        help_text=_("Commercial application name (e.g. Zomato Menu Bridge)."),
    )
    redirect_uris = models.JSONField(
        default=list,
        help_text=_("List of allowed OAuth redirect URI endpoints."),
    )
    allowed_scopes = models.JSONField(
        default=list,
        help_text=_("List of scopes this client application is authorized to request."),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Designates whether this OAuth client is active."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        app_label = "iam"
        db_table = "iam_oauth_client_app"
        ordering = ["-created_at", "id"]

    def is_scope_allowed(self, scope: str) -> bool:
        """Verify requested scope is permitted for this application."""
        return scope in self.allowed_scopes

    def __str__(self) -> str:
        return f"OAuthClientApp({self.name}, client_id={self.client_id})"
