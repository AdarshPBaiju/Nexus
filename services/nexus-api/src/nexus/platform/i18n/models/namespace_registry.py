"""
nexus.platform.i18n.models.namespace_registry - Registered namespace isolation model.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.ids import new_uuid7


class NamespaceRegistry(models.Model):
    """
    Modular translation namespace isolating copy domains across packages.
    """

    id = models.UUIDField(
        primary_key=True,
        default=new_uuid7,
        editable=False,
    )
    slug = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text=_("Namespace slug (e.g. core, pos, kds, gaming, fin_core, auth)."),
    )
    description = models.CharField(
        max_length=255,
        help_text=_("Functional scope of the translation namespace."),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Designates whether this namespace is active in bundles."),
    )

    class Meta:
        app_label = "i18n"
        db_table = "i18n_namespace_registry"
        ordering = ["slug"]

    def __str__(self) -> str:
        return f"Namespace({self.slug})"
