"""
nexus.extensions.commerce.kds.models.kitchen_ticket - Kitchen ticket header model.
"""

from __future__ import annotations

import datetime
import uuid
from dataclasses import dataclass
from typing import Self

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


@dataclass(frozen=True)
class CreateKitchenTicketDto:
    """Parameter object for kitchen ticket creation."""

    tenant_id: uuid.UUID
    branch_id: uuid.UUID
    folio_id: uuid.UUID
    order_token: str
    station_type: str = "BARISTA"
    sla_seconds: int = 300


class KitchenTicket(TenantScopedModel):
    """
    Station-routed kitchen order ticket with prep timers and bump bar state.
    """

    class StationType(models.TextChoices):
        BARISTA = "BARISTA", _("Barista Coffee Counter")
        HOT_KITCHEN = "HOT_KITCHEN", _("Hot Food Kitchen")
        BAKERY = "BAKERY", _("Bakery / Pastry Station")
        DESSERT = "DESSERT", _("Dessert & Ice Cream Bar")
        EXPO = "EXPO", _("Expediter / Hand-off Station")

    class Status(models.TextChoices):
        NEW = "NEW", _("New Order Fired")
        IN_PREP = "IN_PREP", _("Preparation Started")
        READY = "READY", _("Ready for Pickup")
        SERVED = "SERVED", _("Fulfilled & Collected")

    branch_id = models.UUIDField(
        db_index=True,
        help_text=_("Branch or venue location."),
    )
    folio_id = models.UUIDField(
        db_index=True,
        help_text=_("Associated commerce folio or order."),
    )
    order_token = models.CharField(
        max_length=16,
        db_index=True,
        help_text=_("3-digit pickup token (e.g. #042)."),
    )
    station_type = models.CharField(
        max_length=32,
        choices=StationType.choices,
        default=StationType.BARISTA,
        db_index=True,
        help_text=_("Target preparation display station."),
    )
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.NEW,
        db_index=True,
        help_text=_("Ticket lifecycle progression status."),
    )
    sla_seconds = models.PositiveIntegerField(
        default=300,
        help_text=_("Target preparation SLA duration in seconds."),
    )
    bumped_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Timestamp when station completed ticket."),
    )

    class Meta:
        db_table = "kds_kitchen_ticket"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["tenant_id", "station_type", "status"]),
            models.Index(fields=["tenant_id", "branch_id", "status"]),
        ]

    @classmethod
    def create_ticket(cls, dto: CreateKitchenTicketDto) -> Self:
        return cls.objects.create(
            tenant_id=dto.tenant_id,
            branch_id=dto.branch_id,
            folio_id=dto.folio_id,
            order_token=dto.order_token,
            station_type=dto.station_type,
            status=cls.Status.NEW,
            sla_seconds=dto.sla_seconds,
        )

    def mark_bumped(self) -> None:
        self.status = self.Status.READY
        self.bumped_at = timezone.now()
        self.save(update_fields=["status", "bumped_at", "updated_at"])

    def recall(self) -> None:
        self.status = self.Status.IN_PREP
        self.bumped_at = None
        self.save(update_fields=["status", "bumped_at", "updated_at"])

    def get_sla_status(self, now: datetime.datetime | None = None) -> str:
        current_time = now or timezone.now()
        elapsed = (current_time - self.created_at).total_seconds()
        if elapsed < (self.sla_seconds * 0.6):
            return "FRESH"
        if elapsed <= self.sla_seconds:
            return "WARNING"
        return "DELAYED"

    def __str__(self) -> str:
        return (
            f"KitchenTicket({self.order_token}, station={self.station_type}, status={self.status})"
        )
