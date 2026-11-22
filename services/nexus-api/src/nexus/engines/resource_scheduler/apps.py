"""
nexus.engines.resource_scheduler.apps - Django app configuration for Resource Scheduler Engine.
"""
from django.apps import AppConfig


class ResourceSchedulerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nexus.engines.resource_scheduler"
    label = "resource_scheduler"
