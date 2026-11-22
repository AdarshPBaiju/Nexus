"""
nexus.extensions.base.hr_basic.apps - Django app configuration for Default Basic HR.
"""

from __future__ import annotations

from django.apps import AppConfig


class HrBasicConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nexus.extensions.base.hr_basic"
    label = "nexus_hr_basic"
    verbose_name = "Nexus Default Basic HR (HR_CORE)"
