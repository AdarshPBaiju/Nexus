"""
nexus.platform.i18n.models.entity_translation - Granular Entity Field Translation Model.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class EntityTranslation(TenantScopedModel):
    """
    Granular translation entry for a specific field of an entity instance.
    """

    class Status(models.TextChoices):
        HUMAN_VERIFIED = "HUMAN_VERIFIED", _("Human Verified")
        MACHINE_TRANSLATED = "MACHINE_TRANSLATED", _("Machine Translated (Pending Review)")
        NEEDS_REVIEW = "NEEDS_REVIEW", _("Needs Review")

    entity_type = models.CharField(
        max_length=64,
        db_index=True,
        help_text=_("Canonical entity name (e.g. MenuItem, PhysicalZone, MenuCategory)."),
    )
    entity_id = models.UUIDField(
        db_index=True,
        help_text=_("UUID of the target entity record."),
    )
    field_name = models.CharField(
        max_length=64,
        db_index=True,
        help_text=_("Name of the translatable field (e.g. name, description)."),
    )
    locale_code = models.CharField(
        max_length=16,
        db_index=True,
        help_text=_("Target BCP 47 locale code (e.g. ar-AE, hi-IN, fr-FR)."),
    )
    translated_value = models.TextField(
        help_text=_("Translated text content."),
    )
    status = models.CharField(
        max_length=24,
        choices=Status.choices,
        default=Status.MACHINE_TRANSLATED,
        db_index=True,
        help_text=_("Verification lifecycle status."),
    )

    class Meta:
        app_label = "i18n"
        db_table = "i18n_entity_translation"
        unique_together = [("tenant_id", "entity_type", "entity_id", "field_name", "locale_code")]
        ordering = ["entity_type", "entity_id", "locale_code", "id"]

    def __str__(self) -> str:
        return f"EntityTranslation({self.entity_type}:{self.entity_id} [{self.locale_code}] = {self.translated_value[:20]})"
