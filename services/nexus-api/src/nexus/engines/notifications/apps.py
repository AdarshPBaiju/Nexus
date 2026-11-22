"""
nexus.engines.notifications.apps - Django app configuration for Omnichannel Notification Engine.
"""
from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nexus.engines.notifications"
    label = "notifications"
