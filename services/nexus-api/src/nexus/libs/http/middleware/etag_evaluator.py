"""
nexus.libs.http.middleware.etag_evaluator - Stage 11 Weak ETag Evaluator.
"""

from __future__ import annotations

from typing import Callable

from django.http import HttpRequest, HttpResponse


class EtagEvaluatorMiddleware:
    """Stage 11: Evaluates If-None-Match headers and returns 304 Not Modified."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        if request.method != "GET" or response.status_code != 200:
            return response

        etag = response.get("ETag")
        if_none_match = request.headers.get("If-None-Match")
        if etag and if_none_match:
            clean_inm = if_none_match.strip().strip('"')
            clean_etag = etag.strip().strip('"')
            if clean_inm == clean_etag or if_none_match.strip() == etag.strip():
                not_modified = HttpResponse(status=304)
                not_modified["ETag"] = etag
                return not_modified

        return response
