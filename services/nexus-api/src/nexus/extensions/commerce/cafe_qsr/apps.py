"""
nexus.extensions.commerce.cafe_qsr.apps - Django app configuration for Café QSR Commerce.
"""

from __future__ import annotations

from django.apps import AppConfig


class CafeQsrCommerceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nexus.extensions.commerce.cafe_qsr"
    label = "nexus_cafe_qsr_commerce"
    verbose_name = "Nexus Café & Quick-Service Restaurant Commerce (CAFE_QSR)"
