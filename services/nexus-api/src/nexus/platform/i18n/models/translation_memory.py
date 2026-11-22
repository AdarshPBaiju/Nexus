"""
nexus.platform.i18n.models.translation_memory - Translation Memory Cache Model.
"""
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class TranslationMemory(TenantScopedModel):
    """
    Fuzzy and exact match cache preventing duplicate billable translation calls.
    """

    source_hash = models.CharField(
        max_length=64,
        db_index=True,
        help_text=_("SHA-256 hexadecimal hash of the trimmed source string."),
    )
    source_text = models.TextField(
        help_text=_("Verbatim source text content."),
    )
    locale_code = models.CharField(
        max_length=16,
        db_index=True,
        help_text=_("Target BCP 47 locale code."),
    )
    translated_text = models.TextField(
        help_text=_("Verified target translation."),
    )
    is_verified = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_("Whether translation has been human approved."),
    )

    class Meta:
        app_label = "i18n"
        db_table = "i18n_translation_memory"
        unique_together = [("tenant_id", "source_hash", "locale_code")]
        ordering = ["source_hash", "locale_code", "id"]

    def __str__(self) -> str:
        return f"TranslationMemory({self.source_text[:20]} -> {self.locale_code})"
