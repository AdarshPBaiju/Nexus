"""
nexus.platform.i18n.models.translation_entry - Localized translation entry model.
"""
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.ids import new_uuid7
from nexus.platform.i18n.models.locale_master import LocaleMaster
from nexus.platform.i18n.models.translation_key import TranslationKey


class TranslationEntry(models.Model):
    """
    Language-specific translation string mapped to a canonical translation key.
    """

    class TranslationStatus(models.TextChoices):
        MACHINE_TRANSLATED = "MACHINE_TRANSLATED", _("Machine Translated")
        HUMAN_EDITED = "HUMAN_EDITED", _("Human Edited")
        APPROVED = "APPROVED", _("Approved by Language Reviewer")

    id = models.UUIDField(
        primary_key=True,
        default=new_uuid7,
        editable=False,
    )
    key = models.ForeignKey(
        TranslationKey,
        on_delete=models.CASCADE,
        related_name="entries",
        help_text=_("Translation key associated with this localized entry."),
    )
    locale = models.ForeignKey(
        LocaleMaster,
        on_delete=models.PROTECT,
        related_name="translation_entries",
        help_text=_("Target BCP 47 locale."),
    )
    translated_pattern = models.TextField(
        help_text=_("Localized ICU MessageFormat pattern."),
    )
    status = models.CharField(
        max_length=32,
        choices=TranslationStatus.choices,
        default=TranslationStatus.MACHINE_TRANSLATED,
        db_index=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        app_label = "i18n"
        db_table = "i18n_translation_entry"
        unique_together = [("key", "locale")]
        indexes = [
            models.Index(fields=["locale", "status"]),
        ]

    def __str__(self) -> str:
        return f"Entry({self.key.key_code} [{self.locale.code}] - {self.status})"
