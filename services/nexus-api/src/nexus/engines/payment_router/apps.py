"""
nexus.engines.payment_router.apps - Django app configuration for Multi-Rail Payment Router.
"""

from django.apps import AppConfig


class PaymentRouterConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nexus.engines.payment_router"
    label = "payment_router"
