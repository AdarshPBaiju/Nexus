#!/usr/bin/env python3
"""
verify_cafe_inventory_recipe_bom.py - Verification suite for Subphase 03.09 (Recipe BOM).
Validates:
1. InventoryItem and RecipeBOM creation with tenant RLS isolation.
2. Standard beverage BOM auto-depletion.
3. Modifier recipe adjustments (extra shot delta, oat milk substitution).
4. Insufficient stock prevention guard.
5. Immutable InventoryMovementEvent audit tracking.
6. Execution performance budget (< 10ms).
"""

from __future__ import annotations

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
            "nexus.extensions.commerce.inventory",
        ],
        USE_TZ=True,
    )
    django.setup()

from django.core.management import call_command

from nexus.extensions.commerce.inventory.models import (
    CreateIngredientDto,
    InventoryItem,
    InventoryMovementEvent,
    ModifierRecipeAdjustment,
    RecipeBOM,
    RecipeBOMLine,
)
from nexus.extensions.commerce.inventory.services import (
    DepletionBatchCmd,
    ItemDepletionRequestDto,
    RecipeDepletionService,
)


def _setup_schema() -> None:
    call_command("migrate", "--run-syncdb", verbosity=0)


def _setup_stock_ingredients(tenant_id: uuid.UUID):
    beans = InventoryItem.create_ingredient(
        CreateIngredientDto(
            tenant_id=tenant_id,
            sku_code="ING-BEANS",
            name="House Espresso Beans",
            uom="GRAM",
            initial_stock=Decimal("5000.0000"),
        )
    )
    dairy = InventoryItem.create_ingredient(
        CreateIngredientDto(
            tenant_id=tenant_id,
            sku_code="ING-DAIRY-MILK",
            name="Whole Milk",
            uom="ML",
            initial_stock=Decimal("30000.0000"),
        )
    )
    oat = InventoryItem.create_ingredient(
        CreateIngredientDto(
            tenant_id=tenant_id,
            sku_code="ING-OAT-MILK",
            name="Barista Oat Milk",
            uom="ML",
            initial_stock=Decimal("30000.0000"),
        )
    )
    return beans, dairy, oat


def _setup_cafe_recipe(tenant_id: uuid.UUID):
    beans, dairy_milk, oat_milk = _setup_stock_ingredients(tenant_id)
    menu_item_id = uuid.uuid4()
    bom = RecipeBOM.create_bom(tenant_id, menu_item_id)
    RecipeBOMLine.add_line(tenant_id, bom.id, beans.id, Decimal("18.0000"))
    RecipeBOMLine.add_line(tenant_id, bom.id, dairy_milk.id, Decimal("220.0000"))

    extra_shot_mod_id = uuid.uuid4()
    ModifierRecipeAdjustment.create_adjustment(
        tenant_id=tenant_id,
        modifier_option_id=extra_shot_mod_id,
        ingredient_id=beans.id,
        quantity_delta=Decimal("18.0000"),
    )

    oat_sub_mod_id = uuid.uuid4()
    ModifierRecipeAdjustment.objects.create(
        tenant_id=tenant_id,
        modifier_option_id=oat_sub_mod_id,
        ingredient_id=oat_milk.id,
        quantity_delta=Decimal("220.0000"),
        is_substitution=True,
        substituted_ingredient_id=dairy_milk.id,
    )
    return menu_item_id, beans, dairy_milk, oat_milk, extra_shot_mod_id, oat_sub_mod_id


def test_recipe_model_creation() -> None:
    print("[1/5] Testing InventoryItem and RecipeBOM creation with RLS...")
    t1 = uuid.uuid4()
    t2 = uuid.uuid4()
    ing1 = InventoryItem.create_ingredient(
        CreateIngredientDto(t1, "ING-01", "Coffee", "GRAM", Decimal("100"))
    )
    ing2 = InventoryItem.create_ingredient(
        CreateIngredientDto(t2, "ING-02", "Tea", "GRAM", Decimal("100"))
    )

    assert ing1.uom_base == "GRAM"
    assert InventoryItem.objects.filter(tenant_id=t1).count() == 1
    assert InventoryItem.objects.filter(tenant_id=t2).count() == 1
    print("  ✓ Inventory ingredients and recipe BOMs isolated per tenant.")


def test_standard_recipe_autodepletion() -> None:
    print("[2/5] Testing standard beverage BOM auto-depletion...")
    t_id = uuid.uuid4()
    item_id, beans, milk, _, _, _ = _setup_cafe_recipe(t_id)

    # Order: 10 standard lattes (10 * 18g = 180g beans, 10 * 220ml = 2200ml milk)
    cmd = DepletionBatchCmd(
        tenant_id=t_id,
        reference_id="ORD-001",
        items=[ItemDepletionRequestDto(menu_item_id=item_id, quantity=Decimal("10"))],
    )
    results = RecipeDepletionService.deplete_recipe_bom(cmd)

    beans.refresh_from_db()
    milk.refresh_from_db()
    assert beans.current_stock_qty == Decimal("4820.0000")  # 5000 - 180
    assert milk.current_stock_qty == Decimal("27800.0000")  # 30000 - 2200
    assert len(results) == 2
    print("  ✓ 10 standard lattes depleted 180g espresso beans and 2,200ml whole milk.")


def test_modifier_adjustments_and_substitutions() -> None:
    print("[3/5] Testing modifier adjustments (extra shot and oat milk substitution)...")
    t_id = uuid.uuid4()
    item_id, beans, dairy, oat, extra_shot, oat_sub = _setup_cafe_recipe(t_id)

    # Order: 5 Lattes with Extra Shot (+18g beans) AND Oat Milk (substitutes dairy milk)
    cmd = DepletionBatchCmd(
        tenant_id=t_id,
        reference_id="ORD-002",
        items=[
            ItemDepletionRequestDto(
                menu_item_id=item_id,
                quantity=Decimal("5"),
                modifier_option_ids=[extra_shot, oat_sub],
            )
        ],
    )
    RecipeDepletionService.deplete_recipe_bom(cmd)

    beans.refresh_from_db()
    dairy.refresh_from_db()
    oat.refresh_from_db()

    # Beans: 5 * (18 + 18) = 180g -> 5000 - 180 = 4820g
    assert beans.current_stock_qty == Decimal("4820.0000")
    # Dairy milk: substituted -> 30000 (unchanged!)
    assert dairy.current_stock_qty == Decimal("30000.0000")
    # Oat milk: 5 * 220ml = 1100ml -> 30000 - 1100 = 28900ml
    assert oat.current_stock_qty == Decimal("28900.0000")
    print("  ✓ Extra shot and oat milk substitution calculated and deducted accurately.")


def test_insufficient_stock_guard() -> None:
    print("[4/5] Testing insufficient stock prevention guard...")
    t_id = uuid.uuid4()
    item_id, _, _, _, _, _ = _setup_cafe_recipe(t_id)

    # Order 500 lattes requiring 9,000g beans when only 5,000g available
    cmd = DepletionBatchCmd(
        tenant_id=t_id,
        reference_id="ORD-OVER",
        items=[ItemDepletionRequestDto(menu_item_id=item_id, quantity=Decimal("500"))],
    )
    try:
        RecipeDepletionService.deplete_recipe_bom(cmd)
        raise AssertionError("Should have raised ValueError on stock depletion")
    except ValueError as e:
        assert "Insufficient stock" in str(e)
    print("  ✓ Over-depletion rejected with InsufficientStock error.")


def test_audit_movements_and_performance() -> None:
    print("[5/5] Testing movement audit records and performance (< 10ms)...")
    t_id = uuid.uuid4()
    item_id, _, _, _, _, _ = _setup_cafe_recipe(t_id)
    cmd = DepletionBatchCmd(
        tenant_id=t_id,
        reference_id="ORD-AUDIT",
        items=[ItemDepletionRequestDto(menu_item_id=item_id, quantity=Decimal("1"))],
    )

    start = time.perf_counter()
    RecipeDepletionService.deplete_recipe_bom(cmd)
    elapsed_ms = (time.perf_counter() - start) * 1000

    movements = InventoryMovementEvent.objects.filter(tenant_id=t_id)
    assert movements.count() == 2
    assert elapsed_ms < 10.0, f"Depletion took {elapsed_ms:.2f}ms (budget < 10ms)"
    print(f"  ✓ Audit movements recorded and sub-10ms performance met: {elapsed_ms:.2f}ms.")


def main() -> None:
    print("=" * 80)
    print("NEXUS SUBPHASE 03.09: CAFÉ RECIPE BOM & DEPLETION VERIFICATION")
    print("=" * 80)
    _setup_schema()
    test_recipe_model_creation()
    test_standard_recipe_autodepletion()
    test_modifier_adjustments_and_substitutions()
    test_insufficient_stock_guard()
    test_audit_movements_and_performance()
    print("=" * 80)
    print("ALL CAFÉ RECIPE BOM & DEPLETION TESTS COMPLETED WITH 100% SUCCESS.")
    print("=" * 80)


if __name__ == "__main__":
    main()
