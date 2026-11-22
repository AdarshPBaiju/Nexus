"""
nexus.engines.invoicing.service.routing_engine - Multi-Printer Split Routing Engine.
"""
from __future__ import annotations

import uuid
from typing import Any

from nexus.engines.invoicing.models.printer import PrinterDevice
from nexus.engines.invoicing.models.routing import PrintRouteRule


class PrintRoutingEngine:
    """
    Evaluates multi-printer split routing rules and dispatches document streams
    simultaneously across cashier receipt, barista KOT, and zebra label printers.
    """

    @classmethod
    def resolve_printer(cls, tenant_id: uuid.UUID, document_type: str) -> PrinterDevice | None:
        """Finds active configured destination printer for the document category."""
        rule = (
            PrintRouteRule.objects.select_related("target_printer")
            .filter(
                tenant_id=tenant_id,
                document_type=document_type,
                is_active=True,
                target_printer__is_active=True,
            )
            .first()
        )
        return rule.target_printer if rule else None

    @classmethod
    def dispatch_multi_printer_job(
        cls,
        tenant_id: uuid.UUID,
        document_payloads: dict[str, Any],
    ) -> dict[str, str]:
        """
        Routes multiple document types to their respective hardware devices.
        Returns map of {document_type: status_message}.
        """
        results: dict[str, str] = {}
        for doc_type, _payload in document_payloads.items():
            printer = cls.resolve_printer(tenant_id, doc_type)
            if not printer:
                results[doc_type] = "NO_ACTIVE_PRINTER_CONFIGURED"
                continue
            # Simulated print dispatch
            results[doc_type] = f"DISPATCHED_TO_{printer.name}_{printer.device_type}"
        return results
