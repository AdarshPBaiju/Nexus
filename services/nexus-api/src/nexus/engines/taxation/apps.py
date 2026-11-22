"""
nexus.engines.taxation.apps - Django app configuration for Jurisdiction-Agnostic Tax Engine.
"""

from django.apps import AppConfig


class TaxationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nexus.engines.taxation"
    label = "taxation"
