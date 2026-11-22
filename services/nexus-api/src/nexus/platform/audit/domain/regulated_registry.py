"""
nexus.platform.audit.domain.regulated_registry - Registry of monitored tables for CDC.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RegulatedTableConfig:
    table_name: str
    entity_label: str
    scrub_columns: tuple[str, ...] = ()


REGULATED_TABLES: tuple[RegulatedTableConfig, ...] = (
    RegulatedTableConfig(
        table_name="iam_role",
        entity_label="Role",
    ),
    RegulatedTableConfig(
        table_name="iam_staff_profile",
        entity_label="StaffProfile",
        scrub_columns=("cashier_pin_hash",),
    ),
    RegulatedTableConfig(
        table_name="fin_ledger_account",
        entity_label="LedgerAccount",
    ),
    RegulatedTableConfig(
        table_name="fin_journal_entry",
        entity_label="JournalEntry",
    ),
    RegulatedTableConfig(
        table_name="pay_channel_credential",
        entity_label="PaymentCredential",
        scrub_columns=("encrypted_payload",),
    ),
    RegulatedTableConfig(
        table_name="inv_invoice_document",
        entity_label="InvoiceDocument",
    ),
)


def get_regulated_table(table_name: str) -> RegulatedTableConfig | None:
    for item in REGULATED_TABLES:
        if item.table_name == table_name:
            return item
    return None
