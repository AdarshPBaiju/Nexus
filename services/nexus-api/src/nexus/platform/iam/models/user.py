"""
nexus.platform.iam.models.user - Global User identity account model.
"""

from __future__ import annotations

import re

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.ids import new_uuid7


class User(models.Model):
    """
    Global user identity. May hold memberships across multiple tenant workspaces.
    """

    id = models.UUIDField(
        primary_key=True,
        default=new_uuid7,
        editable=False,
    )
    email = models.EmailField(
        unique=True,
        db_index=True,
        help_text=_("Primary corporate or identity email address."),
    )
    phone_e164 = models.CharField(
        max_length=20,
        blank=True,
        default="",
        db_index=True,
        help_text=_("E.164 formatted international telephone number."),
    )
    is_mfa_enabled = models.BooleanField(
        default=False,
        help_text=_("Enforces multi-factor TOTP verification during login."),
    )
    totp_secret = models.CharField(
        max_length=128,
        blank=True,
        default="",
        help_text=_("Encrypted TOTP authentication secret."),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Designates whether this global identity account is active."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        app_label = "iam"
        db_table = "iam_user"
        ordering = ["-created_at", "id"]

    def clean(self) -> None:
        super().clean()
        self._validate_phone()

    def _validate_phone(self) -> None:
        if self.phone_e164 and not re.match(r"^\+[1-9]\d{1,14}$", self.phone_e164):
            raise ValidationError(
                {"phone_e164": _("Phone number must follow E.164 international standard.")}
            )

    def __str__(self) -> str:
        return f"User({self.email}, active={self.is_active})"
