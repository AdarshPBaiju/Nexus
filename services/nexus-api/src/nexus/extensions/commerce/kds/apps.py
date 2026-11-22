"""
nexus.extensions.commerce.kds.apps - Django app configuration for KDS.
"""

from __future__ import annotations

from django.apps import AppConfig


class KdsCommerceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nexus.extensions.commerce.kds"
    label = "nexus_kds_commerce"
    verbose_name = "Nexus Kitchen Display System (KDS)"
