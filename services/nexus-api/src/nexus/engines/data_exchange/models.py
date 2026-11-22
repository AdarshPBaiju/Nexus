"""
nexus.engines.data_exchange.models - Data mapping profile models.
"""

from __future__ import annotations

from django.db import models

from nexus.libs.models import TenantScopedModel


class DataMappingProfile(TenantScopedModel):
    """
    Persisted dynamic schema mapping profile for transforming external datasets.
    """

    name = models.CharField(max_length=128)
    source_format = models.CharField(max_length=32, default="CSV")
    target_entity = models.CharField(max_length=64, db_index=True)
    field_mappings = models.JSONField(default=dict)
    ast_rules = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "dx_data_mapping_profile"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant_id", "target_entity"]),
        ]
