"""
nexus.engines.templates.apps - Django app configuration for Universal Template Engine.
"""
from django.apps import AppConfig


class TemplatesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nexus.engines.templates"
    label = "templates"
