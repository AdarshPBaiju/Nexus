"""
nexus.platform.config.apps - Dynamic Config AppConfig.
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ConfigAppConfig(AppConfig):
    name = "nexus.platform.config"
    label = "dynamic_config"
    verbose_name = _("Platform Dynamic Configuration & Provenance")
