"""
nexus.engines.accounting.apps - Django app configuration for General Ledger & Bookkeeping Engine.
"""

from django.apps import AppConfig


class AccountingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nexus.engines.accounting"
    label = "accounting"
