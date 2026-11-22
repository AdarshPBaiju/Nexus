"""
nexus.libs.db.rls - PostgreSQL 16 Forced Row-Level Security (RLS) infrastructure.
"""

from __future__ import annotations

import uuid
from contextlib import contextmanager
from typing import Generator

from django.db import connection, transaction


@contextmanager
def tenant_transaction(tenant_id: uuid.UUID | str) -> Generator[None, None, None]:
    """
    Execute database operations within an isolated tenant session context.
    Sets LOCAL app.current_tenant_id inside an atomic transaction block.
    """
    tid_str = str(tenant_id)
    # Validate UUID format fails closed
    uuid.UUID(tid_str)

    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT set_config('app.current_tenant_id', %s, true)",
                [tid_str],
            )
        yield


def generate_forced_rls_sql(table_name: str) -> list[str]:
    """
    Generate PostgreSQL 16 DDL statements to enable and force RLS on a table.
    """
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
    """
    Generate DDL statements to drop RLS policy from a table (for rollbacks).
    """
    policy_name = f"{table_name}_tenant_isolation_policy"
    return [
        f"DROP POLICY IF EXISTS {policy_name} ON {table_name};",
        f"ALTER TABLE {table_name} NO FORCE ROW LEVEL SECURITY;",
        f"ALTER TABLE {table_name} DISABLE ROW LEVEL SECURITY;",
    ]
