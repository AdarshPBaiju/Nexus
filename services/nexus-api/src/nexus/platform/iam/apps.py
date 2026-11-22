"""
nexus.platform.iam.apps - IAM AppConfig.
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class IamConfig(AppConfig):
    name = "nexus.platform.iam"
    label = "iam"
    verbose_name = _("Platform Identity & Access Management")
