"""
nexus.platform.i18n.models.compiled_bundle - Compiled namespace JSON bundle with Weak ETag.
"""
from __future__ import annotations

import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel
from nexus.platform.i18n.models.locale_master import LocaleMaster
from nexus.platform.i18n.models.namespace_registry import NamespaceRegistry


class CompiledBundle(TenantScopedModel):
    """
    Pre-compiled translation bundle served with sub-4ms Weak ETag 304 responses.
    Uses sentinel platform tenant ID for global platform bundles.
    """

    PLATFORM_TENANT_ID = uuid.UUID(int=0)

    namespace = models.ForeignKey(
        NamespaceRegistry,
        on_delete=models.CASCADE,
        related_name="compiled_bundles",
        help_text=_("Namespace of this pre-compiled bundle."),
    )
    locale = models.ForeignKey(
        LocaleMaster,
        on_delete=models.PROTECT,
        related_name="compiled_bundles",
        help_text=_("Target locale of this pre-compiled bundle."),
    )
    bundle_json = models.JSONField(
        default=dict,
        help_text=_("Resolved key-to-pattern dictionary ready for client consumption."),
    )
    etag = models.CharField(
        max_length=64,
        db_index=True,
        help_text=_("Weak ETag: W/\"nx:i18n:{ns}:{locale}:{sha256_prefix}\"."),
    )
    compiled_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        app_label = "i18n"
        db_table = "i18n_compiled_bundle"
        unique_together = [("tenant_id", "namespace", "locale")]
        indexes = [
            models.Index(fields=["tenant_id", "etag"]),
        ]

    def clean(self) -> None:
        if not self.tenant_id:
            self.tenant_id = self.PLATFORM_TENANT_ID
        super().clean()

    def __str__(self) -> str:
        return f"Bundle({self.namespace.slug} : {self.locale.code} [{self.etag}])"
