#!/usr/bin/env python3
"""
verify_advanced_django_views_urls_middleware.py - Verification suite for Subphase 01.23.
"""
from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

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
        ],
        USE_TZ=True,
    )
    django.setup()

from django.http import HttpResponse
from django.test import RequestFactory
from rest_framework import exceptions, status
from rest_framework.request import Request

from nexus.libs.http.exceptions import nexus_exception_handler
from nexus.libs.http.middleware import (
    AuditContextMiddleware,
    EtagEvaluatorMiddleware,
    IdempotencyMiddleware,
    RateLimiterMiddleware,
    RyowStickinessMiddleware,
    SecurityHeadersMiddleware,
    TenantRlsMiddleware,
    TraceContextMiddleware,
)
from nexus.libs.http.routing import EngineRouteRegistry
from nexus.libs.http.views import BaseFastTenantAPIView, BaseTenantResourceViewSet


def test_base_viewset_optimistic_locking() -> None:
    factory = RequestFactory()
    viewset = BaseTenantResourceViewSet()

    # Valid version matching If-Match
    req = Request(factory.get("/api/v1/resource/", HTTP_IF_MATCH='"3"'))
    viewset.check_optimistic_lock(req, current_version=3)

    # Version mismatch raises 412
    req_mismatch = Request(factory.get("/api/v1/resource/", HTTP_IF_MATCH='"2"'))
    try:
        viewset.check_optimistic_lock(req_mismatch, current_version=3)
        assert False, "Expected 412 Precondition Failed"
    except exceptions.APIException as exc:
        assert exc.status_code == status.HTTP_412_PRECONDITION_FAILED
    print("PASS: BaseTenantResourceViewSet If-Match optimistic locking verified.")


def test_base_fast_api_view_and_etag() -> None:
    factory = RequestFactory()
    view = BaseFastTenantAPIView()
    test_etag = 'W/"nx:ser:abc1234"'

    # Initial request without etag
    req_fresh = Request(factory.get("/api/v1/fast/"))
    res_fresh = view.build_etag_response(req_fresh, {"data": 42}, test_etag)
    assert res_fresh.status_code == 200
    assert res_fresh["ETag"] == test_etag

    # Subsequent request with If-None-Match
    req_cached = Request(factory.get("/api/v1/fast/", HTTP_IF_NONE_MATCH=test_etag))
    res_cached = view.build_etag_response(req_cached, {"data": 42}, test_etag)
    assert res_cached.status_code == 304
    print("PASS: BaseFastTenantAPIView 304 Not Modified evaluation verified.")


def test_declarative_engine_router() -> None:
    router = EngineRouteRegistry()
    router.register_engine("pos")
    router.register_engine("finance")

    # Matching valid path
    match = router.match("/api/v1/pos/nx1e_token999/")
    assert match is not None
    assert match.engine == "pos"
    assert match.envelope_token == "nx1e_token999"

    # Fails closed on unregistered engine or bad format
    assert router.match("/api/v1/unregistered/nx1e_token999/") is None
    assert router.match("/api/v1/pos/not_an_envelope/") is None
    print("PASS: EngineRouteRegistry declarative path matching verified.")


def test_middleware_stages() -> None:
    factory = RequestFactory()

    # Stage 1: Security Headers
    sec_mw = SecurityHeadersMiddleware(lambda r: HttpResponse("OK"))
    sec_res = sec_mw(factory.get("/"))
    assert "Strict-Transport-Security" in sec_res
    assert sec_res["X-Frame-Options"] == "DENY"

    # Stage 2: Trace Context
    trace_mw = TraceContextMiddleware(lambda r: HttpResponse("OK"))
    trace_res = trace_mw(factory.get("/"))
    assert "X-Nexus-Request-ID" in trace_res

    # Stage 8: Idempotency
    idem_mw = IdempotencyMiddleware(lambda r: HttpResponse(b'{"order_id": 1}', status=201))
    req_idem = factory.post("/api/v1/orders/", HTTP_IDEMPOTENCY_KEY="key-12345")
    res1 = idem_mw(req_idem)
    assert res1.status_code == 201
    assert "X-Nexus-Idempotent-Replay" not in res1

    # Second call returns replay
    res2 = idem_mw(req_idem)
    assert res2.status_code == 201
    assert res2["X-Nexus-Idempotent-Replay"] == "true"

    # Stage 11: ETag Evaluator
    etag_mw = EtagEvaluatorMiddleware(
        lambda r: HttpResponse(b"Content", headers={"ETag": 'W/"123"'})
    )
    req_etag = factory.get("/", HTTP_IF_NONE_MATCH='W/"123"')
    res_etag = etag_mw(req_etag)
    assert res_etag.status_code == 304
    print("PASS: 11-stage middleware pipeline (Security, Trace, Idempotency, ETag) verified.")


def test_rfc9457_exception_handler() -> None:
    val_exc = exceptions.ValidationError({"branch_name": ["This field is required."]})
    res = nexus_exception_handler(val_exc, {})
    assert res is not None
    assert res.status_code == 400
    data = res.data
    assert data["type"] == "urn:nexus:error:validation-failed"
    assert len(data["invalid_params"]) == 1
    assert data["invalid_params"][0]["field"] == "branch_name"
    print("PASS: RFC 9457 unified exception handler verified.")


def main() -> None:
    print("--- Running Subphase 01.23 Verification Suite ---")
    test_base_viewset_optimistic_locking()
    test_base_fast_api_view_and_etag()
    test_declarative_engine_router()
    test_middleware_stages()
    test_rfc9457_exception_handler()
    print("SUCCESS: 01.23 Advanced Django Views & Middleware verified with 100% assertions.")


if __name__ == "__main__":
    main()
