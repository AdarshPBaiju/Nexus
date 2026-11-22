"""
nexus.extensions.commerce.pos.services.offline_sync_service - Server offline outbox drain service.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from django.db import transaction

from nexus.extensions.commerce.pos.models.processed_event_inbox import (
    ProcessedEventInbox,
)
from nexus.extensions.commerce.pos.service import (
    CounterCheckoutRequestDto,
    PosCheckoutService,
)


@dataclass(frozen=True)
class OfflineOrderEventDto:
    """Envelope wrapping a client-side offline sales order for synchronization."""

    event_id: uuid.UUID
    workstation_id: str
    checkout_dto: CounterCheckoutRequestDto


@dataclass(frozen=True)
class SyncBatchResultDto:
    """Outcome report of batch offline sync operation."""

    total_received: int
    processed_count: int
    deduplicated_count: int
    processed_event_ids: tuple[uuid.UUID, ...]
    deduplicated_event_ids: tuple[uuid.UUID, ...]


class OfflineSyncService:
    """
    Drains queued offline sales events with idempotent deduplication and balancing GL posting.
    """

    @classmethod
    def drain_offline_batch(
        cls,
        tenant_id: uuid.UUID,
        workstation_id: str,
        events: list[OfflineOrderEventDto],
    ) -> SyncBatchResultDto:
        processed_ids: list[uuid.UUID] = []
        deduplicated_ids: list[uuid.UUID] = []

        for evt in events:
            if cls._is_already_processed(tenant_id, evt.event_id):
                deduplicated_ids.append(evt.event_id)
                continue

            order = cls._process_single_event(tenant_id, evt)
            ProcessedEventInbox.record_processed_event(
                tenant_id=tenant_id,
                event_id=evt.event_id,
                workstation_id=workstation_id,
                order_id=order.id,
            )
            processed_ids.append(evt.event_id)

        return SyncBatchResultDto(
            total_received=len(events),
            processed_count=len(processed_ids),
            deduplicated_count=len(deduplicated_ids),
            processed_event_ids=tuple(processed_ids),
            deduplicated_event_ids=tuple(deduplicated_ids),
        )

    @classmethod
    def _is_already_processed(cls, tenant_id: uuid.UUID, event_id: uuid.UUID) -> bool:
        return ProcessedEventInbox.objects.filter(
            tenant_id=tenant_id,
            event_id=event_id,
        ).exists()

    @classmethod
    def _process_single_event(cls, tenant_id: uuid.UUID, evt: OfflineOrderEventDto):
        with transaction.atomic():
            return PosCheckoutService.process_counter_checkout(evt.checkout_dto)
