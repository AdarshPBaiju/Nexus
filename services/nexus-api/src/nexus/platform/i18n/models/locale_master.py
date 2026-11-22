"""
nexus.platform.i18n.models.locale_master - Supported BCP 47 locale catalog model.
"""
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.ids import new_uuid7


class LocaleMaster(models.Model):
    """
    Catalog of supported BCP 47 locales with linguistic metadata and text direction.
    """

    class TextDirection(models.TextChoices):
        LTR = "ltr", _("Left-to-Right")
        RTL = "rtl", _("Right-to-Left")

    id = models.UUIDField(
        primary_key=True,
        default=new_uuid7,
        editable=False,
    )
    code = models.CharField(
        max_length=16,
        unique=True,
        db_index=True,
        help_text=_("Standard BCP 47 locale code (e.g. en-US, ar-AE, es-ES)."),
    )
    base_language = models.CharField(
        max_length=8,
        db_index=True,
        help_text=_("ISO 639-1 base language code (e.g. en, ar, es)."),
    )
    native_name = models.CharField(
        max_length=64,
        help_text=_("Endonym name of the language (e.g. English, العربية)."),
    )
    text_direction = models.CharField(
        max_length=4,
        choices=TextDirection.choices,
        default=TextDirection.LTR,
        help_text=_("Reading direction for bidirectional layout engines."),
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_("Designates whether this locale is available for tenants."),
    )
    is_platform_source = models.BooleanField(
        default=False,
        help_text=_("Designates the canonical source locale for all system copy."),
    )

    class Meta:
        app_label = "i18n"
        db_table = "i18n_locale_master"
        ordering = ["code"]

    def __str__(self) -> str:
        return f"Locale({self.code} - {self.native_name} [{self.text_direction}])"
