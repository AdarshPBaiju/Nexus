import React, { useState } from 'react';
import {
  NexusBadge,
  NexusButton,
  NexusDetailPageShell,
} from '@nexus/ui';
import { DenominationCounterModal } from './DenominationCounterModal';
import type { ShiftRegisterSessionDto } from './types';

export interface ShiftRegisterConsoleProps {
  readonly initialSession: ShiftRegisterSessionDto;
  readonly onOpenShift: (float: string) => Promise<void>;
  readonly onCloseShift: (actualCount: string) => Promise<void>;
  readonly onAddExpense: (amount: string, reason: string) => Promise<void>;
}

export const ShiftRegisterConsole: React.FC<ShiftRegisterConsoleProps> = ({
  initialSession,
  onCloseShift,
  onAddExpense,
}) => {
  const [session] = useState<ShiftRegisterSessionDto>(initialSession);
  const [isCounterOpen, setIsCounterOpen] = useState(false);
  const [expenseAmount, setExpenseAmount] = useState('');
  const [expenseReason, setExpenseReason] = useState('PETTY_CASH_SUPPLIES');

  const handleConfirmClose = async (total: string) => {
    setIsCounterOpen(false);
    await onCloseShift(total);
  };

  const handleExpenseSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!expenseAmount || parseFloat(expenseAmount) <= 0) return;
    await onAddExpense(expenseAmount, expenseReason);
    setExpenseAmount('');
  };

  const isOpen = session.status === 'OPEN';

  return (
    <NexusDetailPageShell
      title={`Shift Session: ${session.workstationId}`}
      subtitle={`Cashier ID: ${session.cashierUserId} • Opened: ${session.openedAt}`}
      headerActions={
        isOpen ? (
          <NexusButton variant="primary" onClick={() => setIsCounterOpen(true)}>
            Blind Close Shift
          </NexusButton>
        ) : (
          <NexusBadge variant="neutral">Shift Finalized</NexusBadge>
        )
      }
    >
      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        {/* Metric Cards */}
        <div className="rounded-xl border border-[var(--nx-border-default)] bg-[var(--nx-surface-card)] p-5">
          <div className="text-xs font-semibold text-[var(--nx-text-secondary)]">OPENING FLOAT</div>
          <div className="mt-2 font-mono text-2xl font-bold text-[var(--nx-text-primary)]">
            $ {session.openingFloat}
          </div>
        </div>

        <div className="rounded-xl border border-[var(--nx-border-default)] bg-[var(--nx-surface-card)] p-5">
          <div className="text-xs font-semibold text-[var(--nx-text-secondary)]">NET CASH INTAKE</div>
          <div className="mt-2 font-mono text-2xl font-bold text-[var(--nx-text-primary)]">
            $ {session.systemCashTotal}
          </div>
        </div>

        <div className="rounded-xl border border-[var(--nx-border-default)] bg-[var(--nx-surface-card)] p-5">
          <div className="text-xs font-semibold text-[var(--nx-text-secondary)]">SESSION STATUS</div>
          <div className="mt-2">
            <NexusBadge variant={isOpen ? 'success' : 'neutral'}>
              {session.status}
            </NexusBadge>
          </div>
        </div>
      </div>

      {/* Petty Cash Expense Section */}
      {isOpen && (
        <div className="mt-8 rounded-xl border border-[var(--nx-border-default)] bg-[var(--nx-surface-card)] p-6">
          <h3 className="text-base font-bold text-[var(--nx-text-primary)]">Quick Petty Cash Disbursement</h3>
          <p className="text-xs text-[var(--nx-text-secondary)]">Record emergency register withdrawal with immediate cash decrement</p>
          <form onSubmit={handleExpenseSubmit} className="mt-4 flex flex-wrap items-center gap-4">
            <input
              type="number"
              step="0.01"
              placeholder="Amount ($)"
              value={expenseAmount}
              onChange={(e) => setExpenseAmount(e.target.value)}
              className="w-36 rounded-lg border border-[var(--nx-border-default)] bg-[var(--nx-surface-subtle)] px-3 py-2 font-mono text-sm text-[var(--nx-text-primary)]"
            />
            <select
              value={expenseReason}
              onChange={(e) => setExpenseReason(e.target.value)}
              className="rounded-lg border border-[var(--nx-border-default)] bg-[var(--nx-surface-subtle)] px-3 py-2 text-sm text-[var(--nx-text-primary)]"
            >
              <option value="PETTY_CASH_SUPPLIES">Emergency Store Supplies</option>
              <option value="STAFF_MEAL">Staff Duty Meal</option>
              <option value="DELIVERY_FEE">Delivery Tip / Fee</option>
              <option value="EMERGENCY_REPAIR">Immediate Repair</option>
            </select>
            <NexusButton variant="secondary" type="submit">
              Disburse from Drawer
            </NexusButton>
          </form>
        </div>
      )}

      {/* Denomination Counter Modal */}
      <DenominationCounterModal
        isOpen={isCounterOpen}
        currency="$"
        onClose={() => setIsCounterOpen(false)}
        onConfirm={handleConfirmClose}
      />
    </NexusDetailPageShell>
  );
};
