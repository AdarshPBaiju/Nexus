"""
nexus.libs.http.routing.engine_router - Declarative zero-query-string route registry.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RouteMatch:
    engine: str
    envelope_token: str
    remainder: str = ""


class EngineRouteRegistry:
    """
    Maps declarative engine endpoints to canonical encrypted path patterns:
    /api/v1/{engine}/nx1_<envelope>/
    """

    ROUTE_PATTERN = re.compile(
        r"^/api/v1/(?P<engine>[a-zA-Z0-9_-]+)/(?P<token>nx1[a-z]_[A-Za-z0-9_-]+)(?:/(?P<remainder>.*))?$"
    )

    def __init__(self) -> None:
        self._registered_engines: set[str] = set()

    def register_engine(self, engine_name: str) -> None:
        """Register an engine domain as valid for declarative encrypted routing."""
        self._registered_engines.add(engine_name)

    def match(self, path: str) -> Optional[RouteMatch]:
        """Match an incoming URL path against registered declarative routes."""
        m = self.ROUTE_PATTERN.match(path)
        if not m:
            return None
        engine = m.group("engine")
        if engine not in self._registered_engines:
            return None
        token = m.group("token")
        remainder = m.group("remainder") or ""
        return RouteMatch(engine=engine, envelope_token=token, remainder=remainder)

    def format_url(self, engine: str, envelope_token: str) -> str:
        """Format canonical encrypted endpoint URL."""
        return f"/api/v1/{engine}/{envelope_token}/"
