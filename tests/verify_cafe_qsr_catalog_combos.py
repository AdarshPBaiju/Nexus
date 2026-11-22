#!/usr/bin/env python3
"""
verify_cafe_qsr_catalog_combos.py - Verification suite for Subphase 03.02.
Validates:
1. MenuCategory and MenuItem creation with tenant isolation and station routing.
2. MenuModifierGroup, MenuModifierOption, and MenuItemModifierAssignment.
3. Proportional combo tax splitting with statutory multi-rate items.
4. Sequential daily pickup token generation (#001-#999) with branch and date reset.
5. Execution performance budget (< 15ms).
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
            "nexus.engines.currency_fx",
            "nexus.engines.accounting",
            "nexus.engines.taxation",
            "nexus.extensions.commerce.cafe_qsr",
        ],
        USE_TZ=True,
    )
    django.setup()

from django.core.management import call_command

from nexus.extensions.commerce.cafe_qsr.models import (
    ComboRule,
    DailyPickupToken,
    MenuCategory,
    MenuItem,
    MenuItemModifierAssignment,
    MenuModifierGroup,
    MenuModifierOption,
)
from nexus.extensions.commerce.cafe_qsr.models.menu_item import CreateMenuItemDto
from nexus.extensions.commerce.cafe_qsr.services import (
    ComboItemInputDto,
    ComboTaxEngine,
    PickupTokenService,
)


def _setup_schema() -> None:
    call_command("migrate", "--run-syncdb", verbosity=0)


def _create_category_and_item(
    tenant_id: uuid.UUID,
    cat_slug: str,
    sku: str,
    price: Decimal,
) -> tuple[MenuCategory, MenuItem]:
    category = MenuCategory.create_category(
        tenant_id=tenant_id,
        name="Espresso Bar",
        slug=cat_slug,
        sort_order=1,
    )
    dto = CreateMenuItemDto(
        tenant_id=tenant_id,
        category_id=category.id,
        sku_code=sku,
        name="Flat White",
        base_price=price,
        currency="USD",
        tax_rate_percent=Decimal("5.00"),
        preparation_station="BARISTA",
    )
    item = MenuItem.create_item(dto)
    return category, item


def test_category_and_item_isolation() -> None:
    print("[1/5] Testing MenuCategory and MenuItem creation with tenant isolation...")
    t1 = uuid.uuid4()
    t2 = uuid.uuid4()
    cat1, item1 = _create_category_and_item(t1, "cat-t1", "SKU-FW-01", Decimal("4.50"))
    cat2, item2 = _create_category_and_item(t2, "cat-t2", "SKU-FW-02", Decimal("5.00"))

    assert cat1.is_available() is True
    assert item1.preparation_station == MenuItem.PreparationStation.BARISTA
    assert MenuItem.objects.filter(tenant_id=t1).count() == 1
    assert MenuItem.objects.filter(tenant_id=t2).count() == 1
    tax = item1.calculate_statutory_tax()
    assert tax == Decimal("0.23")  # 5% of 4.50 = 0.225 -> 0.23
    print("  ✓ Category and item created with station routing and tax calculation.")


def test_nested_modifiers_and_assignments() -> None:
    print("[2/5] Testing nested modifier groups and option assignments...")
    t_id = uuid.uuid4()
    _, item = _create_category_and_item(t_id, "cat-mod", "SKU-MOD-01", Decimal("4.00"))

    group = MenuModifierGroup.create_group(
        tenant_id=t_id,
        name="Milk Choice",
        min_selection=1,
        max_selection=1,
    )
    assert group.is_required is True
    assert group.validate_selection_count(1) is True
    assert group.validate_selection_count(0) is False

    opt_oat = MenuModifierOption.create_option(
        tenant_id=t_id,
        group_id=group.id,
        name="Oat Milk",
        price_delta=Decimal("0.75"),
    )
    assignment = MenuItemModifierAssignment.assign_group_to_item(
        tenant_id=t_id,
        item_id=item.id,
        modifier_group_id=group.id,
        sort_order=1,
    )
    assert assignment.modifier_group_id == group.id
    assert opt_oat.price_delta == Decimal("0.75")
    print("  ✓ Modifier groups, options, and item assignments verified.")


def test_proportional_combo_tax_splits() -> None:
    print("[3/5] Testing proportional combo tax split calculation...")
    items = [
        ComboItemInputDto(
            item_id="BEV-01",
            name="Cold Brew Coffee",
            base_price=Decimal("4.00"),
            tax_rate_percent=Decimal("18.00"),
        ),
        ComboItemInputDto(
            item_id="BAK-01",
            name="Almond Croissant",
            base_price=Decimal("6.00"),
            tax_rate_percent=Decimal("5.00"),
        ),
    ]
    bundle_price = Decimal("8.00")
    result = ComboTaxEngine.calculate_proportional_tax_split(bundle_price, items)

    assert result.total_base_price == Decimal("10.00")
    assert result.total_discount == Decimal("2.00")
    assert result.bundle_price == Decimal("8.00")

    # Item 1: 4.00 / 10.00 * 2.00 = 0.80 disc -> net 3.20. Tax 18% of 3.20 = 0.58
    b1 = result.items[0]
    assert b1.allocated_discount == Decimal("0.80")
    assert b1.net_price == Decimal("3.20")
    assert b1.tax_amount == Decimal("0.58")

    # Item 2: 6.00 / 10.00 * 2.00 = 1.20 disc -> net 4.80. Tax 5% of 4.80 = 0.24
    b2 = result.items[1]
    assert b2.allocated_discount == Decimal("1.20")
    assert b2.net_price == Decimal("4.80")
    assert b2.tax_amount == Decimal("0.24")

    assert result.total_tax == Decimal("0.82")
    assert result.total_charge == Decimal("8.82")
    print("  ✓ Proportional discounts and multi-rate taxes balanced with exact cents.")


def test_daily_pickup_token_generation() -> None:
    print("[4/5] Testing sequential daily pickup token generator (#001–#999)...")
    t_id = uuid.uuid4()
    branch_a = uuid.uuid4()
    branch_b = uuid.uuid4()
    day1 = datetime.date(2026, 11, 22)
    day2 = datetime.date(2026, 11, 23)

    tok1 = PickupTokenService.issue_pickup_token(t_id, branch_a, day1)
    tok2 = PickupTokenService.issue_pickup_token(t_id, branch_a, day1)
    tok3 = PickupTokenService.issue_pickup_token(t_id, branch_a, day1)
    assert tok1 == "#001"
    assert tok2 == "#002"
    assert tok3 == "#003"

    # Branch B should start at #001 independently
    tok_b1 = PickupTokenService.issue_pickup_token(t_id, branch_b, day1)
    assert tok_b1 == "#001"

    # Next business day resets to #001
    tok_next_day = PickupTokenService.issue_pickup_token(t_id, branch_a, day2)
    assert tok_next_day == "#001"
    print("  ✓ Sequential daily tokens (#001..#999) and branch/day isolation verified.")


def test_performance_budget_sub_15ms() -> None:
    print("[5/5] Testing execution performance budget (< 15ms)...")
    t_id = uuid.uuid4()
    branch_id = uuid.uuid4()
    today = datetime.date(2026, 11, 22)

    start = time.perf_counter()
    items = [
        ComboItemInputDto(
            item_id=f"ITEM-{i}",
            name=f"Menu Item {i}",
            base_price=Decimal("5.00"),
            tax_rate_percent=Decimal("5.00"),
        )
        for i in range(5)
    ]
    ComboTaxEngine.calculate_proportional_tax_split(Decimal("20.00"), items)
    token = PickupTokenService.issue_pickup_token(t_id, branch_id, today)
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert token != ""
    assert elapsed_ms < 15.0, f"Execution took {elapsed_ms:.2f}ms (budget < 15ms)"
    print(f"  ✓ Sub-15ms performance budget met: {elapsed_ms:.2f}ms.")


def main() -> None:
    print("=" * 80)
    print("NEXUS SUBPHASE 03.02: CAFÉ QSR CATALOG, MODIFIERS & COMBOS VERIFICATION")
    print("=" * 80)
    _setup_schema()
    test_category_and_item_isolation()
    test_nested_modifiers_and_assignments()
    test_proportional_combo_tax_splits()
    test_daily_pickup_token_generation()
    test_performance_budget_sub_15ms()
    print("=" * 80)
    print("ALL CAFÉ QSR CATALOG & COMBO TESTS COMPLETED WITH 100% SUCCESS.")
    print("=" * 80)


if __name__ == "__main__":
    main()
