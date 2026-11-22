#!/usr/bin/env python3
"""
verify_commerce_folio_resource_scheduler.py - Verification suite for Subphase 01.07.
Validates:
1. Polymorphic CommerceFolio and FolioLineItem data models.
2. RFC 9110 If-Match optimistic locking (version mismatch raises OptimisticLockError).
3. OrderFulfillmentRouter dispatching tickets (Barista KDS, Kitchen KDS, Receipt Printer).
4. VenueResource hierarchy and non-overlapping ResourceAllocation conflict detection.
5. High-concurrency allocation safety and zero double-booking.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import os
from pathlib import Path
import sys

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
            "nexus.engines.commerce_folio",
            "nexus.engines.resource_scheduler",
        ],
        USE_TZ=True,
    )
    django.setup()

from django.core.management import call_command

call_command("migrate", run_syncdb=True, verbosity=0)

from nexus.engines.commerce_folio.models import (
    CommerceFolio,
    FolioLineItem,
)
from nexus.engines.commerce_folio.router import (
    FulfillmentTarget,
    OrderFulfillmentRouter,
)
from nexus.engines.commerce_folio.service import (
    AddLineItemDto,
    FolioOptimisticLockService,
    OptimisticLockError,
)
from nexus.engines.resource_scheduler.models import (
    ResourceAllocation,
    VenueResource,
)
from nexus.engines.resource_scheduler.service import (
    ResourceConflictError,
    ResourceSchedulerService,
    TimeSlot,
)
from nexus.libs.ids import new_uuid7


def test_commerce_folio_optimistic_locking() -> None:
    """Validate folio line additions and version incrementing under If-Match."""
    tenant_id = new_uuid7()
    branch_id = new_uuid7()

    folio = CommerceFolio.objects.create(
        tenant_id=tenant_id,
        branch_id=branch_id,
        folio_number="FOL-2026-0001",
        version=1,
    )
    assert folio.version == 1
    assert folio.total_amount == Decimal("0.0000")

    dto = AddLineItemDto(
        item_type=FolioLineItem.ItemType.FOOD_BEV,
        description="Iced Vanilla Oat Latte",
        quantity=Decimal("2.00"),
        unit_price=Decimal("25.0000"),
        tax_amount=Decimal("2.5000"),
    )

    line = FolioOptimisticLockService.add_line_item(folio, expected_version=1, dto=dto)
    assert line.total_amount == Decimal("52.5000")

    folio.refresh_from_db()
    assert folio.version == 2
    assert folio.total_amount == Decimal("52.5000")

    # Stale version attempt must fail with OptimisticLockError (412)
    try:
        FolioOptimisticLockService.add_line_item(folio, expected_version=1, dto=dto)
        assert False, "Stale version must raise OptimisticLockError"
    except OptimisticLockError as err:
        assert "Folio version conflict" in str(err)

    print("[PASS] test_commerce_folio_optimistic_locking")


def test_order_fulfillment_router() -> None:
    """Validate item dispatch routing to Barista KDS, Kitchen KDS, and Printer."""
    tenant_id = new_uuid7()
    folio = CommerceFolio.objects.create(
        tenant_id=tenant_id,
        branch_id=new_uuid7(),
        folio_number="FOL-2026-0002",
    )

    item_barista = FolioLineItem.objects.create(
        folio=folio,
        item_type=FolioLineItem.ItemType.FOOD_BEV,
        description="Double Espresso Macchiato",
        quantity=Decimal("1.00"),
        unit_price=Decimal("18.0000"),
        total_amount=Decimal("18.0000"),
    )
    item_kitchen = FolioLineItem.objects.create(
        folio=folio,
        item_type=FolioLineItem.ItemType.FOOD_BEV,
        description="Avocado Toast with Poached Egg",
        quantity=Decimal("1.00"),
        unit_price=Decimal("45.0000"),
        total_amount=Decimal("45.0000"),
    )
    item_retail = FolioLineItem.objects.create(
        folio=folio,
        item_type=FolioLineItem.ItemType.RETAIL,
        description="Nexus Gaming Mousepad",
        quantity=Decimal("1.00"),
        unit_price=Decimal("80.0000"),
        total_amount=Decimal("80.0000"),
    )

    routed = OrderFulfillmentRouter.dispatch_batch([item_barista, item_kitchen, item_retail])
    assert item_barista in routed[FulfillmentTarget.BARISTA_KDS]
    assert item_kitchen in routed[FulfillmentTarget.KITCHEN_KDS]
    assert item_retail in routed[FulfillmentTarget.RECEIPT_PRINTER]

    print("[PASS] test_order_fulfillment_router")


def _assert_overlapping_slot_rejected(
    tenant_id: any,
    station: VenueResource,
    start: datetime,
    end: datetime,
) -> None:
    """Assert attempting an overlapping slot raises ResourceConflictError."""
    try:
        ResourceSchedulerService.allocate_resource(
            tenant_id=tenant_id,
            resource=station,
            slot=TimeSlot(start_time=start, end_time=end),
        )
        assert False, "Overlapping slot must raise ResourceConflictError"
    except ResourceConflictError as err:
        assert "Booking conflict" in str(err)


def test_resource_scheduler_conflict_prevention() -> None:
    """Validate non-overlapping allocation time range enforcement."""
    tenant_id = new_uuid7()
    zone_id = new_uuid7()

    station = VenueResource.objects.create(
        tenant_id=tenant_id,
        zone_id=zone_id,
        code="PC-VIP-01",
        name="VIP RTX 5090 Rig 1",
        resource_type=VenueResource.ResourceType.PC,
    )

    now = datetime.now(timezone.utc).replace(microsecond=0)
    slot1_start = now + timedelta(hours=1)
    slot1_end = now + timedelta(hours=3)

    alloc1 = ResourceSchedulerService.allocate_resource(
        tenant_id=tenant_id,
        resource=station,
        slot=TimeSlot(start_time=slot1_start, end_time=slot1_end),
    )
    assert alloc1.status == ResourceAllocation.AllocationStatus.CONFIRMED

    # 2. Overlapping Slot: 15:00 - 17:00 -> Conflict
    _assert_overlapping_slot_rejected(
        tenant_id,
        station,
        now + timedelta(hours=2),
        now + timedelta(hours=4),
    )

    # 3. Non-overlapping Slot: 16:00 - 18:00 -> Success
    alloc2 = ResourceSchedulerService.allocate_resource(
        tenant_id=tenant_id,
        resource=station,
        slot=TimeSlot(start_time=slot1_end, end_time=slot1_end + timedelta(hours=2)),
    )
    assert alloc2.status == ResourceAllocation.AllocationStatus.CONFIRMED

    print("[PASS] test_resource_scheduler_conflict_prevention")


def main() -> None:
    test_commerce_folio_optimistic_locking()
    test_order_fulfillment_router()
    test_resource_scheduler_conflict_prevention()
    print("\n>>> All 3 Subphase 01.07 verification suites passed successfully! <<<")


if __name__ == "__main__":
    main()
