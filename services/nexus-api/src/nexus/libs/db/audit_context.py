"""
nexus.libs.db.audit_context - Request audit context propagation.
"""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class AuditRequestContext:
    """Immutable audit request context for PgBouncer GUC propagation."""

    tenant_id: UUID
    actor_id: UUID
    actor_type: str = "STAFF"
    device_id: Optional[UUID] = None
    request_id: Optional[str] = None
    trace_id: Optional[str] = None
    surface: str = "WEB_ALL"
    client_ip: Optional[str] = None
    reason: Optional[str] = None
    supervisor_id: Optional[UUID] = None


_audit_ctx_var: ContextVar[Optional[AuditRequestContext]] = ContextVar(
    "nexus_audit_context", default=None
)


def set_current_audit_context(ctx: AuditRequestContext) -> None:
    """Set the active audit context for the current task/thread."""
    _audit_ctx_var.set(ctx)


def get_current_audit_context() -> Optional[AuditRequestContext]:
    """Retrieve the active audit context if present."""
    return _audit_ctx_var.get()


def clear_current_audit_context() -> None:
    """Clear active audit context."""
    _audit_ctx_var.set(None)
