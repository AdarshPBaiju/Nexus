"""
nexus.platform.i18n.apps - Django app configuration for multilingual kernel module.
"""
from django.apps import AppConfig


class I18nConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nexus.platform.i18n"
    label = "i18n"
