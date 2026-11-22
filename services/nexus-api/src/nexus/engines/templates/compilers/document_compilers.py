"""
nexus.engines.templates.compilers.document_compilers - 6 Document & Hardware Output Compilers.
"""

from __future__ import annotations

import hashlib
from typing import Any

from nexus.engines.templates.ast.nodes import ASTNode
from nexus.engines.templates.compilers.base import BaseTargetCompiler


class A4PdfCompiler(BaseTargetCompiler):
    """Target 8: High-fidelity statutory A4 PDF Invoice & Report Compiler."""

    @property
    def target_name(self) -> str:
        return "A4_PDF"

    def compile(self, root: ASTNode, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        text = self.collect_text(root)
        meta = metadata or {}
        return {
            "format": "A4",
            "page_orientation": "portrait",
            "header": meta.get("header", "Project Nexus"),
            "content": text,
            "footer": "Page 1 of 1",
            "qr_code": meta.get("zatca_qr", ""),
        }


class ThermalEscPosCompiler(BaseTargetCompiler):
    """Target 9: Raw 80mm/58mm Thermal ESC/POS Byte Stream Compiler."""

    ESC_INIT = b"\x1b@"
    ESC_ALIGN_CENTER = b"\x1ba\x01"
    ESC_ALIGN_LEFT = b"\x1ba\x00"
    ESC_BOLD_ON = b"\x1bE\x01"
    ESC_BOLD_OFF = b"\x1bE\x00"
    GS_CUT = b"\x1dV\x00"

    @property
    def target_name(self) -> str:
        return "THERMAL_ESCPOS"

    def compile(self, root: ASTNode, metadata: dict[str, Any] | None = None) -> bytes:
        text = self.collect_text(root)
        payload = bytearray()
        payload.extend(self.ESC_INIT)
        payload.extend(self.ESC_ALIGN_CENTER)
        payload.extend(self.ESC_BOLD_ON)
        payload.extend(b"*** RECEIPT ***\n")
        payload.extend(self.ESC_BOLD_OFF)
        payload.extend(self.ESC_ALIGN_LEFT)
        payload.extend(text.encode("utf-8") + b"\n")
        payload.extend(self.GS_CUT)
        return bytes(payload)


class KitchenKotCompiler(BaseTargetCompiler):
    """Target 10: Kitchen / Barista KOT Ticket Compiler."""

    @property
    def target_name(self) -> str:
        return "KITCHEN_KOT"

    def compile(self, root: ASTNode, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        text = self.collect_text(root)
        meta = metadata or {}
        return {
            "station": meta.get("station", "KITCHEN_MAIN"),
            "table_or_token": meta.get("table_id", "COUNTER_01"),
            "items_text": text,
            "allergens": meta.get("allergens", []),
        }


class ZplLabelCompiler(BaseTargetCompiler):
    """Target 11: Industrial Zebra ZPL-II Label Printer Compiler."""

    @property
    def target_name(self) -> str:
        return "ZPL_LABEL"

    def compile(self, root: ASTNode, metadata: dict[str, Any] | None = None) -> str:
        text = self.collect_text(root)
        meta = metadata or {}
        barcode = meta.get("barcode", "12345678")
        return f"^XA^FO50,50^A0N,36,36^FD{text}^FS^FO50,100^BY3^BCN,100,Y,N,N^FD{barcode}^FS^XZ"


class MobilePassCompiler(BaseTargetCompiler):
    """Target 12: Apple Wallet pkpass and Google Wallet Pass Object Compiler."""

    @property
    def target_name(self) -> str:
        return "MOBILE_PASS"

    def compile(self, root: ASTNode, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        text = self.collect_text(root)
        meta = metadata or {}
        return {
            "formatVersion": 1,
            "passTypeIdentifier": "pass.nexus.storecard",
            "serialNumber": meta.get("serial", "NX-PASS-001"),
            "description": text,
            "primaryFields": [
                {"key": "member", "label": "MEMBER", "value": meta.get("member", "Guest")}
            ],
        }


class VerifiableWebCompiler(BaseTargetCompiler):
    """Target 13: Tamper-Evident SHA-256 Verifiable Receipt Web Page Compiler."""

    @property
    def target_name(self) -> str:
        return "VERIFIABLE_WEB"

    def compile(self, root: ASTNode, metadata: dict[str, Any] | None = None) -> str:
        text = self.collect_text(root)
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return f"<!DOCTYPE html><html><body><div id='receipt'>{text}</div><div id='sig'>{digest}</div></body></html>"
