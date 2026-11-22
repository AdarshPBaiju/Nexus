"""
nexus.extensions.commerce.cafe_qsr.services.pickup_token_service - Daily pickup token generator.
"""

from __future__ import annotations

import datetime
import uuid

from django.db import transaction

from nexus.extensions.commerce.cafe_qsr.models.pickup_token import DailyPickupToken


class PickupTokenService:
    """
    Issues sequential 3-digit pickup tokens (#001-#999) with daily branch rollover.
    """

    MAX_TOKEN_NUMBER = 999

    @classmethod
    def issue_pickup_token(
        cls,
        tenant_id: uuid.UUID,
        branch_id: uuid.UUID,
        business_date: datetime.date,
    ) -> str:
        with transaction.atomic():
            counter, _ = DailyPickupToken.objects.select_for_update().get_or_create(
                tenant_id=tenant_id,
                branch_id=branch_id,
                business_date=business_date,
                defaults={"last_token_number": 0},
            )
            next_num = (counter.last_token_number % cls.MAX_TOKEN_NUMBER) + 1
            counter.last_token_number = next_num
            counter.save(update_fields=["last_token_number", "updated_at"])
            return f"#{next_num:03d}"
