import React, { useMemo, useState } from 'react';
import { NexusButton, NexusNumberInput, NexusText } from '@nexus/ui';

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

  const handleCountChange = (val: number, newCount: number) => {
    setCounts((prev) => ({
      ...prev,
      [val]: isNaN(newCount) || newCount < 0 ? 0 : newCount,
    }));
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className="w-full max-w-lg rounded-xl border border-[var(--nx-border-default)] bg-[var(--nx-surface-card)] p-6 shadow-2xl">
        <div className="flex items-center justify-between border-b border-[var(--nx-border-subtle)] pb-4">
          <div>
            <NexusText variant="h3">Blind Close Denomination Counter</NexusText>
            <NexusText variant="caption" role="muted">Count physical notes and coins in cash drawer</NexusText>
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
                className="flex items-center justify-between rounded-lg bg-[var(--nx-surface-subtle)] px-3 py-2 gap-2"
              >
                <span className="w-32 text-sm font-medium text-[var(--nx-text-primary)]">{d.label}</span>
                <div style={{ width: '90px' }}>
                  <NexusNumberInput
                    min={0}
                    step={1}
                    value={count}
                    onChange={(v) => handleCountChange(d.value, v)}
                  />
                </div>
                <span className="w-24 text-right font-mono text-sm font-semibold text-[var(--nx-text-primary)]">
                  {currency} {subtotal}
                </span>
              </div>
            );
          })}
        </div>

        <div className="flex items-center justify-between rounded-lg border border-[var(--nx-border-default)] bg-[var(--nx-surface-subtle)] p-4">
          <NexusText variant="label" role="secondary">Total Counted:</NexusText>
          <NexusText variant="h2" tabular style={{ fontWeight: 700 }}>
            {currency} {totalCalculated}
          </NexusText>
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
