"""
nexus.engines.payment_router.application.clearing_generator - Double-Entry Clearing Generator.
"""
from __future__ import annotations

from decimal import Decimal

from nexus.engines.payment_router.application.dtos import ClearingPosting


class ClearingJournalGenerator:
    """
    Computes zero-variance balanced double-entry clearing postings for captures and settlements.
    Invariant: sum(Debit) == sum(Credit) exactly.
    """

    @classmethod
    def generate_capture_postings(cls, amount: Decimal) -> list[ClearingPosting]:
        """
        On successful capture:
        Debit:  Gateway Clearing Asset (Funds in transit from processor)
        Credit: Accounts Receivable    (Settlement of customer folio balance)
        """
        amt = Decimal(str(amount))
        return [
            ClearingPosting(
                account_name="Gateway Clearing Asset",
                direction="DEBIT",
                amount=amt,
                description="Payment captured - pending processor settlement",
            ),
            ClearingPosting(
                account_name="Accounts Receivable",
                direction="CREDIT",
                amount=amt,
                description="Customer folio balance cleared by payment capture",
            ),
        ]

    @classmethod
    def generate_settlement_postings(
        cls,
        gross: Decimal,
        fee: Decimal,
        net: Decimal,
    ) -> list[ClearingPosting]:
        """
        On processor T+1 settlement deposit into merchant operating bank account:
        Debit:  Operating Bank Account   (Net funds deposited)
        Debit:  MDR Processing Expense   (Gateway processing fee)
        Credit: Gateway Clearing Asset   (Gross transit balance cleared)
        """
        d_gross = Decimal(str(gross))
        d_fee = Decimal(str(fee))
        d_net = Decimal(str(net))

        if (d_net + d_fee) != d_gross:
            raise ValueError(f"Settlement invariant violated: net ({d_net}) + fee ({d_fee}) != gross ({d_gross})")

        return [
            ClearingPosting(
                account_name="Operating Bank Account",
                direction="DEBIT",
                amount=d_net,
                description="Gateway settlement net payout deposited",
            ),
            ClearingPosting(
                account_name="MDR Processing Expense",
                direction="DEBIT",
                amount=d_fee,
                description="Merchant processing fee deducted by gateway",
            ),
            ClearingPosting(
                account_name="Gateway Clearing Asset",
                direction="CREDIT",
                amount=d_gross,
                description="Processor transit balance fully settled",
            ),
        ]
