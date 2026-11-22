"""
nexus.engines.invoicing.models.printer - Registered Printer Hardware Device Model.
"""
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class PrinterDevice(TenantScopedModel):
    """
    Physical or network printer endpoint registered for counter or kitchen routing.
    """

    class DeviceType(models.TextChoices):
        THERMAL_ESCPOS = "THERMAL_ESCPOS", _("Thermal ESC/POS Receipt Printer (58/80mm)")
        LASER_PDF = "LASER_PDF", _("Laser Sheet-Fed A4 PDF Printer")
        DOT_MATRIX = "DOT_MATRIX", _("Continuous Dot-Matrix ESC/P Tractor Feed")
        LABEL_ZPL = "LABEL_ZPL", _("Zebra ZPL-II Label Printer")

    class ConnectionType(models.TextChoices):
        NETWORK_TCP = "NETWORK_TCP", _("Raw Network TCP Port (e.g. 9100)")
        USB_DIRECT = "USB_DIRECT", _("Direct USB Bulk Interface")
        SERIAL = "SERIAL", _("RS-232 Serial Port")
        OS_SPOOLER = "OS_SPOOLER", _("Native OS Spooler (WinSpool / CUPS)")

    name = models.CharField(
        max_length=128,
        help_text=_("Human-readable printer name (e.g. Counter Thermal, Barista KOT)."),
    )
    device_type = models.CharField(
        max_length=32,
        choices=DeviceType.choices,
        default=DeviceType.THERMAL_ESCPOS,
        help_text=_("Hardware printer architecture category."),
    )
    connection_type = models.CharField(
        max_length=32,
        choices=ConnectionType.choices,
        default=ConnectionType.NETWORK_TCP,
        help_text=_("Underlying transport connection mode."),
    )
    endpoint = models.CharField(
        max_length=256,
        help_text=_("Address endpoint (IP:port, COM3, USB ID, or Queue Name)."),
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_("Operational availability flag."),
    )

    class Meta:
        app_label = "invoicing"
        db_table = "inv_printer_device"
        ordering = ["name", "id"]

    def __str__(self) -> str:
        return f"Printer({self.name} [{self.device_type} via {self.connection_type}])"
