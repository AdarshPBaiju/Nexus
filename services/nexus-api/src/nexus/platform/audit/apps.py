"""
nexus.platform.audit.apps - Audit application configuration.
"""

from django.apps import AppConfig


class AuditConfig(AppConfig):
    name = "nexus.platform.audit"
    label = "audit"
    verbose_name = "Enterprise Forensic Audit Engine"
