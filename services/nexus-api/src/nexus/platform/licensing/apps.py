"""
nexus.platform.licensing.apps - Licensing and Plugin Registry AppConfig.
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LicensingConfig(AppConfig):
    name = "nexus.platform.licensing"
    label = "licensing"
    verbose_name = _("Platform Licensing & Plugin Architecture")
