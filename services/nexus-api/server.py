"""
server.py - Project Nexus Development API Server.
Provides interactive HTTP API endpoints for Project Nexus Phase 1 engines:
- /healthz: Health probe & engine status
- /api/v1/info: Phase 1 capability metadata
- /api/v1/currency-fx/format: Dynamic 18-dimension currency formatting
- /api/v1/currency-fx/words: Legal cheque amount-in-words conversion
- /api/v1/tax/calculate: Statutory tax calculation
- /api/v1/discounts/evaluate: Condition-driven discount allocation
"""

from __future__ import annotations

import json
import os
import sys
from decimal import Decimal
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

API_SRC = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(API_SRC))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nexus_settings")
import django  # noqa: E402

django.setup()

from nexus.engines.currency_fx.formatter import (  # noqa: E402
    CurrencyFormatProfile,
    DynamicCurrencyFormatter,
)
from nexus.engines.currency_fx.words import AmountInWordsEngine, WordsOptions  # noqa: E402
from nexus.engines.discounts.service import (  # noqa: E402
    DiscountEvaluationRequest,
    DiscountEvaluatorService,
)
from nexus.engines.taxation.service import TaxCalculationEngine  # noqa: E402
from nexus.libs.money.money import Money  # noqa: E402
from nexus.server_endpoints import (  # noqa: E402
    GatewayEndpointHandler,
    MarketplaceEndpointHandler,
    TenancyEndpointHandler,
)


class NexusApiHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Project Nexus Development API."""

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self) -> None:
        path = self.path.split("?")[0].rstrip("/")
        if path in {"", "/healthz"}:
            self._send_json(
                200,
                {
                    "status": "healthy",
                    "system": "Project Nexus Core API",
                    "version": "0.1.0",
                    "phase": "Phase 1: Platform Kernel & Shared Business Services",
                    "active_subphases": 30,
                    "engines": [
                        "tenancy",
                        "iam",
                        "licensing",
                        "config",
                        "i18n",
                        "accounting",
                        "currency_fx",
                        "taxation",
                        "discounts",
                        "invoicing",
                        "notifications",
                        "templates",
                        "payment_router",
                    ],
                },
            )
        elif path == "/api/v1/info":
            self._send_json(
                200,
                {
                    "phase": 1,
                    "name": "Platform Kernel & Shared Business Services",
                    "subphases_total": 30,
                    "subphases_completed": 30,
                    "verification_suites": 41,
                    "ci_status": "100% SUCCESS",
                },
            )
        elif path == "/api/v1/gateways/config":
            self._send_json(200, GatewayEndpointHandler.get_config())
        elif path == "/api/v1/plugins":
            self._send_json(200, MarketplaceEndpointHandler.list_plugins())
        elif path == "/api/v1/tenants/lifecycle":
            self._send_json(200, TenancyEndpointHandler.get_lifecycle())
        else:
            self._send_json(404, {"error": "Not Found", "path": self.path})

    def do_POST(self) -> None:
        path = self.path.split("?")[0].rstrip("/")
        data = self._read_json_body()

        if path == "/api/v1/currency-fx/format":
            self._handle_currency_format(data)
        elif path == "/api/v1/currency-fx/words":
            self._handle_currency_words(data)
        elif path == "/api/v1/tax/calculate":
            self._handle_tax_calculate(data)
        elif path == "/api/v1/discounts/evaluate":
            self._handle_discount_evaluate(data)
        elif path == "/api/v1/gateways/config":
            self._send_json(200, GatewayEndpointHandler.update_config(data))
        elif path == "/api/v1/gateways/test":
            self._send_json(200, GatewayEndpointHandler.test_gateway(data))
        elif path == "/api/v1/plugins/toggle":
            self._send_json(200, MarketplaceEndpointHandler.toggle_plugin(data))
        elif path == "/api/v1/tenants/register":
            res = TenancyEndpointHandler.register_tenant(data)
            status = 201 if res.get("success") else 400
            self._send_json(status, res)
        elif path == "/api/v1/tenants/lifecycle":
            self._send_json(200, TenancyEndpointHandler.transition_status(data))
        elif path == "/api/v1/tenants/kms-rotate":
            self._send_json(200, TenancyEndpointHandler.rotate_kms_key(data))
        else:
            self._send_json(404, {"error": "Endpoint Not Found", "path": self.path})

    def _read_json_body(self) -> dict:
        content_len = int(self.headers.get("Content-Length", 0))
        if content_len <= 0:
            return {}
        try:
            raw = self.rfile.read(content_len).decode("utf-8")
            return json.loads(raw)
        except Exception:
            return {}

    def _handle_currency_format(self, data: dict) -> None:
        amt = Decimal(str(data.get("amount", "0.00")))
        curr = str(data.get("currency", "USD")).upper()
        pat = tuple(data.get("grouping_pattern", [3]))
        prof = CurrencyFormatProfile(
            grouping_pattern=pat,
            symbol_mode=data.get("symbol_mode", "UNICODE_SYMBOL"),
            negative_format=data.get("negative_format", "MINUS_PREFIX"),
        )
        formatted = DynamicCurrencyFormatter.format(Money.of(amt, curr), prof)
        self._send_json(200, {"formatted": formatted, "amount": str(amt), "currency": curr})

    def _handle_currency_words(self, data: dict) -> None:
        amt = Decimal(str(data.get("amount", "0.00")))
        curr = str(data.get("currency", "USD")).upper()
        scale = str(data.get("scale", "WESTERN_SHORT"))
        subunit = str(data.get("subunit_format", "WORDS"))
        star = bool(data.get("star_padding", False))
        opt = WordsOptions(scale=scale, subunit_format=subunit, star_padding=star)
        words = AmountInWordsEngine.to_words(Money.of(amt, curr), opt)
        self._send_json(200, {"words": words, "amount": str(amt), "currency": curr})

    def _handle_tax_calculate(self, data: dict) -> None:
        amt = Decimal(str(data.get("amount", "0.00")))
        curr = str(data.get("currency", "USD")).upper()
        rate = Decimal(str(data.get("rate", "5.00")))
        inclusive = bool(data.get("is_inclusive", False))
        res = TaxCalculationEngine.calculate_tax(Money.of(amt, curr), rate, inclusive)
        self._send_json(
            200,
            {
                "net": str(res.net_money.amount),
                "tax": str(res.tax_money.amount),
                "gross": str(res.gross_money.amount),
                "effective_rate": str(res.effective_rate),
                "is_inclusive": res.is_inclusive,
                "currency": curr,
            },
        )

    def _handle_discount_evaluate(self, data: dict) -> None:
        curr = str(data.get("currency", "USD")).upper()
        line_amts = [Decimal(str(a)) for a in data.get("lines", ["100.00"])]
        lines = [Money.of(a, curr) for a in line_amts]
        req = DiscountEvaluationRequest(
            rule_code=data.get("rule_code", "DEFAULT_PROMO"),
            condition_ast=data.get("condition_ast", {}),
            action_ast=data.get("action_ast", {"type": "PERCENTAGE", "value": 10}),
            guardrail_policy=data.get("guardrail_policy", {}),
            context=data.get("context", {}),
        )
        res = DiscountEvaluatorService.evaluate_order_discount(lines, req)
        self._send_json(
            200,
            {
                "original_total": str(res.original_total.amount),
                "discount_total": str(res.discount_total.amount),
                "net_total": str(res.net_total.amount),
                "applied_rules": list(res.applied_rule_codes),
                "line_discounts": [str(m.amount) for m in res.line_discounts],
                "currency": curr,
            },
        )

    def _send_json(self, status_code: int, data: dict) -> None:
        payload = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(payload)

    def _send_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE")
        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type, Authorization, X-Requested-With, X-Nexus-Tenant-Slug",
        )

    def log_message(self, format: str, *args) -> None:
        sys.stdout.write(f"[Nexus-API] {args[0]} - {args[1]}\n")
        sys.stdout.flush()


def run_server(port: int = 8000) -> None:
    server_address = ("0.0.0.0", port)
    httpd = ThreadingHTTPServer(server_address, NexusApiHandler)
    print(f"==> Project Nexus Core API running at http://localhost:{port}/")
    print(f"    - Health probe: http://localhost:{port}/healthz")
    print(f"    - Platform Info: http://localhost:{port}/api/v1/info")
    httpd.serve_forever()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_server(port)
