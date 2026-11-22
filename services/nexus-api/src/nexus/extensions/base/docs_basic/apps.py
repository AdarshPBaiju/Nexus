"""
nexus.extensions.base.docs_basic.apps - Django app configuration for Fiscal Documents Engine.
"""

from __future__ import annotations

from django.apps import AppConfig


class DocsBasicConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nexus.extensions.base.docs_basic"
    label = "nexus_docs_basic"
    verbose_name = "Nexus Fiscal Documents & Receipt Engine (DOCS)"
