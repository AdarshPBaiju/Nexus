"""
nexus.platform.config.models.simulation_run - Config Pre-Publish Simulation Run model.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.ids import new_uuid7
from nexus.platform.config.models.revision import DynamicConfigRevision


class ConfigSimulationRun(models.Model):
    """
    Forecasting dry-run report asserting safety before publishing configuration changes.
    """

    class ResultStatus(models.TextChoices):
        PASSED = "PASSED", _("Passed Cleanly")
        CONFLICT_DETECTED = "CONFLICT_DETECTED", _("Statutory Lock Conflict")
        VALIDATION_FAILED = "VALIDATION_FAILED", _("Schema Validation Failed")

    id = models.UUIDField(
        primary_key=True,
        default=new_uuid7,
        editable=False,
    )
    revision = models.ForeignKey(
        DynamicConfigRevision,
        on_delete=models.CASCADE,
        related_name="simulations",
        help_text=_("Proposed revision evaluated by this simulation."),
    )
    result_status = models.CharField(
        max_length=32,
        choices=ResultStatus.choices,
        default=ResultStatus.PASSED,
        db_index=True,
    )
    conflicts_json = models.JSONField(
        default=list,
        help_text=_("List of detected parent lock or statutory guardrail violations."),
    )
    impact_forecast_json = models.JSONField(
        default=dict,
        help_text=_("Estimated open folios, stations, and tax changes affected."),
    )
    executed_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        app_label = "dynamic_config"
        db_table = "config_simulation_run"
        ordering = ["-executed_at", "id"]

    @property
    def is_safe_to_publish(self) -> bool:
        """Only PASSED simulations may be published to live workstations."""
        return self.result_status == self.ResultStatus.PASSED

    def __str__(self) -> str:
        return f"SimulationRun({self.id}, result={self.result_status})"
