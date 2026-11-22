"""
nexus.extensions.commerce.pos.apps - Django app configuration for POS Counter Commerce.
"""

from __future__ import annotations

from django.apps import AppConfig


class PosCommerceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nexus.extensions.commerce.pos"
    label = "nexus_pos_commerce"
    verbose_name = "Nexus Point of Sale Commerce (POS_COUNTER)"
