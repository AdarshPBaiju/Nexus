"""
nexus.platform.authorization.apps - Django app configuration for Multi-Dimensional Authorization module.
"""
from django.apps import AppConfig


class AuthorizationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nexus.platform.authorization"
    label = "authorization"
