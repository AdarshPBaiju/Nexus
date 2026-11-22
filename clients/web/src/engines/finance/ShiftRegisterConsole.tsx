import React, { useState } from 'react';
import {
  NexusBadge,
  NexusButton,
  NexusDetailPageShell,
  NexusNumberInput,
  NexusSelect,
  NexusText,
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
          <NexusText variant="h3">Quick Petty Cash Disbursement</NexusText>
          <NexusText variant="caption" role="muted">Record emergency register withdrawal with immediate cash decrement</NexusText>
          <form onSubmit={handleExpenseSubmit} className="mt-4 flex flex-wrap items-center gap-4">
            <div style={{ width: '140px' }}>
              <NexusNumberInput
                step={0.5}
                min={0}
                value={parseFloat(expenseAmount) || 0}
                onChange={(v) => setExpenseAmount(v.toString())}
              />
            </div>
            <div style={{ width: '220px' }}>
              <NexusSelect
                value={expenseReason}
                onChange={setExpenseReason}
                options={[
                  { value: 'PETTY_CASH_SUPPLIES', label: 'Emergency Store Supplies' },
                  { value: 'STAFF_MEAL', label: 'Staff Duty Meal' },
                  { value: 'DELIVERY_FEE', label: 'Delivery Tip / Fee' },
                  { value: 'EMERGENCY_REPAIR', label: 'Immediate Repair' },
                ]}
              />
            </div>
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
