"""
nexus.platform.i18n.models.glossary - Protected Brand & Legal Glossary Term Model.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class GlossaryTerm(TenantScopedModel):
    """
    Brand names, trademarks, and legal phrases locked from automated machine translation.
    """

    term = models.CharField(
        max_length=128,
        db_index=True,
        help_text=_("Exact source term or phrase to protect."),
    )
    locale_code = models.CharField(
        max_length=16,
        db_index=True,
        help_text=_("Target BCP 47 locale code (or '*' for all locales)."),
    )
    required_translation = models.CharField(
        max_length=256,
        help_text=_("Mandatory target translation or verbatim phrase to enforce."),
    )
    is_forbidden = models.BooleanField(
        default=False,
        help_text=_("Whether translation of this term into target locale is strictly forbidden."),
    )

    class Meta:
        app_label = "i18n"
        db_table = "i18n_glossary_term"
        unique_together = [("tenant_id", "term", "locale_code")]
        ordering = ["term", "locale_code", "id"]

    def __str__(self) -> str:
        return f"GlossaryTerm({self.term} -> {self.required_translation} [{self.locale_code}])"
