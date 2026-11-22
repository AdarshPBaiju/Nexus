"""
nexus.platform.config.models.schema_registry - Config JSON Schema specification model.
"""
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.ids import new_uuid7


class ConfigSchemaRegistry(models.Model):
    """
    JSON Schema Draft 2020-12 specification governing dynamic config keys for a module.
    """

    id = models.UUIDField(
        primary_key=True,
        default=new_uuid7,
        editable=False,
    )
    module_code = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text=_("Module code (e.g. POS, CAFE_QSR, KDS, GAME_CORE)."),
    )
    schema_json = models.JSONField(
        default=dict,
        help_text=_("JSON Schema Draft 2020-12 validation specification."),
    )
    ui_hints_json = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("UI layout hints, field groups, and custom widget mappings."),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Designates whether this config schema is active."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        app_label = "dynamic_config"
        db_table = "config_schema_registry"
        ordering = ["module_code", "id"]

    def __str__(self) -> str:
        return f"ConfigSchema({self.module_code})"
