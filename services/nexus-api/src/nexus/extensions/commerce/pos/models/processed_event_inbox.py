"""
nexus.extensions.commerce.pos.models.processed_event_inbox - Server idempotency inbox model.
"""

from __future__ import annotations

import uuid
from typing import Self

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class ProcessedEventInbox(TenantScopedModel):
    """
    Idempotent event receipt log ensuring offline outbox events are never double-posted.
    """

    event_id = models.UUIDField(
        db_index=True,
        help_text=_("Client-side UUIDv7 event identifier from offline outbox envelope."),
    )
    workstation_id = models.CharField(
        max_length=64,
        db_index=True,
        help_text=_("Workstation terminal hardware identifier."),
    )
    event_type = models.CharField(
        max_length=64,
        default="POS_COUNTER_CHECKOUT",
        help_text=_("Type of commercial or operational offline transaction."),
    )
    order_id = models.UUIDField(
        null=True,
        blank=True,
        help_text=_("Created PosOrder primary key upon successful processing."),
    )
    processed_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text=_("Server ingestion timestamp."),
    )

    class Meta:
        db_table = "pos_processed_event_inbox"
        ordering = ["-processed_at"]
        indexes = [
            models.Index(fields=["tenant_id", "workstation_id", "processed_at"]),
        ]
        unique_together = ("tenant_id", "event_id")

    @classmethod
    def record_processed_event(
        cls,
        tenant_id: uuid.UUID,
        event_id: uuid.UUID,
        workstation_id: str,
        order_id: uuid.UUID | None = None,
    ) -> Self:
        return cls.objects.create(
            tenant_id=tenant_id,
            event_id=event_id,
            workstation_id=workstation_id,
            event_type="POS_COUNTER_CHECKOUT",
            order_id=order_id,
            processed_at=timezone.now(),
        )

    def __str__(self) -> str:
        return f"ProcessedEventInbox(event={self.event_id}, ws={self.workstation_id})"
