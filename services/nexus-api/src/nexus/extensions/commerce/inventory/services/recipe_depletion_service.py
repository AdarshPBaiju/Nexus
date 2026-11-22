"""
nexus.extensions.commerce.inventory.services.recipe_depletion_service - Auto-depletion engine.
"""

from __future__ import annotations

import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from decimal import Decimal

from django.db import transaction

from nexus.extensions.commerce.inventory.models.inventory_item import InventoryItem
from nexus.extensions.commerce.inventory.models.inventory_movement import (
    InventoryMovementEvent,
)
from nexus.extensions.commerce.inventory.models.modifier_adjustment import (
    ModifierRecipeAdjustment,
)
from nexus.extensions.commerce.inventory.models.recipe_bom import RecipeBOM


@dataclass(frozen=True)
class ItemDepletionRequestDto:
    """Ordered item with customization modifiers for recipe depletion."""

    menu_item_id: uuid.UUID
    quantity: Decimal
    modifier_option_ids: list[uuid.UUID] = field(default_factory=list)


@dataclass(frozen=True)
class DepletionBatchCmd:
    """Batch command payload for depleting stock across ordered items."""

    tenant_id: uuid.UUID
    reference_id: str
    items: list[ItemDepletionRequestDto]
    movement_type: str = "POS_DEPLETION"


@dataclass(frozen=True)
class DepletionItemResultDto:
    """Summary of depleted ingredient quantity and remaining balance."""

    ingredient_sku: str
    quantity_depleted: Decimal
    balance_remaining: Decimal


class RecipeDepletionService:
    """
    Executes atomic recipe BOM ingredient depletion with modifier adjustments.
    """

    @classmethod
    def deplete_recipe_bom(cls, cmd: DepletionBatchCmd) -> list[DepletionItemResultDto]:
        required_map = cls._calculate_requirements(cmd.items)
        if not required_map:
            return []

        with transaction.atomic():
            # Canonical lock ordering: ORDER BY id ASC
            items_locked = (
                InventoryItem.objects.select_for_update()
                .filter(tenant_id=cmd.tenant_id, id__in=required_map.keys())
                .order_by("id")
            )
            return cls._execute_depletion(cmd, items_locked, required_map)

    @classmethod
    def _calculate_requirements(
        cls,
        items: list[ItemDepletionRequestDto],
    ) -> dict[uuid.UUID, Decimal]:
        requirements: dict[uuid.UUID, Decimal] = defaultdict(lambda: Decimal("0.0000"))
        for item in items:
            bom = RecipeBOM.objects.filter(menu_item_id=item.menu_item_id, is_active=True).first()
            if not bom:
                continue
            for line in bom.lines.all():
                requirements[line.ingredient_id] += line.quantity * item.quantity
            cls._apply_modifier_adjustments(item, requirements)
        return requirements

    @classmethod
    def _apply_modifier_adjustments(
        cls,
        item: ItemDepletionRequestDto,
        requirements: dict[uuid.UUID, Decimal],
    ) -> None:
        for mod_id in item.modifier_option_ids:
            adjustments = ModifierRecipeAdjustment.objects.filter(modifier_option_id=mod_id)
            for adj in adjustments:
                if adj.is_substitution and adj.substituted_ingredient_id:
                    requirements[adj.substituted_ingredient_id] -= (
                        adj.quantity_delta * item.quantity
                    )
                requirements[adj.ingredient_id] += adj.quantity_delta * item.quantity

    @classmethod
    def _execute_depletion(
        cls,
        cmd: DepletionBatchCmd,
        items_locked,
        required_map: dict[uuid.UUID, Decimal],
    ) -> list[DepletionItemResultDto]:
        results: list[DepletionItemResultDto] = []
        for ing in items_locked:
            qty_needed = required_map.get(ing.id, Decimal("0.0000"))
            if ing.current_stock_qty < qty_needed:
                raise ValueError(
                    f"Insufficient stock for {ing.sku_code}: available {ing.current_stock_qty}, required {qty_needed}"
                )
            ing.current_stock_qty -= qty_needed
            ing.save(update_fields=["current_stock_qty", "updated_at"])
            InventoryMovementEvent.objects.create(
                tenant_id=cmd.tenant_id,
                ingredient=ing,
                reference_id=cmd.reference_id,
                movement_type=cmd.movement_type,
                quantity_delta=-qty_needed,
                balance_after=ing.current_stock_qty,
            )
            results.append(
                DepletionItemResultDto(
                    ingredient_sku=ing.sku_code,
                    quantity_depleted=qty_needed,
                    balance_remaining=ing.current_stock_qty,
                )
            )
        return results
