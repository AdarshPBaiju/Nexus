"""
nexus.engines.invoicing.apps - Django app configuration for Universal Invoicing & Spooler Engine.
"""

from django.apps import AppConfig


class InvoicingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nexus.engines.invoicing"
    label = "invoicing"
