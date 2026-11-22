"""
nexus.extensions.commerce.cafe_qsr.models.menu_item - Menu item domain model.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Self

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


@dataclass(frozen=True)
class CreateMenuItemDto:
    """Parameter DTO for creating a menu item."""

    tenant_id: uuid.UUID
    category_id: uuid.UUID
    sku_code: str
    name: str
    base_price: Decimal
    currency: str = "USD"
    tax_category_code: str = "STANDARD_FOOD"
    tax_rate_percent: Decimal = Decimal("5.00")
    preparation_station: str = "BARISTA"
    image_url: str = ""
    sort_order: int = 0


class MenuItem(TenantScopedModel):
    """
    Sellable menu product item with pricing, preparation routing and tax metadata.
    """

    class PreparationStation(models.TextChoices):
        BARISTA = "BARISTA", _("Barista Coffee Counter")
        HOT_KITCHEN = "HOT_KITCHEN", _("Hot Line Kitchen")
        BAKERY = "BAKERY", _("Bakery / Pastry Oven")
        DESSERT = "DESSERT", _("Cold Dessert Station")
        COLD_BAR = "COLD_BAR", _("Juice & Smoothie Bar")

    category = models.ForeignKey(
        "nexus_cafe_qsr_commerce.MenuCategory",
        on_delete=models.PROTECT,
        related_name="items",
        help_text=_("Parent menu category classification."),
    )
    sku_code = models.CharField(
        max_length=64,
        db_index=True,
        help_text=_("Unique item stock keeping unit code."),
    )
    name = models.CharField(
        max_length=150,
        help_text=_("Display name of menu item."),
    )
    base_price = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        help_text=_("Base selling price before modifiers and taxes."),
    )
    currency = models.CharField(
        max_length=3,
        default="USD",
        help_text=_("ISO 4217 currency code."),
    )
    tax_category_code = models.CharField(
        max_length=32,
        default="STANDARD_FOOD",
        help_text=_("Tax jurisdiction rate category code."),
    )
    tax_rate_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("5.00"),
        help_text=_("Statutory tax rate percentage (e.g. 5.00 for 5%, 18.00 for 18%)."),
    )
    preparation_station = models.CharField(
        max_length=32,
        choices=PreparationStation.choices,
        default=PreparationStation.BARISTA,
        db_index=True,
        help_text=_("Kitchen Display System routing destination."),
    )
    image_url = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text=_("CDN asset URL for POS visual card thumbnail."),
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_("Availability flag for item in counter POS catalog."),
    )
    sort_order = models.IntegerField(
        default=0,
        db_index=True,
        help_text=_("Sort priority within parent category."),
    )

    class Meta:
        db_table = "cafe_menu_item"
        ordering = ["category", "sort_order", "name"]
        indexes = [
            models.Index(fields=["tenant_id", "category_id", "is_active"]),
            models.Index(fields=["tenant_id", "preparation_station", "is_active"]),
        ]
        unique_together = ("tenant_id", "sku_code")

    @classmethod
    def create_item(cls, dto: CreateMenuItemDto) -> Self:
        return cls.objects.create(
            tenant_id=dto.tenant_id,
            category_id=dto.category_id,
            sku_code=dto.sku_code,
            name=dto.name,
            base_price=dto.base_price,
            currency=dto.currency,
            tax_category_code=dto.tax_category_code,
            tax_rate_percent=dto.tax_rate_percent,
            preparation_station=dto.preparation_station,
            image_url=dto.image_url,
            is_active=True,
            sort_order=dto.sort_order,
        )

    def calculate_statutory_tax(self, net_price: Decimal | None = None) -> Decimal:
        price = self.base_price if net_price is None else net_price
        multiplier = self.tax_rate_percent / Decimal("100.00")
        return (price * multiplier).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def __str__(self) -> str:
        return f"MenuItem({self.sku_code}: {self.name}, {self.base_price} {self.currency})"
