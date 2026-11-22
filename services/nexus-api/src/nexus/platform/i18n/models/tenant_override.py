"""
nexus.platform.i18n.models.tenant_override - Tenant/Brand/Branch translation override model.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel
from nexus.platform.i18n.models.locale_master import LocaleMaster
from nexus.platform.i18n.models.translation_key import TranslationKey


class TenantTranslationOverride(TenantScopedModel):
    """
    Tenant-specific custom copy overrides supporting brand and branch hierarchies.
    Enforces Forced RLS isolation via TenantScopedModel.
    """

    brand_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        help_text=_("Optional commercial brand scoping override."),
    )
    branch_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        help_text=_("Optional physical branch scoping override."),
    )
    key = models.ForeignKey(
        TranslationKey,
        on_delete=models.CASCADE,
        related_name="tenant_overrides",
        help_text=_("Translation key customized by this override."),
    )
    locale = models.ForeignKey(
        LocaleMaster,
        on_delete=models.PROTECT,
        related_name="tenant_overrides",
        help_text=_("Target locale customized by this override."),
    )
    custom_pattern = models.TextField(
        help_text=_("Customized ICU MessageFormat pattern overriding system copy."),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Designates whether this custom override is active."),
    )

    class Meta:
        app_label = "i18n"
        db_table = "i18n_tenant_override"
        indexes = [
            models.Index(fields=["tenant_id", "key", "locale"]),
            models.Index(fields=["tenant_id", "brand_id", "branch_id"]),
        ]

    def __str__(self) -> str:
        return f"Override({self.tenant_id} @ {self.key.key_code} [{self.locale.code}])"
