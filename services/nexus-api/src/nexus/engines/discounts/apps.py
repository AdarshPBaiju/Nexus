"""
nexus.engines.discounts.apps - Django AppConfig for Discounts & Promotions engine.
"""

from __future__ import annotations

from django.apps import AppConfig


class DiscountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nexus.engines.discounts"
    label = "discounts"
    verbose_name = "Nexus Discounts & Promotions Engine"
