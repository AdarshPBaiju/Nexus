"""
nexus.engines.currency_fx.apps - Django app configuration for Multi-Currency FX Engine.
"""
from django.apps import AppConfig


class CurrencyFxConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nexus.engines.currency_fx"
    label = "currency_fx"
