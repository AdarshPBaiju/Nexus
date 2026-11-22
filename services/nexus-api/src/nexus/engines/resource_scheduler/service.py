"""
nexus.engines.resource_scheduler.service - Non-Overlapping Conflict Detection & Scheduler Service.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import transaction

from nexus.engines.resource_scheduler.models.allocation import ResourceAllocation
from nexus.engines.resource_scheduler.models.resource import VenueResource


class ResourceConflictError(ValidationError):
    """Raised when an allocation request overlaps with an active booking."""


@dataclass(frozen=True)
class TimeSlot:
    """Time boundaries and optional linked commerce folio for a reservation."""

    start_time: datetime
    end_time: datetime
    folio_id: uuid.UUID | None = None


class ResourceSchedulerService:
    """
    Coordinates atomic booking and time conflict resolution for VenueResources.
    """

    ACTIVE_STATUSES = [
        ResourceAllocation.AllocationStatus.CONFIRMED,
        ResourceAllocation.AllocationStatus.ACTIVE,
        ResourceAllocation.AllocationStatus.HOLD_LOCKED,
    ]

    @classmethod
    def assert_no_overlap(
        cls,
        resource_id: uuid.UUID,
        start_time: datetime,
        end_time: datetime,
        exclude_allocation_id: uuid.UUID | None = None,
    ) -> None:
        """Enforces that requested time range has zero overlap with existing active bookings."""
        if start_time >= end_time:
            raise ValidationError("start_time must be strictly earlier than end_time.")

        query = ResourceAllocation.objects.filter(
            resource_id=resource_id,
            status__in=cls.ACTIVE_STATUSES,
            start_time__lt=end_time,
            end_time__gt=start_time,
        )
        if exclude_allocation_id:
            query = query.exclude(id=exclude_allocation_id)

        if query.exists():
            conflict = query.first()
            raise ResourceConflictError(
                f"Booking conflict on resource {resource_id}: existing allocation {conflict.id} "
                f"covers {conflict.start_time} to {conflict.end_time}."
            )

    @classmethod
    @transaction.atomic
    def allocate_resource(
        cls,
        tenant_id: uuid.UUID,
        resource: VenueResource,
        slot: TimeSlot,
    ) -> ResourceAllocation:
        """
        Atomically acquires resource lock, checks for time overlap, and creates confirmed allocation.
        """
        VenueResource.objects.select_for_update().get(id=resource.id)
        cls.assert_no_overlap(resource.id, slot.start_time, slot.end_time)

        return ResourceAllocation.objects.create(
            tenant_id=tenant_id,
            resource=resource,
            start_time=slot.start_time,
            end_time=slot.end_time,
            folio_id=slot.folio_id,
            status=ResourceAllocation.AllocationStatus.CONFIRMED,
        )

