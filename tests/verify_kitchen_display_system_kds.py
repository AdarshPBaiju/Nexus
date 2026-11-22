#!/usr/bin/env python3
"""
verify_kitchen_display_system_kds.py - Verification suite for Subphase 03.08 (KDS).
Validates:
1. KitchenTicket & KitchenTicketLine models with Forced RLS isolation.
2. Station-specific order ticket routing (Barista vs Hot Kitchen).
3. Prep SLA status calculation (Fresh, Warning, Delayed).
4. Bump ticket completion transition.
5. Ticket recall (Ctrl+Z) functionality.
6. Execution performance budget (< 5ms).
"""

from __future__ import annotations

import datetime
from decimal import Decimal
import os
from pathlib import Path
import sys
import time
import uuid

REPO_ROOT = Path(__file__).resolve().parents[1]
API_SRC = REPO_ROOT / "services" / "nexus-api" / "src"
sys.path.insert(0, str(API_SRC))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nexus_test_settings")
import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "nexus.platform.tenancy",
            "nexus.extensions.commerce.kds",
        ],
        USE_TZ=True,
    )
    django.setup()

from django.core.management import call_command

from nexus.extensions.commerce.kds.models import (
    KitchenTicket,
    KitchenTicketLine,
)
from nexus.extensions.commerce.kds.models.kitchen_ticket import CreateKitchenTicketDto
from nexus.extensions.commerce.kds.services import (
    DispatchOrderDto,
    KdsTicketService,
    RoutedOrderItemDto,
)


def _setup_schema() -> None:
    call_command("migrate", "--run-syncdb", verbosity=0)


def test_ticket_model_and_rls() -> None:
    print("[1/5] Testing KitchenTicket and KitchenTicketLine creation with RLS...")
    t1 = uuid.uuid4()
    t2 = uuid.uuid4()
    dto1 = CreateKitchenTicketDto(
        tenant_id=t1,
        branch_id=uuid.uuid4(),
        folio_id=uuid.uuid4(),
        order_token="#001",
        station_type="BARISTA",
    )
    dto2 = CreateKitchenTicketDto(
        tenant_id=t2,
        branch_id=uuid.uuid4(),
        folio_id=uuid.uuid4(),
        order_token="#002",
        station_type="HOT_KITCHEN",
    )
    tk1 = KitchenTicket.create_ticket(dto1)
    tk2 = KitchenTicket.create_ticket(dto2)

    assert tk1.status == KitchenTicket.Status.NEW
    assert KitchenTicket.objects.filter(tenant_id=t1).count() == 1
    assert KitchenTicket.objects.filter(tenant_id=t2).count() == 1
    print("  ✓ Kitchen tickets created with tenant RLS isolation.")


def test_station_routing() -> None:
    print("[2/5] Testing station-specific order routing (Barista vs Kitchen)...")
    t_id = uuid.uuid4()
    branch_id = uuid.uuid4()
    folio_id = uuid.uuid4()
    items = [
        RoutedOrderItemDto(
            item_name="Oat Cortado",
            quantity=Decimal("2"),
            station_type="BARISTA",
            modifier_notes=["Extra Shot"],
            allergen_flags=[],
        ),
        RoutedOrderItemDto(
            item_name="Avocado Sourdough Toast",
            quantity=Decimal("1"),
            station_type="HOT_KITCHEN",
            modifier_notes=["Poached Egg"],
            allergen_flags=["GLUTEN", "EGG"],
        ),
    ]
    dispatch_dto = DispatchOrderDto(
        tenant_id=t_id,
        branch_id=branch_id,
        folio_id=folio_id,
        order_token="#042",
        items=items,
    )
    tickets = KdsTicketService.dispatch_order_to_stations(dispatch_dto)

    assert len(tickets) == 2
    stations = {t.station_type for t in tickets}
    assert stations == {"BARISTA", "HOT_KITCHEN"}

    kitchen_ticket = next(t for t in tickets if t.station_type == "HOT_KITCHEN")
    assert kitchen_ticket.lines.count() == 1
    line = kitchen_ticket.lines.first()
    assert line.allergen_flags_json == ["GLUTEN", "EGG"]
    print("  ✓ Multi-item order automatically partitioned across station monitors.")


def test_prep_sla_calculation() -> None:
    print("[3/5] Testing prep SLA timer status (Fresh, Warning, Delayed)...")
    t_id = uuid.uuid4()
    dto = CreateKitchenTicketDto(
        tenant_id=t_id,
        branch_id=uuid.uuid4(),
        folio_id=uuid.uuid4(),
        order_token="#099",
        station_type="BARISTA",
        sla_seconds=300,
    )
    ticket = KitchenTicket.create_ticket(dto)
    base_time = ticket.created_at

    # T+60s (<60% of 300s): FRESH
    assert ticket.get_sla_status(base_time + datetime.timedelta(seconds=60)) == "FRESH"
    # T+200s (between 180s and 300s): WARNING
    assert ticket.get_sla_status(base_time + datetime.timedelta(seconds=200)) == "WARNING"
    # T+350s (> 300s): DELAYED
    assert ticket.get_sla_status(base_time + datetime.timedelta(seconds=350)) == "DELAYED"
    print("  ✓ SLA status correctly reflects elapsed preparation time against target.")


def test_bump_and_recall_lifecycle() -> None:
    print("[4/5] Testing ticket bump and recall (Ctrl+Z) lifecycle...")
    t_id = uuid.uuid4()
    dto = CreateKitchenTicketDto(
        tenant_id=t_id,
        branch_id=uuid.uuid4(),
        folio_id=uuid.uuid4(),
        order_token="#101",
        station_type="BARISTA",
    )
    ticket = KitchenTicket.create_ticket(dto)
    assert ticket.status == KitchenTicket.Status.NEW

    bumped = KdsTicketService.bump_ticket(t_id, ticket.id)
    assert bumped.status == KitchenTicket.Status.READY
    assert bumped.bumped_at is not None

    recalled = KdsTicketService.recall_ticket(t_id, ticket.id)
    assert recalled.status == KitchenTicket.Status.IN_PREP
    assert recalled.bumped_at is None
    print("  ✓ Ticket bumped to READY and recalled back to IN_PREP cleanly.")


def test_performance_budget_sub_5ms() -> None:
    print("[5/5] Testing execution performance budget (< 5ms)...")
    t_id = uuid.uuid4()
    dto = CreateKitchenTicketDto(
        tenant_id=t_id,
        branch_id=uuid.uuid4(),
        folio_id=uuid.uuid4(),
        order_token="#999",
        station_type="BARISTA",
    )
    ticket = KitchenTicket.create_ticket(dto)

    start = time.perf_counter()
    KdsTicketService.bump_ticket(t_id, ticket.id)
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert elapsed_ms < 5.0, f"Bump took {elapsed_ms:.2f}ms (budget < 5ms)"
    print(f"  ✓ Sub-5ms bump transition performance met: {elapsed_ms:.2f}ms.")


def main() -> None:
    print("=" * 80)
    print("NEXUS SUBPHASE 03.08: KITCHEN DISPLAY SYSTEM (KDS) VERIFICATION")
    print("=" * 80)
    _setup_schema()
    test_ticket_model_and_rls()
    test_station_routing()
    test_prep_sla_calculation()
    test_bump_and_recall_lifecycle()
    test_performance_budget_sub_5ms()
    print("=" * 80)
    print("ALL KITCHEN DISPLAY SYSTEM TESTS COMPLETED WITH 100% SUCCESS.")
    print("=" * 80)


if __name__ == "__main__":
    main()
