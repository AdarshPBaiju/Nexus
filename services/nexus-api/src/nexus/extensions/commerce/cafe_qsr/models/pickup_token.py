"""
nexus.extensions.commerce.cafe_qsr.models.pickup_token - Daily sequential pickup token counter.
"""

from __future__ import annotations

import datetime
import uuid
from typing import Self

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class DailyPickupToken(TenantScopedModel):
    """
    Tracks daily sequential 3-digit order pickup tokens (#001-#999) per branch business day.
    """

    branch_id = models.UUIDField(
        db_index=True,
        help_text=_("Branch or venue location issuing order tokens."),
    )
    business_date = models.DateField(
        db_index=True,
        help_text=_("Business operating date for sequence reset boundary."),
    )
    last_token_number = models.PositiveIntegerField(
        default=0,
        help_text=_("Last assigned sequential token number (1 to 999)."),
    )

    class Meta:
        db_table = "cafe_daily_pickup_token"
        indexes = [
            models.Index(fields=["tenant_id", "branch_id", "business_date"]),
        ]
        unique_together = ("tenant_id", "branch_id", "business_date")

    @classmethod
    def get_or_create_counter(
        cls,
        tenant_id: uuid.UUID,
        branch_id: uuid.UUID,
        business_date: datetime.date,
    ) -> Self:
        counter, _ = cls.objects.get_or_create(
            tenant_id=tenant_id,
            branch_id=branch_id,
            business_date=business_date,
            defaults={"last_token_number": 0},
        )
        return counter

    @property
    def formatted_token(self) -> str:
        return f"#{self.last_token_number:03d}"

    def __str__(self) -> str:
        return f"DailyPickupToken(branch={self.branch_id}, date={self.business_date}, current={self.formatted_token})"
