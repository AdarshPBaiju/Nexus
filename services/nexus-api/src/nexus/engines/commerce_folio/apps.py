"""
nexus.engines.commerce_folio.apps - Django app configuration for Commerce Folio Engine.
"""

from django.apps import AppConfig


class CommerceFolioConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nexus.engines.commerce_folio"
    label = "commerce_folio"
