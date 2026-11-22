"""
nexus.platform.tenancy.apps - Tenancy AppConfig.
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TenancyConfig(AppConfig):
    name = "nexus.platform.tenancy"
    label = "tenancy"
    verbose_name = _("Platform Tenancy & Regional Boundaries")
