"""
nexus.extensions.commerce.kds.services.kds_service - Kitchen ticket service and routing engine.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from decimal import Decimal

from django.db import transaction

from nexus.extensions.commerce.kds.models.kitchen_ticket import (
    CreateKitchenTicketDto,
    KitchenTicket,
)
from nexus.extensions.commerce.kds.models.kitchen_ticket_line import (
    CreateTicketLineDto,
    KitchenTicketLine,
)


@dataclass(frozen=True)
class RoutedOrderItemDto:
    """Item to be routed to station KDS monitors."""

    item_name: str
    quantity: Decimal
    station_type: str
    modifier_notes: list[str] = field(default_factory=list)
    allergen_flags: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DispatchOrderDto:
    """Order routing parameter object for kitchen station dispatch."""

    tenant_id: uuid.UUID
    branch_id: uuid.UUID
    folio_id: uuid.UUID
    order_token: str
    items: list[RoutedOrderItemDto]


class KdsTicketService:
    """
    Coordinates station-level kitchen ticket dispatch, bump transitions, and recalls.
    """

    @classmethod
    def dispatch_order_to_stations(cls, dto: DispatchOrderDto) -> list[KitchenTicket]:
        # Group items by station
        by_station: dict[str, list[RoutedOrderItemDto]] = {}
        for item in dto.items:
            by_station.setdefault(item.station_type, []).append(item)

        created_tickets: list[KitchenTicket] = []
        with transaction.atomic():
            for station, station_items in by_station.items():
                ticket_dto = CreateKitchenTicketDto(
                    tenant_id=dto.tenant_id,
                    branch_id=dto.branch_id,
                    folio_id=dto.folio_id,
                    order_token=dto.order_token,
                    station_type=station,
                )
                ticket = KitchenTicket.create_ticket(ticket_dto)
                for it in station_items:
                    line_dto = CreateTicketLineDto(
                        tenant_id=dto.tenant_id,
                        ticket_id=ticket.id,
                        item_name=it.item_name,
                        quantity=it.quantity,
                        modifier_notes=it.modifier_notes,
                        allergen_flags=it.allergen_flags,
                    )
                    KitchenTicketLine.create_line(line_dto)
                created_tickets.append(ticket)

        return created_tickets

    @classmethod
    def bump_ticket(cls, tenant_id: uuid.UUID, ticket_id: uuid.UUID) -> KitchenTicket:
        with transaction.atomic():
            ticket = KitchenTicket.objects.select_for_update().get(
                tenant_id=tenant_id,
                id=ticket_id,
            )
            ticket.mark_bumped()
            for line in ticket.lines.filter(status=KitchenTicketLine.LineStatus.PENDING):
                line.mark_completed()
            return ticket

    @classmethod
    def recall_ticket(cls, tenant_id: uuid.UUID, ticket_id: uuid.UUID) -> KitchenTicket:
        with transaction.atomic():
            ticket = KitchenTicket.objects.select_for_update().get(
                tenant_id=tenant_id,
                id=ticket_id,
            )
            ticket.recall()
            return ticket
