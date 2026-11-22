"""
nexus.platform.i18n.models.translation_key - Canonical translation key definition model.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.ids import new_uuid7
from nexus.platform.i18n.models.namespace_registry import NamespaceRegistry


class TranslationKey(models.Model):
    """
    Canonical system copy identifier with ICU MessageFormat 2.0 template pattern.
    """

    id = models.UUIDField(
        primary_key=True,
        default=new_uuid7,
        editable=False,
    )
    namespace = models.ForeignKey(
        NamespaceRegistry,
        on_delete=models.CASCADE,
        related_name="keys",
        help_text=_("Namespace owning this translation key."),
    )
    key_code = models.CharField(
        max_length=128,
        db_index=True,
        help_text=_("Dot-separated key code (e.g. orders.summary.grand_total)."),
    )
    default_icu_pattern = models.TextField(
        help_text=_("Default ICU MessageFormat 2.0 source pattern in en-US."),
    )
    parameter_schema_json = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("JSON Schema defining expected interpolation parameters."),
    )
    description_context = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Linguistic context and notes provided to translators."),
    )
    max_length_hint = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text=_("Maximum character length guidance for UI containers."),
    )

    class Meta:
        app_label = "i18n"
        db_table = "i18n_translation_key"
        unique_together = [("namespace", "key_code")]
        ordering = ["namespace", "key_code"]

    def __str__(self) -> str:
        return f"Key({self.namespace.slug}:{self.key_code})"
