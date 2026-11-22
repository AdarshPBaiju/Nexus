"""
nexus.extensions.commerce.inventory.services - Inventory services barrel export.
"""

from __future__ import annotations

from nexus.extensions.commerce.inventory.services.recipe_depletion_service import (
    DepletionBatchCmd,
    DepletionItemResultDto,
    ItemDepletionRequestDto,
    RecipeDepletionService,
)

__all__ = [
    "DepletionBatchCmd",
    "DepletionItemResultDto",
    "ItemDepletionRequestDto",
    "RecipeDepletionService",
]
