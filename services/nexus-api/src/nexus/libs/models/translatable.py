"""
nexus.libs.models.translatable - Model Mixin for Multilingual Entity Fields.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class TranslatableFieldsMixin(models.Model):
    """
    Mixin providing declarative multilingual translation support with GIN-indexed localized_cache.
    """

    TRANSLATABLE_FIELDS: tuple[str, ...] = ("name", "description")

    source_locale = models.CharField(
        max_length=16,
        default="en-US",
        help_text=_("Source BCP 47 locale code of the initial entity record."),
    )
    localized_cache = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Denormalized JSON cache mapping {field_name: {locale: value}}."),
    )

    class Meta:
        abstract = True

    def get_localized(self, field_name: str, locale: str | None = None) -> str:
        """
        Retrieves localized text with automatic fallback:
        requested locale -> source_locale -> raw model attribute -> empty string.
        """
        field_cache = self.localized_cache.get(field_name, {})
        target = locale or self.source_locale

        # 1. Exact locale match
        if field_cache.get(target):
            return str(field_cache[target])

        # 2. Source locale fallback
        if field_cache.get(self.source_locale):
            return str(field_cache[self.source_locale])

        # 3. Model attribute direct fallback
        raw_val = getattr(self, field_name, "")
        return str(raw_val) if raw_val is not None else ""

    def set_localized(self, field_name: str, locale: str, value: str) -> None:
        """Sets a localized string in the denormalized localized_cache dictionary."""
        if not isinstance(self.localized_cache, dict):
            self.localized_cache = {}
        if field_name not in self.localized_cache:
            self.localized_cache[field_name] = {}
        self.localized_cache[field_name][locale] = value
