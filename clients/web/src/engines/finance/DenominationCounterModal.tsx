import React, { useMemo, useState } from 'react';
import { NexusButton } from '@nexus/ui';
import type { DenominationItem } from './types';

export interface DenominationCounterModalProps {
  readonly isOpen: boolean;
  readonly currency: string;
  readonly onClose: () => void;
  readonly onConfirm: (total: string) => void;
}

const DEFAULT_DENOMINATIONS: readonly { value: number; label: string }[] = [
  { value: 100, label: '$100 Bill' },
  { value: 50, label: '$50 Bill' },
  { value: 20, label: '$20 Bill' },
  { value: 10, label: '$10 Bill' },
  { value: 5, label: '$5 Bill' },
  { value: 2, label: '$2 Bill' },
  { value: 1, label: '$1 Bill / Coin' },
  { value: 0.25, label: '25¢ Quarter' },
  { value: 0.1, label: '10¢ Dime' },
  { value: 0.05, label: '5¢ Nickel' },
  { value: 0.01, label: '1¢ Penny' },
];

export const DenominationCounterModal: React.FC<DenominationCounterModalProps> = ({
  isOpen,
  currency,
  onClose,
  onConfirm,
}) => {
  const [counts, setCounts] = useState<Record<number, number>>({});

  const totalCalculated = useMemo(() => {
    let sum = 0;
    for (const d of DEFAULT_DENOMINATIONS) {
      const c = counts[d.value] ?? 0;
      sum += d.value * c;
    }
    return sum.toFixed(2);
  }, [counts]);

  if (!isOpen) return null;

  const handleCountChange = (val: number, countStr: string) => {
    const parsed = parseInt(countStr, 10);
    setCounts((prev) => ({
      ...prev,
      [val]: isNaN(parsed) || parsed < 0 ? 0 : parsed,
    }));
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className="w-full max-w-lg rounded-xl border border-[var(--nx-border-default)] bg-[var(--nx-surface-card)] p-6 shadow-2xl">
        <div className="flex items-center justify-between border-b border-[var(--nx-border-subtle)] pb-4">
          <div>
            <h2 className="text-lg font-bold text-[var(--nx-text-primary)]">Blind Close Denomination Counter</h2>
            <p className="text-xs text-[var(--nx-text-secondary)]">Count physical notes and coins in cash drawer</p>
          </div>
          <button
            onClick={onClose}
            className="text-[var(--nx-text-muted)] hover:text-[var(--nx-text-primary)]"
            type="button"
          >
            ✕
          </button>
        </div>

        <div className="my-4 max-h-72 space-y-2 overflow-y-auto pr-2">
          {DEFAULT_DENOMINATIONS.map((d) => {
            const count = counts[d.value] ?? 0;
            const subtotal = (d.value * count).toFixed(2);
            return (
              <div
                key={d.value}
                className="flex items-center justify-between rounded-lg bg-[var(--nx-surface-subtle)] px-3 py-2"
              >
                <span className="w-32 text-sm font-medium text-[var(--nx-text-primary)]">{d.label}</span>
                <input
                  type="number"
                  min="0"
                  value={count === 0 ? '' : count}
                  placeholder="0"
                  onChange={(e) => handleCountChange(d.value, e.target.value)}
                  className="w-20 rounded border border-[var(--nx-border-default)] bg-[var(--nx-surface-card)] px-2 py-1 text-center font-mono text-sm text-[var(--nx-text-primary)]"
                />
                <span className="w-24 text-right font-mono text-sm font-semibold text-[var(--nx-text-primary)]">
                  {currency} {subtotal}
                </span>
              </div>
            );
          })}
        </div>

        <div className="flex items-center justify-between rounded-lg border border-[var(--nx-border-default)] bg-[var(--nx-surface-subtle)] p-4">
          <span className="text-sm font-medium text-[var(--nx-text-secondary)]">Total Counted:</span>
          <span className="font-mono text-xl font-bold text-[var(--nx-text-primary)]">
            {currency} {totalCalculated}
          </span>
        </div>

        <div className="mt-6 flex justify-end gap-3">
          <NexusButton variant="secondary" onClick={onClose}>
            Cancel
          </NexusButton>
          <NexusButton variant="primary" onClick={() => onConfirm(totalCalculated)}>
            Confirm Physical Count
          </NexusButton>
        </div>
      </div>
    </div>
  );
};
