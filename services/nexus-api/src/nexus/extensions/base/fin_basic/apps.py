"""
nexus.extensions.base.fin_basic.apps - Django app configuration for Default Basic Finance.
"""

from __future__ import annotations

from django.apps import AppConfig


class FinBasicConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nexus.extensions.base.fin_basic"
    label = "nexus_fin_basic"
    verbose_name = "Nexus Default Basic Finance (FIN_CORE)"
