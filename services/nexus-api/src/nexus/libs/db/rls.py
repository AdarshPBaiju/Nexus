"""
nexus.libs.db.rls - PostgreSQL 16 Forced Row-Level Security (RLS) infrastructure.
"""

from __future__ import annotations

import uuid
from contextlib import contextmanager
from typing import Generator, Optional

from django.db import connection, transaction

from nexus.libs.db.audit_context import AuditRequestContext, get_current_audit_context


def _apply_audit_gucs(cursor, audit_ctx: AuditRequestContext) -> None:
    """Set transaction-local audit context GUCs inside PgBouncer session."""
    guc_params: list[tuple[str, str]] = [
        ("app.current_actor_id", str(audit_ctx.actor_id)),
        ("app.current_actor_type", audit_ctx.actor_type),
        ("app.current_surface", audit_ctx.surface),
    ]
    if audit_ctx.device_id:
        guc_params.append(("app.current_device_id", str(audit_ctx.device_id)))
    if audit_ctx.request_id:
        guc_params.append(("app.current_request_id", audit_ctx.request_id))
    if audit_ctx.trace_id:
        guc_params.append(("app.current_trace_id", audit_ctx.trace_id))
    if audit_ctx.client_ip:
        guc_params.append(("app.current_client_ip", audit_ctx.client_ip))
    if audit_ctx.reason:
        guc_params.append(("app.current_audit_reason", audit_ctx.reason))

    for param_name, param_val in guc_params:
        cursor.execute(
            f"SELECT set_config('{param_name}', %s, true)",
            [param_val],
        )


@contextmanager
def tenant_transaction(
    tenant_id: uuid.UUID | str,
    audit_ctx: Optional[AuditRequestContext] = None,
) -> Generator[None, None, None]:
    """
    Execute database operations within an isolated tenant session context.
    Sets LOCAL app.current_tenant_id and audit GUCs inside atomic transaction.
    """
    tid_str = str(tenant_id)
    uuid.UUID(tid_str)  # Validates UUID format

    active_audit = audit_ctx or get_current_audit_context()

    with transaction.atomic():
        with connection.cursor() as cursor:
            if connection.vendor == "postgresql":
                cursor.execute(
                    "SELECT set_config('app.current_tenant_id', %s, true)",
                    [tid_str],
                )
                if active_audit:
                    _apply_audit_gucs(cursor, active_audit)
        yield


def generate_forced_rls_sql(table_name: str) -> list[str]:
    """Generate PostgreSQL 16 DDL statements to enable and force RLS on a table."""
    policy_name = f"{table_name}_tenant_isolation_policy"
    return [
        f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;",
        f"ALTER TABLE {table_name} FORCE ROW LEVEL SECURITY;",
        f"DROP POLICY IF EXISTS {policy_name} ON {table_name};",
        (
            f"CREATE POLICY {policy_name} ON {table_name} "
            f"FOR ALL "
            f"USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid) "
            f"WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid);"
        ),
    ]


def generate_drop_rls_sql(table_name: str) -> list[str]:
    """Generate DDL statements to drop RLS policy from a table."""
    policy_name = f"{table_name}_tenant_isolation_policy"
    return [
        f"DROP POLICY IF EXISTS {policy_name} ON {table_name};",
        f"ALTER TABLE {table_name} NO FORCE ROW LEVEL SECURITY;",
        f"ALTER TABLE {table_name} DISABLE ROW LEVEL SECURITY;",
    ]
