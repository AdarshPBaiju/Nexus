"""
nexus.extensions.commerce.inventory.apps - Django app configuration for Inventory.
"""

from __future__ import annotations

from django.apps import AppConfig


class InventoryCommerceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nexus.extensions.commerce.inventory"
    label = "nexus_inventory_commerce"
    verbose_name = "Nexus Café Inventory & Recipe BOM (INVENTORY)"
